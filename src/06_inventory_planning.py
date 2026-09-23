import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_inventory_planning():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abc_path = os.path.join(base_dir, "outputs", "abc_xyz_sku_classification.csv")
    output_dir = os.path.join(base_dir, "outputs")
    chart_dir = os.path.join(output_dir, "charts")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(chart_dir, exist_ok=True)

    print("=" * 60)
    print("PHASE 8: BASIC INVENTORY PLANNING & REPLENISHMENT")
    print("=" * 60)

    # 1. Load ABC-XYZ SKU Table
    print("[1/3] Loading SKU Demand Statistics and ABC-XYZ Classification...")
    df_skus = pd.read_csv(abc_path)

    # 2. Inventory Planning Calculations with Explicit Documented Assumptions
    print("[2/3] Applying Explainable Inventory Planning Formulas...")
    # Business Assumptions (Explicitly documented)
    LEAD_TIME_DAYS = 7 # Assumed supplier replenishment lead time = 7 calendar days
    
    # Target Service Levels & Z-scores (Standard Normal Distribution)
    # Class A: 95% Cycle Service Level (Z = 1.645 ~ 1.65)
    # Class B: 90% Cycle Service Level (Z = 1.282 ~ 1.28)
    # Class C: 90% Cycle Service Level (Z = 1.282 ~ 1.28)
    def get_service_level(abc):
        if abc == 'A':
            return 0.95, 1.65
        elif abc == 'B':
            return 0.90, 1.28
        else:
            return 0.90, 1.28

    sl_and_z = df_skus['abc_class'].apply(get_service_level)
    df_skus['target_service_level'] = [x[0] for x in sl_and_z]
    df_skus['z_score'] = [x[1] for x in sl_and_z]
    df_skus['lead_time_days'] = LEAD_TIME_DAYS

    # Formula 1: Lead-Time Demand (LTD) = Average Daily Demand * Lead Time
    df_skus['lead_time_demand'] = (df_skus['avg_daily_demand'] * df_skus['lead_time_days']).round(2)

    # Formula 2: Safety Stock (SS) = Z * Demand Standard Deviation * sqrt(Lead Time)
    df_skus['safety_stock'] = (df_skus['z_score'] * df_skus['std_daily_demand'] * np.sqrt(df_skus['lead_time_days'])).round(2)
    # Ceiling / integer rounding for practical store execution
    df_skus['safety_stock_units'] = np.ceil(df_skus['safety_stock']).astype(int)

    # Formula 3: Reorder Point (ROP) = Lead-Time Demand + Safety Stock
    df_skus['reorder_point'] = (df_skus['lead_time_demand'] + df_skus['safety_stock']).round(2)
    df_skus['reorder_point_units'] = np.ceil(df_skus['reorder_point']).astype(int)

    # Replenishment Policy & Review Frequency Recommendation
    def get_replenishment_action(row):
        segment = row['abc_xyz_segment']
        if segment in ['AX', 'AY']:
            return 'Continuous Review (Weekly Reorder Trigger) | High Service Level 95%'
        elif segment == 'AZ':
            return 'Bi-Weekly Review + Safety Buffer | Monitor Demand Spikes Closely'
        elif segment in ['BX', 'BY', 'BZ']:
            return 'Periodic Review (Bi-Weekly) | Standard Reorder Trigger'
        else:
            return 'Monthly Periodic Review / Minimum Batch Reorder | Avoid Excess Stock'

    df_skus['replenishment_policy'] = df_skus.apply(get_replenishment_action, axis=1)

    # Select clean inventory columns
    inv_cols = [
        'item_id', 'abc_class', 'xyz_class', 'abc_xyz_segment',
        'avg_daily_demand', 'std_daily_demand', 'cv_demand', 'avg_price',
        'lead_time_days', 'target_service_level', 'z_score',
        'lead_time_demand', 'safety_stock', 'safety_stock_units',
        'reorder_point', 'reorder_point_units', 'replenishment_policy'
    ]
    df_inv = df_skus[inv_cols].sort_values(by=['abc_class', 'avg_daily_demand'], ascending=[True, False]).reset_index(drop=True)

    # Save to CSV
    inv_out_path = os.path.join(output_dir, "inventory_planning_table.csv")
    df_inv.to_csv(inv_out_path, index=False)
    print(f"  -> Saved Inventory Planning Table to {inv_out_path}")

    # 3. Visualizations
    print("[3/3] Generating Safety Stock and ROP Visuals...")
    
    # Chart: Top 15 SKUs - Lead Time Demand vs Safety Stock vs ROP
    top15 = df_inv.head(15).copy()
    plt.figure(figsize=(10, 5.5), dpi=300)
    x = np.arange(len(top15))
    width = 0.55

    p1 = plt.bar(x, top15['lead_time_demand'], width, color='#3b82f6', label='Lead-Time Demand (LTD)', edgecolor='#1e293b')
    p2 = plt.bar(x, top15['safety_stock'], width, bottom=top15['lead_time_demand'], color='#f59e0b', label='Safety Stock (SS)', edgecolor='#1e293b')

    plt.title('Reorder Point (ROP) Breakdown for Top 15 Class A SKUs (Lead Time = 7 Days)', pad=15)
    plt.xlabel('SKU Identifier (Ranked by Demand)')
    plt.ylabel('Units (Demand Buffer)')
    plt.xticks(x, top15['item_id'], rotation=45, ha='right', fontsize=8.5)
    plt.legend(frameon=True, loc='upper right')
    plt.tight_layout()
    chart_path = os.path.join(chart_dir, "inventory_safety_stock_rop.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"  Saved visual to {chart_path}")

    # Print summary averages by ABC class
    print("\n--- Inventory Planning Summary by ABC Class ---")
    summary = df_inv.groupby('abc_class').agg(
        sku_count=('item_id', 'count'),
        avg_daily_demand=('avg_daily_demand', 'mean'),
        avg_lead_time_demand=('lead_time_demand', 'mean'),
        avg_safety_stock=('safety_stock', 'mean'),
        avg_reorder_point=('reorder_point', 'mean')
    ).round(2)
    print(summary.to_string())
    print("=" * 60)

if __name__ == '__main__':
    run_inventory_planning()
