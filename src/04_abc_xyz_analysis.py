import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_abc_xyz_analysis():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data_processed", "clean_retail_demand.csv")
    output_dir = os.path.join(base_dir, "outputs")
    chart_dir = os.path.join(output_dir, "charts")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(chart_dir, exist_ok=True)

    print("=" * 60)
    print("PHASE 5: ABC-XYZ DEMAND SEGMENTATION")
    print("=" * 60)

    df = pd.read_csv(data_path)

    # 1. Calculate SKU-level Demand Statistics
    print("[1/4] Calculating SKU demand and revenue statistics...")
    sku_stats = df.groupby('item_id').agg(
        total_units=('units_sold', 'sum'),
        total_revenue=('revenue', 'sum'),
        avg_daily_demand=('units_sold', 'mean'),
        std_daily_demand=('units_sold', 'std'),
        avg_price=('sell_price', 'mean'),
        total_days=('date', 'count'),
        zero_days=('units_sold', lambda s: (s == 0).sum())
    ).reset_index()

    sku_stats['zero_demand_pct'] = (sku_stats['zero_days'] / sku_stats['total_days'] * 100).round(2)
    sku_stats['avg_daily_demand'] = sku_stats['avg_daily_demand'].round(4)
    sku_stats['std_daily_demand'] = sku_stats['std_daily_demand'].fillna(0).round(4)
    sku_stats['avg_price'] = sku_stats['avg_price'].round(2)
    sku_stats['total_revenue'] = sku_stats['total_revenue'].round(2)

    # 2. ABC Classification (Pareto Revenue Contribution)
    print("[2/4] Performing ABC Classification (Pareto 80/15/5)...")
    sku_stats = sku_stats.sort_values(by='total_revenue', ascending=False).reset_index(drop=True)
    sku_stats['cumulative_revenue'] = sku_stats['total_revenue'].cumsum()
    grand_total_rev = sku_stats['total_revenue'].sum()
    sku_stats['cumulative_rev_pct'] = (sku_stats['cumulative_revenue'] / grand_total_rev * 100).round(2)

    def classify_abc(cum_pct):
        if cum_pct <= 80.0:
            return 'A'
        elif cum_pct <= 95.0:
            return 'B'
        else:
            return 'C'

    sku_stats['abc_class'] = sku_stats['cumulative_rev_pct'].apply(classify_abc)

    # 3. XYZ Classification (Demand Predictability via Coefficient of Variation)
    print("[3/4] Performing XYZ Classification (Coefficient of Variation CV = std / mean)...")
    sku_stats['cv_demand'] = (sku_stats['std_daily_demand'] / np.where(sku_stats['avg_daily_demand'] > 0, sku_stats['avg_daily_demand'], np.nan)).round(4)
    sku_stats['cv_demand'] = sku_stats['cv_demand'].fillna(99.0) # High CV for 0 demand items

    def classify_xyz(cv):
        if cv <= 0.50:
            return 'X' # Low variability, steady demand
        elif cv <= 1.00:
            return 'Y' # Moderate variability, seasonal
        else:
            return 'Z' # High variability, erratic / lumpy

    sku_stats['xyz_class'] = sku_stats['cv_demand'].apply(classify_xyz)
    sku_stats['abc_xyz_segment'] = sku_stats['abc_class'] + sku_stats['xyz_class']

    # Strategy Mapping
    strategies = {
        'AX': 'Continuous Auto-Replenishment | High Service Level (98%) | Minimal Safety Stock Buffer',
        'AY': 'Seasonal Forecasting | Medium Safety Stock Buffer | Weekly Demand Review',
        'AZ': 'Dedicated Planner Review | Dynamic Safety Stock | Close Supplier Lead Time Tracking',
        'BX': 'Standard Periodic Replenishment | Medium Service Level (92%) | Low Safety Stock',
        'BY': 'Standard Replenishment | Moderate Safety Stock | Bi-weekly Review',
        'BZ': 'Responsive Reorder | Buffer against Demand Spikes | Strict Minimum Order Quantity',
        'CX': 'Automated Simple Reorder | Low Service Level (85-90%) | Bulk Order / Low Review Frequency',
        'CY': 'Order on Demand | Minimal Safety Stock | Avoid Overstock Holding Costs',
        'CZ': 'Make-to-Order / Rationalization Candidate | Zero/Near-Zero Safety Stock'
    }
    sku_stats['replenishment_strategy'] = sku_stats['abc_xyz_segment'].map(strategies)

    # Save SKU-level classification table
    sku_out_path = os.path.join(output_dir, "abc_xyz_sku_classification.csv")
    sku_stats.to_csv(sku_out_path, index=False)
    print(f"  -> Saved SKU Classification to {sku_out_path}")

    # Summary 9-Box Matrix Pivot
    summary_matrix = sku_stats.groupby(['abc_class', 'xyz_class']).agg(
        sku_count=('item_id', 'count'),
        total_revenue=('total_revenue', 'sum'),
        total_units=('total_units', 'sum'),
        avg_cv=('cv_demand', 'mean')
    ).reset_index()
    summary_matrix['rev_pct'] = (summary_matrix['total_revenue'] / grand_total_rev * 100).round(2)
    summary_matrix['avg_cv'] = summary_matrix['avg_cv'].round(2)

    matrix_out_path = os.path.join(output_dir, "abc_xyz_summary_matrix.csv")
    summary_matrix.to_csv(matrix_out_path, index=False)
    print(f"  -> Saved 9-Box Summary to {matrix_out_path}")

    # 4. Generate Visualizations
    print("[4/4] Generating Pareto Curve and 9-Box Matrix Charts...")
    
    # Chart 1: ABC Pareto Curve
    plt.figure(figsize=(9, 5), dpi=300)
    sku_rank = np.arange(1, len(sku_stats) + 1)
    sku_pct = sku_rank / len(sku_stats) * 100
    
    plt.plot(sku_pct, sku_stats['cumulative_rev_pct'], color='#2563eb', linewidth=2.5, label='Cumulative Revenue %')
    plt.axhline(80, color='#16a34a', linestyle='--', linewidth=1.2, label='80% Revenue Threshold (Class A)')
    plt.axhline(95, color='#ca8a04', linestyle='--', linewidth=1.2, label='95% Revenue Threshold (Class B)')
    plt.title('ABC Pareto Revenue Concentration Curve (FOODS_1 @ CA_1)', pad=15)
    plt.xlabel('% of Total SKUs (Ranked by Revenue)')
    plt.ylabel('Cumulative Revenue %')
    plt.legend(frameon=True, loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    pareto_path = os.path.join(chart_dir, "abc_pareto_curve.png")
    plt.savefig(pareto_path)
    plt.close()

    # Chart 2: 9-Box Heatmap Table Visual
    pivot_count = pd.pivot_table(sku_stats, index='abc_class', columns='xyz_class', values='item_id', aggfunc='count', fill_value=0)
    pivot_rev = pd.pivot_table(sku_stats, index='abc_class', columns='xyz_class', values='total_revenue', aggfunc='sum', fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    ax.axis('off')
    
    table_data = []
    headers = ['ABC Class', 'X (CV <= 0.50)\nSteady Demand', 'Y (0.50 < CV <= 1.0)\nSeasonal Demand', 'Z (CV > 1.0)\nErratic Demand', 'Total SKUs']
    
    for abc in ['A', 'B', 'C']:
        row = [f"Class {abc}"]
        for xyz in ['X', 'Y', 'Z']:
            cnt = pivot_count.loc[abc, xyz] if (abc in pivot_count.index and xyz in pivot_count.columns) else 0
            rev = pivot_rev.loc[abc, xyz] if (abc in pivot_rev.index and xyz in pivot_rev.columns) else 0
            row.append(f"{cnt} SKUs\n(${rev:,.0f})")
        row.append(f"{sku_stats[sku_stats['abc_class'] == abc]['item_id'].count()} SKUs")
        table_data.append(row)
    
    table = ax.table(cellText=table_data, colLabels=headers, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2.5)

    # Style header row
    for col in range(len(headers)):
        table[(0, col)].set_facecolor('#1e293b')
        table[(0, col)].set_text_props(color='white', weight='bold')

    # Color code cells
    color_map = {
        (1, 1): '#dcfce7', (1, 2): '#fef9c3', (1, 3): '#fee2e2', # A row
        (2, 1): '#f0fdf4', (2, 2): '#fefce8', (2, 3): '#fff1f2', # B row
        (3, 1): '#f8fafc', (3, 2): '#f8fafc', (3, 3): '#f1f5f9'  # C row
    }
    for pos, col in color_map.items():
        if pos in table._cells:
            table[pos].set_facecolor(col)

    plt.title('ABC-XYZ Demand Segmentation Matrix (9-Box Summary)', fontsize=13, weight='bold', pad=20)
    plt.tight_layout()
    matrix_path = os.path.join(chart_dir, "abc_xyz_9box_matrix.png")
    plt.savefig(matrix_path, bbox_inches='tight')
    plt.close()

    # Print summary breakdown
    print("\n--- ABC-XYZ Segmentation Summary ---")
    print(summary_matrix.to_string(index=False))
    print("=" * 60)

if __name__ == '__main__':
    run_abc_xyz_analysis()
