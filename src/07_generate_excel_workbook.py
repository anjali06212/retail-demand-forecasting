import os
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_excel_workbook():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "outputs")
    excel_path = os.path.join(output_dir, "Retail_Demand_Forecasting_Inventory_Plan.xlsx")

    print("=" * 60)
    print("PHASE 9: GENERATING PROFESSIONAL EXCEL PORTFOLIO WORKBOOK")
    print("=" * 60)

    # 1. Load Data
    clean_df = pd.read_csv(os.path.join(base_dir, "data_processed", "clean_retail_demand.csv"))
    abc_df = pd.read_csv(os.path.join(output_dir, "abc_xyz_sku_classification.csv"))
    eval_df = pd.read_csv(os.path.join(output_dir, "forecast_evaluation_summary.csv"))
    inv_df = pd.read_csv(os.path.join(output_dir, "inventory_planning_table.csv"))

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styles
    font_title = Font(name='Segoe UI', size=16, bold=True, color='1E293B')
    font_subtitle = Font(name='Segoe UI', size=11, italic=True, color='64748B')
    font_section = Font(name='Segoe UI', size=13, bold=True, color='0F172A')
    font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
    font_data = Font(name='Segoe UI', size=10, color='1E293B')
    font_bold = Font(name='Segoe UI', size=10, bold=True, color='0F172A')
    font_kpi_num = Font(name='Segoe UI', size=18, bold=True, color='2563EB')
    font_kpi_label = Font(name='Segoe UI', size=9, bold=True, color='64748B')

    fill_header = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
    fill_sub_header = PatternFill(start_color='334155', end_color='334155', fill_type='solid')
    fill_kpi = PatternFill(start_color='F1F5F9', end_color='F1F5F9', fill_type='solid')
    fill_accent_a = PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid') # Soft green
    fill_accent_b = PatternFill(start_color='FEF9C3', end_color='FEF9C3', fill_type='solid') # Soft yellow
    fill_accent_c = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid') # Soft red

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    kpi_border = Border(
        left=Side(style='medium', color='94A3B8'),
        right=Side(style='medium', color='94A3B8'),
        top=Side(style='medium', color='94A3B8'),
        bottom=Side(style='medium', color='94A3B8')
    )

    # -----------------------------------------------------------------
    # TAB 1: EXECUTIVE SUMMARY
    # -----------------------------------------------------------------
    print("[1/4] Building Tab 1: Executive Summary...")
    ws1 = wb.create_sheet(title='Executive Summary')
    ws1.views.sheetView[0].showGridLines = True

    ws1['B2'] = "Retail Demand Forecasting & Inventory Planning"
    ws1['B2'].font = font_title
    ws1['B3'] = "Executive Portfolio Summary | Target Store: CA_1 | Category: FOODS_1"
    ws1['B3'].font = font_subtitle

    # KPI Cards
    kpis = [
        ('Total Historical Revenue', f"${clean_df['revenue'].sum():,.2f}"),
        ('Total Units Sold', f"{clean_df['units_sold'].sum():,}"),
        ('Active SKUs Tracked', f"{clean_df['item_id'].nunique()}"),
        ('Historical Tracking Days', f"{clean_df['d'].nunique()}"),
        ('Zero-Demand Day %', f"{(clean_df['units_sold'] == 0).mean()*100:.1f}%"),
        ('Best Forecast Model', f"{eval_df.loc[0, 'Model_Name']}"),
        ('Best Forecast WAPE', f"{eval_df.loc[0, 'WAPE_Pct']:.2f}%"),
        ('Avg Replenishment Lead Time', "7 Days (Supplier SLA)")
    ]

    for i, (label, val) in enumerate(kpis):
        r_start = 5 + (i // 4) * 3
        c_start = 2 + (i % 4) * 3
        
        # Merge 2x2 for card
        ws1.merge_cells(start_row=r_start, start_column=c_start, end_row=r_start+1, end_column=c_start+2)
        top_cell = ws1.cell(row=r_start, column=c_start, value=f"{val}\n{label}")
        top_cell.font = font_kpi_num
        top_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        
        for r in range(r_start, r_start+2):
            for c in range(c_start, c_start+3):
                cell = ws1.cell(row=r, column=c)
                cell.fill = fill_kpi
                cell.border = kpi_border

    # Overview Section
    ws1['B12'] = "Project Methodology & Governance Summary"
    ws1['B12'].font = font_section

    notes = [
        ("1. Data Pipeline", "413,208 daily records mined from Kaggle Walmart M5 dataset, merged with calendar and weekly sell prices."),
        ("2. SQL Star Schema", "SQLite star schema with 3 dimensions (dim_date, dim_product, dim_store) and 1 fact table (fact_daily_sales)."),
        ("3. ABC-XYZ Segmentation", "Pareto 80/15/5 revenue classification paired with Demand Coefficient of Variation (CV = std/mean)."),
        ("4. Explainable Forecasting", "Evaluated 4 explainable models over a 28-day forward holdout horizon; 28-Day SMA demonstrated lowest WAPE."),
        ("5. Inventory Planning", "Calculated Safety Stock (SS) and Reorder Points (ROP) with explicit 7-day lead time and 95%/90% service level assumptions.")
    ]

    for idx, (head, desc) in enumerate(notes, start=14):
        ws1.cell(row=idx, column=2, value=head).font = font_bold
        ws1.cell(row=idx, column=3, value=desc).font = font_data

    # -----------------------------------------------------------------
    # TAB 2: DEMAND & PRODUCT ANALYSIS
    # -----------------------------------------------------------------
    print("[2/4] Building Tab 2: Demand & Product Analysis...")
    ws2 = wb.create_sheet(title='Demand & Product Analysis')
    ws2.views.sheetView[0].showGridLines = True

    ws2['B2'] = "Product-Level Demand & Revenue Rankings (Top 25 SKUs)"
    ws2['B2'].font = font_section

    headers2 = ['Rank', 'Item ID', 'Category', 'Avg Unit Price', 'Total Units Sold', 'Total Revenue ($)', 'Avg Daily Demand', 'Zero-Demand %', 'ABC Class']
    for col_idx, h in enumerate(headers2, start=2):
        cell = ws2.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal='center', vertical='center')

    top25 = abc_df.head(25)
    for row_idx, (_, r) in enumerate(top25.iterrows(), start=5):
        ws2.cell(row=row_idx, column=2, value=row_idx-4).alignment = Alignment(horizontal='center')
        ws2.cell(row=row_idx, column=3, value=r['item_id']).alignment = Alignment(horizontal='center')
        ws2.cell(row=row_idx, column=4, value='FOODS_1').alignment = Alignment(horizontal='center')
        c_price = ws2.cell(row=row_idx, column=5, value=r['avg_price'])
        c_price.number_format = '$#,##0.00'
        c_units = ws2.cell(row=row_idx, column=6, value=r['total_units'])
        c_units.number_format = '#,##0'
        c_rev = ws2.cell(row=row_idx, column=7, value=r['total_revenue'])
        c_rev.number_format = '$#,##0.00'
        c_add = ws2.cell(row=row_idx, column=8, value=r['avg_daily_demand'])
        c_add.number_format = '#,##0.00'
        c_zero = ws2.cell(row=row_idx, column=9, value=r['zero_demand_pct']/100.0)
        c_zero.number_format = '0.0%'
        c_abc = ws2.cell(row=row_idx, column=10, value=r['abc_class'])
        c_abc.alignment = Alignment(horizontal='center')
        c_abc.font = font_bold
        if r['abc_class'] == 'A': c_abc.fill = fill_accent_a
        elif r['abc_class'] == 'B': c_abc.fill = fill_accent_b
        else: c_abc.fill = fill_accent_c

        for c in range(2, 11):
            ws2.cell(row=row_idx, column=c).border = thin_border
            ws2.cell(row=row_idx, column=c).font = font_data if c != 10 else font_bold

    # -----------------------------------------------------------------
    # TAB 3: ABC-XYZ SEGMENTATION
    # -----------------------------------------------------------------
    print("[3/4] Building Tab 3: ABC-XYZ Segmentation...")
    ws3 = wb.create_sheet(title='ABC-XYZ Matrix')
    ws3.views.sheetView[0].showGridLines = True

    ws3['B2'] = "ABC-XYZ SKU Segmentation & Replenishment Governance"
    ws3['B2'].font = font_section

    # Summary 9-box
    ws3['B4'] = "9-Box Matrix Summary"
    ws3['B4'].font = font_bold

    headers3_box = ['ABC Class', 'X (CV <= 0.50) Steady', 'Y (0.50 < CV <= 1.0) Seasonal', 'Z (CV > 1.0) Erratic', 'Total SKUs']
    for c_idx, h in enumerate(headers3_box, start=2):
        cell = ws3.cell(row=5, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    matrix_rows = [
        ('Class A (Top 80% Rev)', 0, 9, 100, 109),
        ('Class B (Next 15% Rev)', 0, 0, 62, 62),
        ('Class C (Bottom 5% Rev)', 0, 0, 45, 45),
        ('Total Department SKUs', 0, 9, 207, 216)
    ]

    for r_idx, (label, x_cnt, y_cnt, z_cnt, tot) in enumerate(matrix_rows, start=6):
        ws3.cell(row=r_idx, column=2, value=label).font = font_bold
        ws3.cell(row=r_idx, column=3, value=f"{x_cnt} SKUs").alignment = Alignment(horizontal='center')
        ws3.cell(row=r_idx, column=4, value=f"{y_cnt} SKUs").alignment = Alignment(horizontal='center')
        ws3.cell(row=r_idx, column=5, value=f"{z_cnt} SKUs").alignment = Alignment(horizontal='center')
        ws3.cell(row=r_idx, column=6, value=f"{tot} SKUs").alignment = Alignment(horizontal='center')
        ws3.cell(row=r_idx, column=6).font = font_bold

        for c in range(2, 7):
            ws3.cell(row=r_idx, column=c).border = thin_border

    # Full SKU Table
    ws3['B12'] = "Complete SKU-Level ABC-XYZ Classification"
    ws3['B12'].font = font_bold

    headers3_full = ['Item ID', 'Total Revenue ($)', 'Cumulative Rev %', 'ABC Class', 'Avg Daily Demand', 'Std Dev Demand', 'CV (Variability)', 'XYZ Class', 'Segment', 'Replenishment Policy']
    for c_idx, h in enumerate(headers3_full, start=2):
        cell = ws3.cell(row=13, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_sub_header
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for r_idx, (_, r) in enumerate(abc_df.iterrows(), start=14):
        ws3.cell(row=r_idx, column=2, value=r['item_id']).alignment = Alignment(horizontal='center')
        c_rev = ws3.cell(row=r_idx, column=3, value=r['total_revenue'])
        c_rev.number_format = '$#,##0.00'
        c_cum = ws3.cell(row=r_idx, column=4, value=r['cumulative_rev_pct']/100.0)
        c_cum.number_format = '0.0%'
        c_abc = ws3.cell(row=r_idx, column=5, value=r['abc_class'])
        c_abc.alignment = Alignment(horizontal='center')
        c_abc.font = font_bold

        c_add = ws3.cell(row=r_idx, column=6, value=r['avg_daily_demand'])
        c_add.number_format = '#,##0.00'
        c_std = ws3.cell(row=r_idx, column=7, value=r['std_daily_demand'])
        c_std.number_format = '#,##0.00'
        c_cv = ws3.cell(row=r_idx, column=8, value=r['cv_demand'])
        c_cv.number_format = '#,##0.00'
        c_xyz = ws3.cell(row=r_idx, column=9, value=r['xyz_class'])
        c_xyz.alignment = Alignment(horizontal='center')
        c_xyz.font = font_bold

        c_seg = ws3.cell(row=r_idx, column=10, value=r['abc_xyz_segment'])
        c_seg.alignment = Alignment(horizontal='center')
        c_seg.font = font_bold
        ws3.cell(row=r_idx, column=11, value=r['replenishment_strategy'])

        for c in range(2, 12):
            ws3.cell(row=r_idx, column=c).border = thin_border
            ws3.cell(row=r_idx, column=c).font = font_data if c not in [5, 9, 10] else font_bold

    # -----------------------------------------------------------------
    # TAB 4: FORECAST & INVENTORY PLAN (WITH LIVE DYNAMIC FORMULAS)
    # -----------------------------------------------------------------
    print("[4/4] Building Tab 4: Forecast & Inventory Plan...")
    ws4 = wb.create_sheet(title='Forecast & Inventory Plan')
    ws4.views.sheetView[0].showGridLines = True

    ws4['B2'] = "28-Day Forecasting Benchmark & Interactive Inventory Planning Calculator"
    ws4['B2'].font = font_section

    # Section A: Forecasting Benchmark Table
    ws4['B4'] = "1. Empirical Forecasting Model Benchmark (28-Day Holdout Period)"
    ws4['B4'].font = font_bold

    headers4_fc = ['Forecasting Model', 'MAE (Units)', 'RMSE (Units)', 'WAPE % (Accuracy Metric)', 'Forecast Bias %', 'Model Recommendation']
    for c_idx, h in enumerate(headers4_fc, start=2):
        cell = ws4.cell(row=5, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for r_idx, (_, r) in enumerate(eval_df.iterrows(), start=6):
        ws4.cell(row=r_idx, column=2, value=r['Model_Name']).font = font_bold
        ws4.cell(row=r_idx, column=3, value=r['MAE']).number_format = '#,##0.000'
        ws4.cell(row=r_idx, column=4, value=r['RMSE']).number_format = '#,##0.000'
        c_wape = ws4.cell(row=r_idx, column=5, value=r['WAPE_Pct']/100.0)
        c_wape.number_format = '0.00%'
        c_wape.font = font_bold
        c_bias = ws4.cell(row=r_idx, column=6, value=r['Forecast_Bias_Pct']/100.0)
        c_bias.number_format = '+0.00%;-0.00%'

        rec = "Best Model (Selected)" if r_idx == 6 else "Benchmark Comparison"
        c_rec = ws4.cell(row=r_idx, column=7, value=rec)
        c_rec.alignment = Alignment(horizontal='center')
        if r_idx == 6:
            c_rec.fill = fill_accent_a
            c_rec.font = font_bold

        for c in range(2, 8):
            ws4.cell(row=r_idx, column=c).border = thin_border
            if c != 2 and c != 5 and (c != 7 or r_idx != 6):
                ws4.cell(row=r_idx, column=c).font = font_data

    # Section B: Inventory Planning Dynamic Table with LIVE EXCEL FORMULAS
    ws4['B12'] = "2. SKU Inventory Planning Table (Dynamic Live Excel Formulas)"
    ws4['B12'].font = font_bold
    ws4['B13'] = "Formulas: Lead-Time Demand = ADD * Lead_Time | Safety Stock = Z * StdDev * SQRT(Lead_Time) | Reorder Point = LTD + SS"
    ws4['B13'].font = font_subtitle

    headers4_inv = [
        'Item ID', 'ABC Class', 'Avg Daily Demand (ADD)', 'Std Dev Demand', 'Lead Time (Days)',
        'Target Service Level', 'Z-Score', 'Lead-Time Demand (LTD) [Formula]',
        'Safety Stock (Units) [Formula]', 'Reorder Point (ROP) [Formula]', 'Replenishment Action'
    ]
    for c_idx, h in enumerate(headers4_inv, start=2):
        cell = ws4.cell(row=14, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_sub_header
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    for r_idx, (_, r) in enumerate(inv_df.iterrows(), start=15):
        ws4.cell(row=r_idx, column=2, value=r['item_id']).alignment = Alignment(horizontal='center')
        c_abc = ws4.cell(row=r_idx, column=3, value=r['abc_class'])
        c_abc.alignment = Alignment(horizontal='center')
        c_abc.font = font_bold

        c_add = ws4.cell(row=r_idx, column=4, value=r['avg_daily_demand'])
        c_add.number_format = '#,##0.00'
        c_std = ws4.cell(row=r_idx, column=5, value=r['std_daily_demand'])
        c_std.number_format = '#,##0.00'
        c_lt = ws4.cell(row=r_idx, column=6, value=r['lead_time_days'])
        c_lt.alignment = Alignment(horizontal='center')
        c_sl = ws4.cell(row=r_idx, column=7, value=r['target_service_level'])
        c_sl.number_format = '0.0%'
        c_sl.alignment = Alignment(horizontal='center')
        c_z = ws4.cell(row=r_idx, column=8, value=r['z_score'])
        c_z.number_format = '0.00'
        c_z.alignment = Alignment(horizontal='center')

        # LIVE EXCEL FORMULAS!
        # Formula for LTD: =ROUND(D{r_idx} * F{r_idx}, 2)
        c_ltd = ws4.cell(row=r_idx, column=9, value=f"=ROUND(D{r_idx}*F{r_idx}, 2)")
        c_ltd.number_format = '#,##0.00'

        # Formula for Safety Stock: =ROUND(H{r_idx} * E{r_idx} * SQRT(F{r_idx}), 2)
        c_ss = ws4.cell(row=r_idx, column=10, value=f"=ROUND(H{r_idx}*E{r_idx}*SQRT(F{r_idx}), 2)")
        c_ss.number_format = '#,##0.00'
        c_ss.font = font_bold

        # Formula for Reorder Point: =ROUND(I{r_idx} + J{r_idx}, 2)
        c_rop = ws4.cell(row=r_idx, column=11, value=f"=ROUND(I{r_idx}+J{r_idx}, 2)")
        c_rop.number_format = '#,##0.00'
        c_rop.font = font_bold

        ws4.cell(row=r_idx, column=12, value=r['replenishment_policy'])

        for c in range(2, 13):
            ws4.cell(row=r_idx, column=c).border = thin_border
            if c not in [3, 10, 11]:
                ws4.cell(row=r_idx, column=c).font = font_data

    # Auto-adjust column widths for all worksheets
    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or '')
                if '\n' in val:
                    val = max(val.split('\n'), key=len)
                if not str(val).startswith('='): # Don't size on raw formula string
                    max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Save Workbook
    wb.save(excel_path)
    print(f"\n[SUCCESS] Excel Portfolio Workbook Created Successfully at:")
    print(f"  -> {excel_path}")
    print("=" * 60)

if __name__ == '__main__':
    build_excel_workbook()
