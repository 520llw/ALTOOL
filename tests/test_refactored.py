# -*- coding: utf-8 -*-
"""测试重构后的提取效果（含名称归一化验证）"""
import sys
import re
import json
import time
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.pdf_parser import PDFParser
from backend.ai_processor import AIProcessor


def build_gt_normalizer(device_type: str) -> dict:
    """
    构建 GT名称 → 配置标准名 的映射表
    解决 GT 使用 MOSFET 名称而配置使用 IGBT 名称的问题
    """
    ai = AIProcessor()
    normalizer = ai._build_name_normalizer(device_type)
    return normalizer


def normalize_gt_name(gt_name: str, ai_proc: AIProcessor, device_type: str,
                      normalizer: dict) -> str:
    """将 GT 的参数名映射到配置标准名"""
    return ai_proc._normalize_param_name(gt_name, normalizer)


def values_match(ai_val: str, gt_val: str) -> bool:
    """智能值匹配"""
    if not ai_val or not gt_val:
        return False
    # 清洗
    e_clean = re.sub(r'[^0-9a-zA-Z.\-+]', '', str(ai_val).lower())
    g_clean = re.sub(r'[^0-9a-zA-Z.\-+]', '', str(gt_val).lower())
    # 精确或包含
    if e_clean == g_clean:
        return True
    if e_clean and g_clean:
        if e_clean in g_clean or g_clean in e_clean:
            return True
    # 数值比较（容忍5%误差）
    try:
        e_num = float(re.search(r'[-+]?[\d.]+', str(ai_val)).group())
        g_num = float(re.search(r'[-+]?[\d.]+', str(gt_val)).group())
        if g_num == 0:
            return e_num == 0
        if abs(e_num - g_num) / abs(g_num) < 0.05:
            return True
    except (AttributeError, ValueError, ZeroDivisionError):
        pass
    return False


def test_new_extraction():
    parser = PDFParser()
    ai = AIProcessor()
    ai.timeout = 180

    # 加载标准答案
    with open("shanyangtong_ground_truth.json", "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    pdf_name = "Sanrise-SRE50N120FSUS7(1).pdf"
    gt = gt_data[pdf_name]
    pdf_path = f"/home/gjw/AITOOL/尚阳通规格书/{pdf_name}"

    print("=" * 80, flush=True)
    print(f"测试重构后提取效果（含名称归一化）", flush=True)
    print(f"文件: {pdf_name}", flush=True)
    print(f"GT参数: {len(gt)} 项", flush=True)
    print("=" * 80, flush=True)

    # 解析 PDF
    print("\n1. 解析 PDF...", flush=True)
    pdf_content = parser.parse_pdf(pdf_path)
    print(f"   页数: {pdf_content.page_count}, 表格: {len(pdf_content.tables)}, 文本段: {len(pdf_content.texts)}", flush=True)
    device_type = pdf_content.metadata.get('device_type', 'Si MOSFET')
    print(f"   器件类型: {device_type}", flush=True)

    # 显示分组信息
    groups = ai._get_param_groups(device_type)
    total_params = sum(len(p) for p in groups.values())
    print(f"\n2. 参数分组 [{device_type}]: {len(groups)} 组, 共 {total_params} 参数", flush=True)
    for name, params in groups.items():
        print(f"   {name}: {len(params)} 参数", flush=True)

    # 提取
    print(f"\n3. 开始并行提取...", flush=True)
    start = time.time()
    result = ai.extract_params(pdf_content, [])
    elapsed = time.time() - start

    if result.error:
        print(f"   错误: {result.error}", flush=True)
        return

    print(f"   完成! 耗时 {elapsed:.1f}s, 提取 {len(result.params)} 个参数", flush=True)

    # 构建名称归一化器（也用于 GT 名称）
    normalizer = ai._build_name_normalizer(device_type)

    # 获取配置中所有标准参数名
    config_std_names = set()
    for group_params in groups.values():
        for p in group_params:
            config_std_names.add(p['name'])

    # AI 提取结果
    extracted = {p.standard_name: p.value for p in result.params}

    # 对比 GT（GT 名称也要归一化）
    print(f"\n4. 与标准答案对比:", flush=True)

    correct = 0
    wrong = []
    missed = []
    gt_name_mapping = {}  # gt_name → normalized_name

    for gt_name, gt_val in gt.items():
        # 将 GT 名称也通过归一化器映射
        norm_name = ai._normalize_param_name(gt_name, normalizer)
        gt_name_mapping[gt_name] = norm_name

        if norm_name in extracted:
            e_val = extracted[norm_name]
            if values_match(e_val, gt_val):
                correct += 1
            else:
                wrong.append((gt_name, norm_name, e_val, gt_val))
        elif gt_name in extracted:
            # 直接用 GT 原名匹配
            e_val = extracted[gt_name]
            if values_match(e_val, gt_val):
                correct += 1
            else:
                wrong.append((gt_name, gt_name, e_val, gt_val))
        else:
            missed.append((gt_name, norm_name))

    total_in_table = correct + len(wrong)
    accuracy = (correct / total_in_table * 100) if total_in_table > 0 else 0
    recall = (total_in_table / len(gt) * 100)

    print(f"\n   ✅ 正确: {correct}", flush=True)
    print(f"   ❌ 错误: {len(wrong)}", flush=True)
    print(f"   ⬜ 未提取: {len(missed)}", flush=True)
    print(f"   📊 表格准确率: {accuracy:.1f}%", flush=True)
    print(f"   📊 召回率: {recall:.1f}%", flush=True)

    if wrong:
        print(f"\n   【错误详情】", flush=True)
        for gt_name, used_name, ai_val, gt_val in wrong:
            label = f"{gt_name}" if gt_name == used_name else f"{gt_name}→{used_name}"
            print(f"      {label}: AI=\"{ai_val}\" vs GT=\"{gt_val}\"", flush=True)

    if missed:
        print(f"\n   【未提取】", flush=True)
        for gt_name, norm_name in missed:
            in_config = "✓配置有" if norm_name in config_std_names else "✗配置无"
            mapped = f"→{norm_name}" if norm_name != gt_name else ""
            print(f"      {gt_name}{mapped} [{in_config}]", flush=True)

    # 显示 AI 提出但 GT 没有的（额外提取）
    gt_normalized = set(gt_name_mapping.values()) | set(gt.keys())
    extra = [name for name in extracted if name not in gt_normalized]
    if extra:
        print(f"\n   【额外提取（不在GT中）】{', '.join(extra[:15])}", flush=True)

    # 名称归一化日志
    print(f"\n5. 名称映射详情:", flush=True)
    print(f"   GT名→配置名（有变化的）:", flush=True)
    for gt_name, norm_name in gt_name_mapping.items():
        if gt_name != norm_name:
            print(f"      {gt_name} → {norm_name}", flush=True)


if __name__ == "__main__":
    test_new_extraction()
