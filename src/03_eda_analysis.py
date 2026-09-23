import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set clean aesthetic styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'

def run_eda():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data_processed", "clean_retail_demand.csv")
    chart_dir = os.path.join(base_dir, "outputs", "charts")
    os.makedirs(chart_dir, exist_ok=True)

    print("=" * 60)
    print("PHASE 4: EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 60)

    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])

    # 1. Daily Aggregation
    daily = df.groupby('date').agg(
        total_units=('units_sold', 'sum'),
        total_revenue=('revenue', 'sum')
    ).reset_index()
    daily['rolling_28d'] = daily['total_units'].rolling(window=28, min_periods=7).mean()

    # Chart 1: Daily Demand Trend & 28-Day Moving Average
    print("[1/4] Generating Chart: Overall Demand Trend...")
    plt.figure(figsize=(12, 5), dpi=300)
    plt.plot(daily['date'], daily['total_units'], color='#94a3b8', alpha=0.5, linewidth=0.8, label='Daily Units Sold')
    plt.plot(daily['date'], daily['rolling_28d'], color='#2563eb', linewidth=2.2, label='28-Day Moving Average (Trend)')
    plt.title('Daily Retail Demand & 28-Day Moving Average Trend (FOODS_1 @ CA_1)', pad=15)
    plt.xlabel('Date')
    plt.ylabel('Total Units Sold / Day')
    plt.legend(frameon=True, loc='upper left')
    plt.tight_layout()
    chart1_path = os.path.join(chart_dir, "eda_overall_demand_trend.png")
    plt.savefig(chart1_path)
    plt.close()
    print(f"  Saved to {chart1_path}")

    # Chart 2: Day of Week Seasonality
    print("[2/4] Generating Chart: Day-of-Week Seasonality...")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow = df.groupby(['date', 'weekday'])['units_sold'].sum().reset_index()
    dow_avg = dow.groupby('weekday')['units_sold'].mean().reindex(day_order)

    plt.figure(figsize=(8, 4.5), dpi=300)
    colors = ['#64748b' if d not in ['Saturday', 'Sunday'] else '#3b82f6' for d in day_order]
    bars = plt.bar(day_order, dow_avg, color=colors, edgecolor='#1e293b', width=0.6)
    plt.title('Average Daily Demand by Day of Week (Weekend Lift Effect)', pad=15)
    plt.xlabel('Day of Week')
    plt.ylabel('Average Total Units Sold / Day')
    
    # Add value labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 5, f"{yval:.1f}", ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.ylim(0, max(dow_avg) * 1.15)
    plt.tight_layout()
    chart2_path = os.path.join(chart_dir, "eda_day_of_week_seasonality.png")
    plt.savefig(chart2_path)
    plt.close()
    print(f"  Saved to {chart2_path}")

    # Chart 3: Zero-Demand Distribution (Intermittent Demand Analysis)
    print("[3/4] Generating Chart: Intermittent Demand & Zero-Demand Distribution...")
    sku_zero = df.groupby('item_id')['units_sold'].apply(lambda s: (s == 0).mean() * 100)

    plt.figure(figsize=(8, 4.5), dpi=300)
    n, bins, patches = plt.hist(sku_zero, bins=20, color='#0ea5e9', edgecolor='#0369a1', alpha=0.85)
    plt.axvline(sku_zero.median(), color='#ef4444', linestyle='--', linewidth=1.8, label=f'Median Zero-Demand % ({sku_zero.median():.1f}%)')
    plt.title('Distribution of Zero-Demand Days Across SKUs (Intermittency)', pad=15)
    plt.xlabel('Zero-Demand Days (% of Total Tracked Days)')
    plt.ylabel('Number of SKUs')
    plt.legend(frameon=True, loc='upper left')
    plt.tight_layout()
    chart3_path = os.path.join(chart_dir, "eda_intermittent_zero_demand.png")
    plt.savefig(chart3_path)
    plt.close()
    print(f"  Saved to {chart3_path}")

    # Chart 4: Monthly Seasonality
    print("[4/4] Generating Chart: Monthly Seasonality...")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly = df.groupby(['date', 'month'])['units_sold'].sum().reset_index()
    monthly_avg = monthly.groupby('month')['units_sold'].mean()

    plt.figure(figsize=(9, 4.5), dpi=300)
    plt.plot(month_names, monthly_avg, marker='o', color='#10b981', linewidth=2.2, markersize=6)
    plt.fill_between(month_names, monthly_avg, color='#10b981', alpha=0.15)
    plt.title('Average Daily Demand by Calendar Month (Seasonal Patterns)', pad=15)
    plt.xlabel('Month')
    plt.ylabel('Average Daily Units Sold')
    for i, txt in enumerate(monthly_avg):
        plt.annotate(f"{txt:.1f}", (month_names[i], txt + 3), ha='center', fontsize=8.5, fontweight='bold')
    plt.ylim(min(monthly_avg) * 0.9, max(monthly_avg) * 1.1)
    plt.tight_layout()
    chart4_path = os.path.join(chart_dir, "eda_monthly_seasonality.png")
    plt.savefig(chart4_path)
    plt.close()
    print(f"  Saved to {chart4_path}")

    print("\n[SUCCESS] All 4 EDA Charts Generated Successfully!")
    print("=" * 60)

if __name__ == '__main__':
    run_eda()
