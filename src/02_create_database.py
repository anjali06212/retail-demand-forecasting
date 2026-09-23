import os
import sqlite3
import pandas as pd
import numpy as np

def create_database():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data_processed", "clean_retail_demand.csv")
    db_path = os.path.join(base_dir, "database", "retail_demand.db")
    schema_path = os.path.join(base_dir, "sql", "schema.sql")

    print("=" * 60)
    print("PHASE 2: SQLITE STAR SCHEMA DATABASE POPULATION")
    print("=" * 60)

    # 1. Read clean dataset
    print(f"[1/4] Reading clean processed dataset: {data_path}")
    df = pd.read_csv(data_path, keep_default_na=False)
    df['date_dt'] = pd.to_datetime(df['date'])
    df['date_key'] = df['date_dt'].dt.strftime('%Y%m%d').astype(int)

    # 2. Connect to SQLite & initialize schema
    print(f"[2/4] Initializing database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()

    # 3. Populate Dimension Tables
    print("[3/4] Populating Dimension Tables (dim_date, dim_product, dim_store)...")

    # Dim Date
    dim_date = df[['date_key', 'date', 'd', 'weekday', 'wday', 'month', 'year',
                   'is_weekend', 'event_name_1', 'event_type_1', 'is_event', 'snap_CA']].drop_duplicates().copy()
    dim_date['month_name'] = pd.to_datetime(dim_date['date']).dt.strftime('%B')
    dim_date = dim_date.rename(columns={
        'weekday': 'day_name',
        'wday': 'day_of_week',
        'event_name_1': 'event_name',
        'event_type_1': 'event_type',
        'snap_CA': 'snap_flag'
    })
    dim_date['event_name'] = dim_date['event_name'].replace('', 'None')
    dim_date['event_type'] = dim_date['event_type'].replace('', 'None')
    date_cols = ['date_key', 'date', 'd', 'day_name', 'day_of_week', 'month', 'month_name',
                 'year', 'is_weekend', 'event_name', 'event_type', 'is_event', 'snap_flag']
    dim_date = dim_date[date_cols].sort_values(by='date_key')
    dim_date.to_sql('dim_date', conn, if_exists='append', index=False)
    print(f"  -> Inserted {len(dim_date)} rows into dim_date")

    # Dim Product
    prod_agg = df.groupby(['item_id', 'dept_id', 'cat_id'])['sell_price'].agg(
        avg_price='mean', min_price='min', max_price='max'
    ).reset_index()
    prod_agg['avg_price'] = prod_agg['avg_price'].round(2)
    prod_agg.to_sql('dim_product', conn, if_exists='append', index=False)
    print(f"  -> Inserted {len(prod_agg)} rows into dim_product")

    # Dim Store (Clean dataset-supported naming: Store CA_1)
    dim_store = pd.DataFrame([{
        'store_id': 'CA_1',
        'state_id': 'CA',
        'store_name': 'Store CA_1'
    }])
    dim_store.to_sql('dim_store', conn, if_exists='append', index=False)
    print(f"  -> Inserted {len(dim_store)} rows into dim_store")

    # 4. Populate Fact Table
    print("[4/4] Populating Fact Table (fact_daily_sales)...")
    fact_sales = df[['date_key', 'item_id', 'store_id', 'units_sold', 'sell_price', 'revenue']].copy()
    fact_sales['is_zero_demand'] = (fact_sales['units_sold'] == 0).astype(int)

    fact_sales.to_sql('fact_daily_sales', conn, if_exists='append', index=False, chunksize=50000)
    print(f"  -> Inserted {len(fact_sales):,} rows into fact_daily_sales")

    # Verify counts
    cursor.execute("SELECT COUNT(*) FROM fact_daily_sales")
    fact_count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(units_sold), ROUND(SUM(revenue), 2) FROM fact_daily_sales")
    total_u, total_r = cursor.fetchone()

    conn.close()

    print("\n[SUCCESS] SQLite Star Schema Database Created Successfully!")
    print(f"Fact Table Records: {fact_count:,}")
    print(f"Total Units in DB:  {total_u:,}")
    print(f"Total Revenue in DB: ${total_r:,.2f}")
    print("=" * 60)

if __name__ == '__main__':
    create_database()
