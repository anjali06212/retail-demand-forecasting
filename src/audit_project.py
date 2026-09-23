import os
import sqlite3
import pandas as pd
import numpy as np
import openpyxl

def audit_all():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 70)
    print("STARTING TECHNICAL AUDIT")
    print("=" * 70)

    # 1. Check Raw Data Untouched
    print("\n--- 1. Raw Data Check ---")
    data_dir = os.path.join(base_dir, "data")
    for f in ['calendar.csv', 'sales_train_validation.csv', 'sell_prices.csv']:
        p = os.path.join(data_dir, f)
        print(f"  {f}: Exists={os.path.exists(p)}, Size={os.path.getsize(p):,} bytes")

    # 2. Check Clean Processed Data
    print("\n--- 2. Clean Data Verification ---")
    clean_path = os.path.join(base_dir, "data_processed", "clean_retail_demand.csv")
    df = pd.read_csv(clean_path)
    print(f"  Shape: {df.shape}")
    print(f"  Unique SKUs: {df['item_id'].nunique()} (Expected: 216)")
    print(f"  Unique Dates: {df['date'].nunique()} (Expected: 1913)")
    print(f"  Total Expected Grid: 216 * 1913 = {216 * 1913} == {len(df)} ({len(df) == 216 * 1913})")
    print(f"  Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Total Units: {df['units_sold'].sum():,} (Expected: 567,849)")
    print(f"  Total Revenue: ${df['revenue'].sum():,.2f} (Expected: $1,303,428.49)")
    print(f"  Avg Selling Price: ${df['sell_price'].mean():.2f} (Expected: $3.24)")
    zero_pct = (df['units_sold'] == 0).mean() * 100
    print(f"  Zero-Demand %: {zero_pct:.2f}% (Expected: 59.29%)")
    print(f"  Null count across all columns:\n{df.isnull().sum().to_dict()}")
    print(f"  Duplicates count: {df.duplicated().sum()}")

    # 3. Check SQLite DB
    print("\n--- 3. SQLite Database Verification ---")
    db_path = os.path.join(base_dir, "database", "retail_demand.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM dim_date")
    print(f"  dim_date rows: {cur.fetchone()[0]} (Expected: 1913)")
    cur.execute("SELECT COUNT(*) FROM dim_product")
    print(f"  dim_product rows: {cur.fetchone()[0]} (Expected: 216)")
    cur.execute("SELECT COUNT(*) FROM dim_store")
    print(f"  dim_store rows: {cur.fetchone()[0]} (Expected: 1)")
    cur.execute("SELECT store_id, state_id, store_name FROM dim_store")
    print(f"  dim_store content: {cur.fetchall()}")
    cur.execute("SELECT COUNT(*) FROM fact_daily_sales")
    print(f"  fact_daily_sales rows: {cur.fetchone()[0]} (Expected: 413,208)")
    cur.execute("SELECT SUM(units_sold), ROUND(SUM(revenue), 2) FROM fact_daily_sales")
    db_u, db_r = cur.fetchone()
    print(f"  fact_daily_sales Units: {db_u:,}, Revenue: ${db_r:,.2f}")

    # Check for orphan fact records
    cur.execute("""
        SELECT COUNT(*) FROM fact_daily_sales f
        LEFT JOIN dim_date d ON f.date_key = d.date_key
        WHERE d.date_key IS NULL
    """)
    print(f"  Orphan date keys: {cur.fetchone()[0]}")
    cur.execute("""
        SELECT COUNT(*) FROM fact_daily_sales f
        LEFT JOIN dim_product p ON f.item_id = p.item_id
        WHERE p.item_id IS NULL
    """)
    print(f"  Orphan product keys: {cur.fetchone()[0]}")
    conn.close()

    # 4. Check Forecasting Implementation & Leakage
    print("\n--- 4. Forecasting Verification ---")
    pred_path = os.path.join(base_dir, "outputs", "forecast_predictions_28d.csv")
    pred_df = pd.read_csv(pred_path)
    print(f"  Predictions Shape: {pred_df.shape} (Expected: 6,048 = 216 * 28)")
    print(f"  Prediction Dates: {pred_df['date'].min()} to {pred_df['date'].max()} ({pred_df['date'].nunique()} days)")
    
    # Check metric calculations
    eval_path = os.path.join(base_dir, "outputs", "forecast_evaluation_summary.csv")
    eval_df = pd.read_csv(eval_path)
    print(f"  Evaluation Summary:\n{eval_df.to_string(index=False)}")

    # 5. Check ABC-XYZ & Inventory Calculations
    print("\n--- 5. ABC-XYZ & Inventory Verification ---")
    abc_path = os.path.join(base_dir, "outputs", "abc_xyz_sku_classification.csv")
    abc_df = pd.read_csv(abc_path)
    print(f"  ABC breakdown:\n{abc_df['abc_class'].value_counts().to_dict()}")
    print(f"  XYZ breakdown:\n{abc_df['xyz_class'].value_counts().to_dict()}")
    print(f"  9-box matrix counts:\n{abc_df['abc_xyz_segment'].value_counts().to_dict()}")

    inv_path = os.path.join(base_dir, "outputs", "inventory_planning_table.csv")
    inv_df = pd.read_csv(inv_path)
    print(f"  Inventory Table Shape: {inv_df.shape}")
    print(f"  Inventory Sample (First row):\n{inv_df.iloc[0].to_dict()}")

    # 6. Check Excel Workbook Sheet & Cell Formula Integrity
    print("\n--- 6. Excel Workbook Verification ---")
    excel_path = os.path.join(base_dir, "outputs", "Retail_Demand_Forecasting_Inventory_Plan.xlsx")
    wb = openpyxl.load_workbook(excel_path, data_only=False)
    print(f"  Sheets in Workbook: {wb.sheetnames}")
    
    ws4 = wb['Forecast & Inventory Plan']
    print(f"  Tab 4 Header Row 14 Values:")
    for col in range(2, 13):
        print(f"    Col {openpyxl.utils.get_column_letter(col)}: '{ws4.cell(row=14, column=col).value}'")
    
    print(f"  Tab 4 Row 15 Content & Formulas:")
    for col in range(2, 13):
        c_letter = openpyxl.utils.get_column_letter(col)
        c_val = ws4.cell(row=15, column=col).value
        print(f"    Col {c_letter} ({c_letter}15): {c_val}")

    # 7. Check Power BI CSV Exports
    print("\n--- 7. Power BI Exports Verification ---")
    pbi_dir = os.path.join(base_dir, "powerbi")
    for f in os.listdir(pbi_dir):
        if f.endswith('.csv'):
            p_file = os.path.join(pbi_dir, f)
            p_df = pd.read_csv(p_file)
            print(f"  {f}: {p_df.shape}, Cols={p_df.columns.tolist()[:4]}...")

    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    audit_all()
