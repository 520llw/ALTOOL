# -*- coding: utf-8 -*-
"""
Excel最终输出精度测试
模拟 generate_comparison_table 的完整匹配逻辑，
以最终写入Excel的参数值来计算 Precision 和 Recall。

P = 正确填入的单元格数 / Excel中实际填入值的单元格数
R = 正确填入的单元格数 / PDF中应该填入的单元格数
"""

import os, sys, re, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import config
from backend.db_manager import DatabaseManager, StandardParam, ParamVariant
from backend.pdf_parser import PDFParser
from backend.ai_processor import AIProcessor

# ===================== 标准答案（完整版，以参数库标准名为key）=====================
GROUND_TRUTH = {
    "LSGT10R011_V1.0.pdf": {
        "PDF文件名": "LSGT10R011_V1.0.pdf", "厂家": "Lonten", "OPN": "LSGT10R011",
        "封装": "TOLL", "厂家封装名": "TOLL", "极性": "N-channel",
        "技术": "Shielded Gate Trench DMOS", "特殊功能": "Fast switching",
        "认证": "Green device", "安装": "SMD",
        "VDS": "100V", "Vgs min": "-20V", "Vgs max": "20V",
        "Vth min": "2V", "Vth type": "3.18V", "Vth max": "4V", "Vplateau": "4.9V",
        "Ron 10V_type": "0.98mΩ", "Ron 10V_max": "1.15mΩ",
        "RDS(on) 10V TJ=175℃": "2.16mΩ", "Rg": "1.49Ω",
        "ID Tc=25℃": "478A", "ID TA=25℃": "420A",
        "ID Tc=100℃": "338A", "ID puls Tc=25℃": "1680A",
        "Idss": "1μA", "IDSS TJ=175℃": "300μA",
        "Igss": "100nA", "IGSSF": "100nA", "IGSSR": "-100nA",
        "Is": "420A", "Ism": "1680A", "Irrm": "3.62A", "gfs": "176S",
        "Ciss": "14838pF", "Coss": "3458pF", "Crss": "73pF",
        "Qg": "260.1nC", "Qg_10V": "260.1nC", "Qgs": "69.1nC",
        "Qgd": "78.0nC", "Qoss": "302.5nC", "Qrr": "191.4nC",
        "td-on": "160.5ns", "tr": "183.1ns", "td-off": "322.5ns",
        "tf": "135.1ns", "trr": "83.9ns",
        "反二极管压降Vsd": "1.1V",
        "EAS L=0.1mH": "1764mJ", "PD Tc=25℃": "577W",
        "RthJC max": "0.26℃/W", "RthJA max": "62℃/W",
        "工作温度min": "-55", "工作温度max": "175",
        "TSTG min": "-55", "TSTG max": "175", "Tsold": "260℃",
        "Qg测试条件": "VDS=50V, ID=50A, VGS=10V",
        "Ciss测试条件": "VDS=50V, VGS=0V, f=250kHz",
        "开关时间测试条件": "VDD=50V, VGS=10V, ID=50A, Rg=10Ω",
        "Qrr测试条件": "IS=50A, di/dt=100A/us, TJ=25℃",
        "EAS测试条件": "VDD=50V, VGS=10V, L=0.5mH, IAS=84A",
        "IDM限制条件": "Pulse width limited by maximum junction temperature",
    },
    "LSGT10R016_V1.0.pdf": {
        "PDF文件名": "LSGT10R016_V1.0.pdf", "厂家": "Lonten", "OPN": "LSGT10R016",
        "封装": "TOLL", "厂家封装名": "TOLL", "极性": "N-channel",
        "技术": "Shielded Gate Trench DMOS", "特殊功能": "Fast switching",
        "认证": "Green device", "安装": "SMD",
        "VDS": "100V", "Vgs min": "-20V", "Vgs max": "20V",
        "Vth min": "2V", "Vth type": "3.3V", "Vth max": "4V", "Vplateau": "5.5V",
        "Ron 10V_type": "1.44mΩ", "Ron 10V_max": "1.65mΩ",
        "RDS(on) 10V TJ=175℃": "3.08mΩ", "Rg": "2.17Ω",
        "ID Tc=25℃": "348A", "ID TA=25℃": "300A",
        "ID Tc=100℃": "246A", "ID puls Tc=25℃": "1200A",
        "Idss": "1μA", "IDSS TJ=175℃": "300μA",
        "Igss": "100nA", "IGSSF": "100nA", "IGSSR": "-100nA",
        "Is": "300A", "Ism": "1200A", "Irrm": "3.15A", "gfs": "160S",
        "Ciss": "10017pF", "Coss": "2332pF", "Crss": "70pF",
        "Qg": "175.4nC", "Qg_10V": "175.4nC", "Qgs": "52.2nC",
        "Qgd": "55nC", "Qoss": "210nC", "Qrr": "138.7nC",
        "td-on": "139.6ns", "tr": "161.5ns", "td-off": "201.3ns",
        "tf": "93.2ns", "trr": "70.6ns",
        "反二极管压降Vsd": "1.1V",
        "EAS L=0.1mH": "1190mJ", "PD Tc=25℃": "429W",
        "RthJC max": "0.35℃/W", "RthJA max": "62℃/W",
        "工作温度min": "-55", "工作温度max": "175",
        "TSTG min": "-55", "TSTG max": "175", "Tsold": "260℃",
        "Qg测试条件": "VDS=50V, ID=50A, VGS=10V",
        "Ciss测试条件": "VDS=50V, VGS=0V, f=250kHz",
        "开关时间测试条件": "VDD=50V, VGS=10V, ID=50A, Rg=10Ω",
        "Qrr测试条件": "IS=50A, di/dt=100A/us, TJ=25℃",
        "EAS测试条件": "VDD=50V, VGS=10V, L=0.5mH, IAS=69A",
        "IDM限制条件": "Pulse width limited by maximum junction temperature",
    },
    "LSGT10R013_V1.1(1).pdf": {
        "PDF文件名": "LSGT10R013_V1.1(1).pdf", "厂家": "Lonten", "OPN": "LSGT10R013",
        "封装": "TOLL", "厂家封装名": "TOLL", "极性": "N-channel",
        "技术": "Shielded Gate Trench DMOS", "特殊功能": "Fast switching",
        "认证": "Green device", "安装": "SMD",
        "VDS": "100V", "Vgs min": "-20V", "Vgs max": "20V",
        "Vth min": "2V", "Vth type": "2.87V", "Vth max": "4V", "Vplateau": "4.6V",
        "Ron 10V_type": "1.05mΩ", "Ron 10V_max": "1.35mΩ",
        "RDS(on) 10V TJ=175℃": "2.29mΩ", "Rg": "1.34Ω",
        "ID Tc=25℃": "445A", "ID TA=25℃": "420A",
        "ID Tc=100℃": "314A", "ID puls Tc=25℃": "1680A",
        "Idss": "1μA", "IDSS TJ=175℃": "300μA",
        "Igss": "100nA", "IGSSF": "100nA", "IGSSR": "-100nA",
        "Is": "420A", "Ism": "1680A", "Irrm": "4.29A", "gfs": "161.8S",
        "Ciss": "16020pF", "Coss": "1980pF", "Crss": "72.6pF",
        "Qg": "252.9nC", "Qg_10V": "252.9nC", "Qgs": "67.4nC",
        "Qgd": "65.2nC", "Qoss": "258nC", "Qrr": "213.6nC",
        "td-on": "133.1ns", "tr": "161.1ns", "td-off": "239ns",
        "tf": "101.9ns", "trr": "84.4ns",
        "反二极管压降Vsd": "1.1V",
        "EAS L=0.1mH": "1764mJ", "PD Tc=25℃": "581W",
        "RthJC max": "0.26℃/W", "RthJA max": "62℃/W",
        "工作温度min": "-55", "工作温度max": "175",
        "TSTG min": "-55", "TSTG max": "175", "Tsold": "260℃",
        "Qg测试条件": "VDS=50V, ID=50A, VGS=10V",
        "Ciss测试条件": "VDS=50V, VGS=0V, f=100kHz",
        "开关时间测试条件": "VDD=50V, VGS=10V, ID=50A, Rg=10Ω",
        "Qrr测试条件": "IS=50A, di/dt=100A/us, TJ=25℃",
        "EAS测试条件": "VDD=50V, VGS=10V, L=0.5mH, IAS=84A",
        "IDM限制条件": "Pulse width limited by maximum junction temperature",
    },
    "LSGT20R089HCF _V1.3.pdf": {
        "PDF文件名": "LSGT20R089HCF _V1.3.pdf", "厂家": "Lonten", "OPN": "LSGT20R089HCF",
        "封装": "TOLL", "厂家封装名": "TOLL", "极性": "N-channel",
        "技术": "Shielded Gate Trench DMOS", "特殊功能": "Fast switching",
        "认证": "Pb-free", "安装": "SMD",
        "VDS": "200V", "Vgs min": "-20V", "Vgs max": "20V",
        "Vth min": "2.5V", "Vth max": "4.5V", "Vplateau": "4.9V",
        "Ron 10V_type": "7.8mΩ", "Ron 10V_max": "8.95mΩ",
        "RDS(on) 10V TJ=150℃": "16.6mΩ", "Rg": "1.3Ω",
        "ID Tc=25℃": "159A", "ID TA=25℃": "360A",
        "ID Tc=100℃": "100A", "ID puls Tc=25℃": "636A",
        "Idss": "1μA", "IDSS TJ=150℃": "10mA",
        "Igss": "100nA", "IGSSF": "100nA", "IGSSR": "-100nA",
        "Is": "159A", "Ism": "636A", "gfs": "86S",
        "Ciss": "4947pF", "Coss": "513pF", "Crss": "7.8pF",
        "Qg": "63.5nC", "Qg_10V": "63.5nC", "Qgs": "23.5nC",
        "Qgd": "9.9nC", "Qoss": "170nC", "Qrr": "1167nC",
        "td-on": "51.2ns", "tr": "98.8ns", "td-off": "62ns",
        "tf": "16.5ns", "trr": "121ns",
        "反二极管压降Vsd": "1.1V",
        "EAS L=0.1mH": "1122mJ", "PD Tc=25℃": "481W",
        "RthJC max": "0.26℃/W", "RthJA max": "62℃/W",
        "工作温度min": "-55", "工作温度max": "150",
        "TSTG min": "-55", "TSTG max": "150", "Tsold": "260℃",
        "Qg测试条件": "VDS=100V, ID=50A, VGS=10V",
        "Ciss测试条件": "VDS=100V, VGS=0V, f=250kHz",
        "开关时间测试条件": "VDD=100V, VGS=10V, ID=50A, RG=10Ω",
        "Qrr测试条件": "IS=50A, di/dt=200A/us, TJ=25℃",
        "EAS测试条件": "VDD=50V, VGS=10V, L=0.5mH, IAS=67A",
        "IDM限制条件": "Pulse width limited by maximum junction temperature",
    },
}


def extract_number(s):
    if not s or not isinstance(s, str):
        return None
    m = re.search(r'[-+]?\d*\.?\d+', s.strip())
    return float(m.group()) if m else None


def values_match(gt_val, ext_val, param_name):
    if not gt_val or not ext_val:
        return False
    gt_val, ext_val = gt_val.strip(), ext_val.strip()

    text_params = {'厂家', 'OPN', '封装', '厂家封装名', '极性', '技术', '特殊功能', '认证',
                   'Product Status', '安装', 'PDF文件名',
                   'Qg测试条件', 'Ciss测试条件', '开关时间测试条件', 'Qrr测试条件',
                   'EAS测试条件', 'IDM限制条件'}
    if param_name in text_params:
        gt_l = gt_val.lower().replace(' ', '').replace('-', '')
        ex_l = ext_val.lower().replace(' ', '').replace('-', '')
        if '测试条件' in param_name or '限制条件' in param_name:
            gt_nums = set(re.findall(r'\d+\.?\d*', gt_val))
            ex_nums = set(re.findall(r'\d+\.?\d*', ext_val))
            return len(gt_nums & ex_nums) >= len(gt_nums) * 0.6
        return gt_l in ex_l or ex_l in gt_l

    gn, en = extract_number(gt_val), extract_number(ext_val)
    if gn is None or en is None:
        return gt_val.replace(' ', '') == ext_val.replace(' ', '')
    if gn == 0:
        return en == 0
    return abs(gn - en) / abs(gn) <= 0.05


def build_excel_param_map(session):
    """复刻 generate_comparison_table 中的参数名映射逻辑"""
    all_params = session.query(StandardParam).order_by(StandardParam.id).all()
    param_names = [p.param_name for p in all_params]

    param_name_map = {}
    for p in all_params:
        norm = p.param_name.lower().replace(' ', '').replace('_', '').replace('-', '')
        param_name_map[norm] = p.param_name
        param_name_map[p.param_name] = p.param_name
        if p.param_name_en:
            param_name_map[p.param_name_en] = p.param_name
            en_norm = p.param_name_en.lower().replace(' ', '').replace('_', '').replace('-', '')
            param_name_map[en_norm] = p.param_name
        variants = session.query(ParamVariant).filter_by(param_id=p.id).all()
        for v in variants:
            vn = v.variant_name.lower().replace(' ', '').replace('_', '').replace('-', '')
            param_name_map[vn] = p.param_name
            param_name_map[v.variant_name] = p.param_name

    legacy = {
        'Ron 10V_type': 'RDS(on) 10V_type', 'Ron 10V_max': 'RDS(on) 10V_max',
        'Ron 4.5V_type': 'RDS(on) 4.5V_type', 'Ron 4.5V_max': 'RDS(on) 4.5V_max',
        'Ron 2.5V_type': 'RDS(on) 2.5V_type', 'Ron 2.5V_max': 'RDS(on) 2.5V_max',
        'Igss': 'IGSSF',
        'ID Tc=25℃': 'ID TC=25℃', 'ID Tc=100℃': 'ID TC=100℃',
        'ID puls Tc=25℃': 'ID puls TC=25℃', 'PD Tc=25℃': 'PD TC=25℃',
    }
    valid_names = set(param_names)
    for old, new in legacy.items():
        if new in valid_names:
            param_name_map[old] = new
            param_name_map[old.lower().replace(' ', '').replace('_', '').replace('-', '')] = new

    return param_names, param_name_map


def simulate_excel_row(extracted_params, param_names, param_name_map):
    """模拟 generate_comparison_table 为一个PDF生成的Excel行"""
    excel_row = {}  # standard_param_name -> value

    for p in extracted_params:
        name = p.standard_name
        value = p.value or '-'
        if not name or value == '-':
            continue

        matched = None
        if name in param_name_map:
            matched = param_name_map[name]
        else:
            norm = name.lower().replace(' ', '').replace('_', '').replace('-', '')
            if norm in param_name_map:
                matched = param_name_map[norm]

        if matched and matched in set(param_names):
            # 只保留第一个匹配的值（与实际逻辑一致）
            if matched not in excel_row:
                excel_row[matched] = value

    return excel_row


def run_test():
    print("=" * 80)
    print("  Excel 最终输出精度测试")
    print(f"  模型: {config.ai.model} | Provider: {config.ai.provider}")
    print("  P = 正确填入 / Excel实际填入 | R = 正确填入 / PDF中应填入")
    print("=" * 80)

    db = DatabaseManager()
    session = db.get_session()
    parser = PDFParser()
    ai = AIProcessor()
    params_info = db.get_all_params_with_variants()

    param_names, param_name_map = build_excel_param_map(session)
    param_names_set = set(param_names)
    print(f"\n参数库: {len(param_names)} 个标准参数列")

    total_tp, total_filled, total_should = 0, 0, 0
    all_results = {}

    for pdf_name, gt in GROUND_TRUTH.items():
        pdf_path = Path(__file__).parent / pdf_name
        if not pdf_path.exists():
            print(f"\n⚠ 文件不存在: {pdf_name}")
            continue

        # 把GT中的key也通过映射转成Excel列名
        gt_excel = {}
        for gk, gv in gt.items():
            if gk in param_name_map:
                mapped = param_name_map[gk]
                if mapped in param_names_set:
                    gt_excel[mapped] = gv
            else:
                norm = gk.lower().replace(' ', '').replace('_', '').replace('-', '')
                if norm in param_name_map:
                    mapped = param_name_map[norm]
                    if mapped in param_names_set:
                        gt_excel[mapped] = gv

        print(f"\n{'─' * 80}")
        print(f"📄 {pdf_name}")
        print(f"   标准答案映射到Excel列: {len(gt_excel)} 个")

        # 提取
        pdf_content = parser.parse_pdf(str(pdf_path))
        t0 = time.time()
        result = ai.extract_params(pdf_content, params_info, parallel=True)
        elapsed = time.time() - t0

        if result.error:
            print(f"   ❌ 提取错误: {result.error}")
            continue

        # 模拟Excel行
        excel_row = simulate_excel_row(result.params, param_names, param_name_map)
        print(f"   AI提取 → Excel填入: {len(excel_row)} 个单元格, 耗时 {elapsed:.1f}s")

        # 对比
        tp, wrong_list, missed_list, extra_list = 0, [], [], []

        for col_name, gt_val in gt_excel.items():
            if col_name in excel_row:
                if values_match(gt_val, excel_row[col_name], col_name):
                    tp += 1
                else:
                    wrong_list.append((col_name, gt_val, excel_row[col_name]))
            else:
                missed_list.append((col_name, gt_val))

        # 多填的（Excel中有值但不在GT中的）
        for col_name, val in excel_row.items():
            if col_name not in gt_excel:
                extra_list.append((col_name, val))

        n_filled = len(excel_row)
        n_should = len(gt_excel)
        p = tp / n_filled * 100 if n_filled else 0
        r = tp / n_should * 100 if n_should else 0
        f1 = 2 * p * r / (p + r) if (p + r) else 0

        print(f"\n   📊 Excel输出统计:")
        print(f"   ├─ 应填入: {n_should} 个 (PDF中存在的参数)")
        print(f"   ├─ 实际填入: {n_filled} 个")
        print(f"   ├─ 正确(TP): {tp}")
        print(f"   ├─ 值错误:   {len(wrong_list)}")
        print(f"   ├─ 漏填(FN): {len(missed_list)}")
        print(f"   ├─ 多填(FP): {len(extra_list)}")
        print(f"   ├─ Precision: {p:.1f}%")
        print(f"   ├─ Recall:    {r:.1f}%")
        print(f"   └─ F1-Score:  {f1:.1f}%")

        if wrong_list:
            print(f"\n   ⚠ 值错误:")
            for c, gv, ev in wrong_list:
                print(f"     {c}: 标准={gv} → 提取={ev}")
        if missed_list:
            print(f"\n   ❌ 漏填:")
            for c, gv in missed_list:
                print(f"     {c}: 应为={gv}")
        if extra_list:
            print(f"\n   ➕ 多填 (不在标准答案中):")
            for c, v in extra_list:
                print(f"     {c}: {v}")

        all_results[pdf_name] = {
            'tp': tp, 'filled': n_filled, 'should': n_should,
            'p': p, 'r': r, 'f1': f1, 'time': elapsed,
            'wrong': len(wrong_list), 'missed': len(missed_list), 'extra': len(extra_list)
        }
        total_tp += tp
        total_filled += n_filled
        total_should += n_should

    # 汇总
    avg_p = total_tp / total_filled * 100 if total_filled else 0
    avg_r = total_tp / total_should * 100 if total_should else 0
    avg_f1 = 2 * avg_p * avg_r / (avg_p + avg_r) if (avg_p + avg_r) else 0

    print(f"\n{'=' * 80}")
    print(f"  汇总（以Excel最终输出为准）")
    print(f"{'=' * 80}")
    print(f"\n{'文件':<35} {'P':>8} {'R':>8} {'F1':>8} {'正确':>5} {'填入':>5} {'应填':>5} {'错':>4} {'漏':>4} {'耗时':>7}")
    print(f"{'─'*35} {'─'*8} {'─'*8} {'─'*8} {'─'*5} {'─'*5} {'─'*5} {'─'*4} {'─'*4} {'─'*7}")
    for name, r in all_results.items():
        short = name[:33]
        print(f"{short:<35} {r['p']:>7.1f}% {r['r']:>7.1f}% {r['f1']:>7.1f}% {r['tp']:>5} {r['filled']:>5} {r['should']:>5} {r['wrong']:>4} {r['missed']:>4} {r['time']:>5.1f}s")
    print(f"{'─'*35} {'─'*8} {'─'*8} {'─'*8} {'─'*5} {'─'*5} {'─'*5} {'─'*4} {'─'*4} {'─'*7}")
    print(f"{'总计':<33} {avg_p:>7.1f}% {avg_r:>7.1f}% {avg_f1:>7.1f}% {total_tp:>5} {total_filled:>5} {total_should:>5}")

    session.close()
    print(f"\n✅ 测试完成")


if __name__ == '__main__':
    run_test()
