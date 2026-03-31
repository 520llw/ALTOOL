# -*- coding: utf-8 -*-
"""
尚阳通 PDF 提取精度测试脚本
使用 shanyangtong_ground_truth.json 作为标准答案
"""

import os
import sys
import re
import time
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import config
from backend.db_manager import DatabaseManager
from backend.pdf_parser import PDFParser
from backend.ai_processor import AIProcessor

def extract_number(value_str: str) -> float:
    """从参数值字符串中提取数字部分"""
    if not value_str or not isinstance(value_str, str):
        return None
    value_str = value_str.strip()
    # 匹配数字（含负号、小数点）
    m = re.search(r'[-+]?\d*\.?\d+', value_str)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None

def values_match(gt_value: str, extracted_value: str, param_name: str) -> bool:
    """
    判断提取值是否与标准答案匹配
    1. 文本类：语义等价匹配
    2. 数值类：提取数字比较，允许 5% 误差
    3. 测试条件类：只要数字部分匹配 80% 以上即可
    """
    if not gt_value or not extracted_value:
        return False
    
    gt_value = str(gt_value).strip()
    extracted_value = str(extracted_value).strip()
    
    # 1. 如果是测试条件类参数，采用宽松匹配
    if '测试条件' in param_name or '限制条件' in param_name:
        gt_nums = re.findall(r'\d+\.?\d*', gt_value)
        ext_nums = re.findall(r'\d+\.?\d*', extracted_value)
        if not gt_nums: return True # 如果标准答案没写条件，不扣分
        
        # 计算交集
        matches = 0
        for gn in gt_nums:
            g_val = float(gn)
            for en in ext_nums:
                try:
                    e_val = float(en)
                    # 处理分母为0的情况
                    if g_val == 0:
                        if e_val == 0: matches += 1; break
                    elif abs(g_val - e_val) / abs(g_val) < 0.05:
                        matches += 1; break
                except: continue
        return matches >= len(gt_nums) * 0.8

    # 2. 语义等价库
    semantic_equivalence = {
        '安装': {
            'THT': ['through hole', '插件', 'tht', 'th'],
            'SMD': ['surface mount', '贴片', 'smd', 'toll', 'dfn', 'qfn', 'sot']
        },
        '认证': {
            'Green/RoHS': ['non-automotive qualified', 'pb-free', 'lead-free', 'rohs', 'green', '符合rohs', 'halogen-free']
        }
    }
    
    # 3. 文本类基础匹配
    text_params = {'厂家', 'OPN', '封装', '厂家封装名', '极性', '技术', '特殊功能', '认证',
                   '安装', 'PDF文件名'}
                   
    if param_name in text_params:
        gt_lower = gt_value.lower().replace(' ', '').replace('-', '').replace('_', '')
        ext_lower = extracted_value.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        if gt_lower in ext_lower or ext_lower in gt_lower:
            return True
            
        if param_name in semantic_equivalence:
            for std, synonyms in semantic_equivalence[param_name].items():
                is_ext_in_group = any(s in ext_lower for s in synonyms) or ext_lower == std.lower()
                is_gt_in_group = any(s in gt_lower for s in synonyms) or gt_lower == std.lower()
                if is_ext_in_group and is_gt_in_group:
                    return True
        return False
    
    # 4. 数值类参数
    gt_num = extract_number(gt_value)
    ext_num = extract_number(extracted_value)
    
    if gt_num is None or ext_num is None:
        return gt_value.lower().replace(' ', '') == extracted_value.lower().replace(' ', '')
    
    if gt_num == 0:
        return ext_num == 0
    
    # 允许 5% 误差
    tolerance = 0.05
    return abs(gt_num - ext_num) / abs(gt_num) <= tolerance
    
    # 数值类参数
    gt_num = extract_number(gt_value)
    ext_num = extract_number(extracted_value)
    
    if gt_num is None or ext_num is None:
        return gt_value.replace(' ', '') == extracted_value.replace(' ', '')
    
    if gt_num == 0:
        return ext_num == 0
    
    # 允许 5% 误差
    tolerance = 0.05
    return abs(gt_num - ext_num) / abs(gt_num) <= tolerance

def run_test():
    # 加载标准答案
    gt_path = Path(__file__).parent / "shanyangtong_ground_truth.json"
    with open(gt_path, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
    
    print("=" * 80)
    print(f"🚀 开始测试: 尚阳通 PDF 提取精度")
    print(f"模型: {config.ai.model} | 文件数: {len(ground_truth)}")
    print("=" * 80)
    
    pdf_parser = PDFParser()
    ai_processor = AIProcessor()
    db_manager = DatabaseManager()
    
    # 获取参数库
    params_info = db_manager.get_all_params_with_variants()
    
    all_results = {}
    total_tp = 0
    total_extracted = 0
    total_gt = 0
    
    pdf_dir = Path(__file__).parent / "尚阳通规格书"
    
    for pdf_name, gt in ground_truth.items():
        # 优化文件名查找：忽略所有空格和特殊字符
        def normalize_name(n):
            return re.sub(r'[^a-zA-Z0-9]', '', n).lower()
            
        target_norm = normalize_name(pdf_name)
        pdf_path = None
        for p in pdf_dir.glob("*.pdf"):
            if target_norm in normalize_name(p.name) or normalize_name(p.name) in target_norm:
                pdf_path = p
                break
        
        if not pdf_path:
            print(f"❌ 找不到文件: {pdf_name}")
            continue
        
        print(f"\n📄 正在提取: {pdf_path.name}")
        
        # 解析 PDF
        try:
            pdf_content = pdf_parser.parse_pdf(str(pdf_path))
        except Exception as e:
            print(f"   解析失败: {e}")
            continue
            
        # AI 提取
        start_time = time.time()
        result = ai_processor.extract_params(pdf_content, params_info, parallel=True)
        elapsed = time.time() - start_time
        
        if result.error:
            print(f"   提取错误: {result.error}")
            continue
            
        # 构建提取结果映射
        extracted_map = {p.standard_name: p.value for p in result.params}
        
        # 匹配统计
        tp = 0
        wrong_list = []
        fn_list = [] # 漏提
        
        for gt_name, gt_value in gt.items():
            total_gt += 1
            if gt_name in extracted_map:
                if values_match(gt_value, extracted_map[gt_name], gt_name):
                    tp += 1
                else:
                    wrong_list.append((gt_name, gt_value, extracted_map[gt_name]))
            else:
                fn_list.append(gt_name)
        
        n_extracted = len(extracted_map)
        total_extracted += n_extracted
        total_tp += tp
        
        p = (tp / n_extracted * 100) if n_extracted > 0 else 0
        r = (tp / len(gt) * 100) if len(gt) > 0 else 0
        
        print(f"   提取完成: {n_extracted} 参数 | 耗时 {elapsed:.1f}s")
        print(f"   正确(TP): {tp}/{len(gt)} | 漏提(FN): {len(fn_list)} | 错值: {len(wrong_list)}")
        print(f"   Precision: {p:.1f}% | Recall: {r:.1f}%")
        
        if wrong_list:
            print("   ⚠️ 错值项:")
            for name, gtv, extv in wrong_list[:5]: # 只显示前5个
                print(f"     - {name}: 标准={gtv}, 提取={extv}")
            if len(wrong_list) > 5: print(f"     ...等 {len(wrong_list)} 项")

    # 汇总
    print("\n" + "=" * 80)
    print("📊 最终汇总结果")
    print("=" * 80)
    overall_p = (total_tp / total_extracted * 100) if total_extracted > 0 else 0
    overall_r = (total_tp / total_gt * 100) if total_gt > 0 else 0
    overall_f1 = (2 * overall_p * overall_r / (overall_p + overall_r)) if (overall_p + overall_r) > 0 else 0
    
    print(f"总标准参数数: {total_gt}")
    print(f"总提取参数数: {total_extracted}")
    print(f"总正确参数数: {total_tp}")
    print(f"综合 Precision: {overall_p:.1f}%")
    print(f"综合 Recall:    {overall_r:.1f}%")
    print(f"综合 F1-Score:  {overall_f1:.1f}%")
    print("=" * 80)

if __name__ == '__main__':
    run_test()
