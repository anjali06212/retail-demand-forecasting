import os
import pandas as pd
import numpy as np

def prepare_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(base_dir, "data_processed")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("PHASE 1: DATA PREPARATION & CLEANING")
    print("=" * 60)

    # 1. Load Calendar
    print("[1/4] Loading calendar metadata...")
    cal_path = os.path.join(data_dir, "calendar.csv")
    cal = pd.read_csv(cal_path)
    cal_cols = ['date', 'wm_yr_wk', 'weekday', 'wday', 'month', 'year', 'd', 
                'event_name_1', 'event_type_1', 'snap_CA']
    cal = cal[cal_cols].copy()
    cal['event_name_1'] = cal['event_name_1'].fillna('None')
    cal['event_type_1'] = cal['event_type_1'].fillna('None')
    cal['is_weekend'] = cal['wday'].apply(lambda x: 1 if x in [1, 2] else 0) # wday 1=Saturday, 2=Sunday in Walmart calendar
    cal['is_event'] = (cal['event_name_1'] != 'None').astype(int)
    print(f"  Loaded {len(cal)} calendar days ({cal['date'].min()} to {cal['date'].max()})")

    # 2. Load Sales for CA_1 Store & FOODS_1 Department
    print("[2/4] Loading and filtering sales data (Store: CA_1, Dept: FOODS_1)...")
    sales_path = os.path.join(data_dir, "sales_train_validation.csv")
    sales = pd.read_csv(sales_path)
    sales_subset = sales[(sales['store_id'] == 'CA_1') & (sales['dept_id'] == 'FOODS_1')].copy()
    print(f"  Selected {len(sales_subset)} SKUs in FOODS_1 for CA_1")

    # Melt from wide to long format
    id_vars = ['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id']
    day_cols = [c for c in sales_subset.columns if c.startswith('d_')]
    print(f"  Melting wide columns ({len(day_cols)} days) into long format...")
    sales_long = pd.melt(
        sales_subset,
        id_vars=id_vars,
        value_vars=day_cols,
        var_name='d',
        value_name='units_sold'
    )
    sales_long['units_sold'] = sales_long['units_sold'].astype(np.int32)
    print(f"  Long format created: {len(sales_long):,} records")

    # 3. Merge with Calendar
    print("[3/4] Merging with calendar metadata...")
    df_merged = sales_long.merge(cal, on='d', how='left')

    # 4. Merge with Sell Prices
    print("[4/4] Loading and merging weekly sell prices...")
    prices_path = os.path.join(data_dir, "sell_prices.csv")
    prices = pd.read_csv(prices_path)
    prices_subset = prices[(prices['store_id'] == 'CA_1') & (prices['item_id'].isin(sales_subset['item_id']))].copy()
    
    df_final = df_merged.merge(prices_subset, on=['store_id', 'item_id', 'wm_yr_wk'], how='left')

    # Handle items where price starts later by backfilling SKU average price
    avg_prices = prices_subset.groupby('item_id')['sell_price'].mean().to_dict()
    df_final['sell_price'] = df_final['sell_price'].fillna(df_final['item_id'].map(avg_prices))
    df_final['sell_price'] = df_final['sell_price'].round(2)
    
    # Calculate revenue
    df_final['revenue'] = (df_final['units_sold'] * df_final['sell_price']).round(2)

    # Sort chronologically by item and date
    df_final['date'] = pd.to_datetime(df_final['date'])
    df_final = df_final.sort_values(by=['item_id', 'date']).reset_index(drop=True)

    # Format date string for export
    df_final['date'] = df_final['date'].dt.strftime('%Y-%m-%d')

    # Select and order clean columns
    clean_cols = [
        'date', 'd', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id',
        'units_sold', 'sell_price', 'revenue',
        'weekday', 'wday', 'month', 'year', 'is_weekend',
        'event_name_1', 'event_type_1', 'is_event', 'snap_CA'
    ]
    df_final = df_final[clean_cols]

    # Save to CSV
    output_path = os.path.join(output_dir, "clean_retail_demand.csv")
    df_final.to_csv(output_path, index=False)
    print(f"\n[SUCCESS] Saved clean dataset to {output_path}")

    # Print summary metrics
    total_units = df_final['units_sold'].sum()
    total_rev = df_final['revenue'].sum()
    zero_demand_pct = (df_final['units_sold'] == 0).mean() * 100
    avg_price = df_final['sell_price'].mean()

    print("\n--- Clean Dataset Summary ---")
    print(f"Total Observations: {len(df_final):,}")
    print(f"Date Range:         {df_final['date'].min()} to {df_final['date'].max()} ({df_final['d'].nunique()} days)")
    print(f"Total Unique SKUs:  {df_final['item_id'].nunique()}")
    print(f"Total Units Sold:   {total_units:,}")
    print(f"Total Revenue:      ${total_rev:,.2f}")
    print(f"Average Unit Price: ${avg_price:.2f}")
    print(f"Zero-Demand Days:   {zero_demand_pct:.2f}% (Intermittent retail demand)")
    print("=" * 60)

if __name__ == '__main__':
    prepare_data()
