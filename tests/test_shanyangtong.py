# -*- coding: utf-8 -*-
"""
尚阳通PDF参数提取测试
测试前5个PDF文件的参数提取效果
"""

import os
import sys
import time
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import config
from backend.db_manager import DatabaseManager
from backend.pdf_parser import PDFParser
from backend.ai_processor import AIProcessor

def run_test():
    """运行尚阳通PDF提取测试"""
    print("=" * 100)
    print("  尚阳通规格书参数提取测试")
    print(f"  模型: {config.ai.model} | Provider: {config.ai.provider}")
    print("=" * 100)
    
    pdf_parser = PDFParser()
    ai_processor = AIProcessor()
    db_manager = DatabaseManager()
    
    # 获取参数库
    params_info = db_manager.get_all_params_with_variants()
    print(f"\n参数库: {len(params_info)} 个标准参数")
    
    # 要测试的PDF文件
    pdf_dir = Path(__file__).parent / "尚阳通规格书"
    pdf_files = [
        "Sanrise-SRE50N120FSUS7(1).pdf",
        "SRC30R018BTLTR-G preliminary Datasheet V0.1 .pdf",
        "SRC60R017FBDatasheetV1.pdf",
        "SRC60R017FBS Datasheet V1.1.pdf",
        "SRC60R020BS   DatasheetV1.0(1).pdf"
    ]
    
    # 汇总统计
    all_results = []
    total_time = 0
    total_params = 0
    
    for idx, pdf_name in enumerate(pdf_files, 1):
        pdf_path = pdf_dir / pdf_name
        
        if not pdf_path.exists():
            print(f"\n⚠ 文件不存在: {pdf_name}，跳过")
            continue
        
        print(f"\n{'=' * 100}")
        print(f"📄 [{idx}/{len(pdf_files)}] 正在提取: {pdf_name}")
        print(f"{'=' * 100}")
        
        # 解析PDF
        try:
            print(f"   📖 解析PDF...")
            parse_start = time.time()
            pdf_content = pdf_parser.parse_pdf(str(pdf_path))
            parse_time = time.time() - parse_start
            print(f"   ✅ PDF解析完成: 耗时 {parse_time:.2f}s")
        except Exception as e:
            print(f"   ❌ PDF解析失败: {e}")
            continue
        
        # AI提取
        print(f"   🤖 AI参数提取中...")
        extract_start = time.time()
        try:
            result = ai_processor.extract_params(pdf_content, params_info, parallel=True)
            extract_time = time.time() - extract_start
        except Exception as e:
            print(f"   ❌ AI提取失败: {e}")
            continue
        
        if result.error:
            print(f"   ❌ 提取错误: {result.error}")
            continue
        
        total_elapsed = time.time() - parse_start
        
        print(f"   ✅ 提取完成: {len(result.params)} 个参数")
        print(f"   ⏱️  耗时: 解析 {parse_time:.1f}s + 提取 {extract_time:.1f}s = 总计 {total_elapsed:.1f}s")
        
        # 展示提取的参数
        print(f"\n   📊 提取的参数详情:")
        print(f"   {'─' * 96}")
        print(f"   {'参数名':<30} {'值':<35} {'测试条件':<30}")
        print(f"   {'─' * 96}")
        
        # 分类显示
        basic_params = []
        voltage_params = []
        current_params = []
        resistance_params = []
        capacitance_params = []
        charge_params = []
        time_params = []
        thermal_params = []
        other_params = []
        
        for p in result.params:
            if p.standard_name in ['PDF文件名', '厂家', 'OPN', '封装', '厂家封装名', '极性', '技术', 
                                   '特殊功能', '认证', '安装', 'Product Status']:
                basic_params.append(p)
            elif 'V' in p.standard_name or '电压' in p.standard_name:
                voltage_params.append(p)
            elif 'I' in p.standard_name or '电流' in p.standard_name or 'gfs' in p.standard_name:
                current_params.append(p)
            elif 'R' in p.standard_name or '电阻' in p.standard_name or 'Rth' in p.standard_name:
                resistance_params.append(p)
            elif 'C' in p.standard_name or '电容' in p.standard_name:
                capacitance_params.append(p)
            elif 'Q' in p.standard_name or '电荷' in p.standard_name:
                charge_params.append(p)
            elif 't' in p.standard_name or '时间' in p.standard_name:
                time_params.append(p)
            elif '温度' in p.standard_name or 'PD' in p.standard_name or 'EAS' in p.standard_name:
                thermal_params.append(p)
            else:
                other_params.append(p)
        
        def print_category(name, params):
            if params:
                print(f"\n   {name}:")
                for p in params:
                    name_str = p.standard_name[:29] if len(p.standard_name) > 29 else p.standard_name
                    value_str = str(p.value)[:34] if len(str(p.value)) > 34 else str(p.value)
                    cond_str = str(p.condition)[:29] if len(str(p.condition)) > 29 else str(p.condition)
                    print(f"   {name_str:<30} {value_str:<35} {cond_str:<30}")
        
        print_category("基本信息", basic_params)
        print_category("电压参数", voltage_params)
        print_category("电流参数", current_params)
        print_category("电阻参数", resistance_params)
        print_category("电容参数", capacitance_params)
        print_category("电荷参数", charge_params)
        print_category("时间参数", time_params)
        print_category("热特性参数", thermal_params)
        print_category("其他参数", other_params)
        
        # 记录结果
        result_data = {
            'pdf_name': pdf_name,
            'parse_time': parse_time,
            'extract_time': extract_time,
            'total_time': total_elapsed,
            'params_count': len(result.params),
            'success': True,
            'manufacturer': next((p.value for p in result.params if p.standard_name == '厂家'), ''),
            'opn': next((p.value for p in result.params if p.standard_name == 'OPN'), ''),
            'vds': next((p.value for p in result.params if p.standard_name == 'VDS'), ''),
            'ron': next((p.value for p in result.params if 'Ron' in p.standard_name), ''),
            'id': next((p.value for p in result.params if p.standard_name == 'ID Tc=25℃'), ''),
            'params': [{'name': p.standard_name, 'value': p.value, 'condition': p.condition} 
                      for p in result.params]
        }
        
        all_results.append(result_data)
        total_time += total_elapsed
        total_params += len(result.params)
    
    # ==================== 汇总 ====================
    print(f"\n{'=' * 100}")
    print(f"  汇总结果 ({len(all_results)} 个文件)")
    print(f"{'=' * 100}")
    
    if all_results:
        print(f"\n{'文件名':<45} {'厂家':<12} {'OPN':<20} {'参数数':<8} {'耗时':<8}")
        print(f"{'─' * 45} {'─' * 12} {'─' * 20} {'─' * 8} {'─' * 8}")
        
        for r in all_results:
            short_name = r['pdf_name'][:43] if len(r['pdf_name']) > 43 else r['pdf_name']
            mfr = r['manufacturer'][:11] if len(r['manufacturer']) > 11 else r['manufacturer']
            opn = r['opn'][:19] if len(r['opn']) > 19 else r['opn']
            print(f"{short_name:<45} {mfr:<12} {opn:<20} {r['params_count']:<8} {r['total_time']:>6.1f}s")
        
        print(f"{'─' * 45} {'─' * 12} {'─' * 20} {'─' * 8} {'─' * 8}")
        avg_time = total_time / len(all_results)
        avg_params = total_params / len(all_results)
        print(f"{'平均':<45} {'':<12} {'':<20} {avg_params:>7.1f} {avg_time:>6.1f}s")
        
        # 保存结果到JSON
        output_file = Path(__file__).parent / 'test_results_shanyangtong.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 测试完成，结果已保存到: {output_file.name}")
    else:
        print("\n⚠️  没有成功提取任何文件")
    
    return all_results


if __name__ == '__main__':
    run_test()
