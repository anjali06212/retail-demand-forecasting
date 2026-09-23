-- ============================================================
-- Star Schema Database Definition for Retail Demand Planning
-- Database: SQLite (database/retail_demand.db)
-- ============================================================

-- Drop tables if they already exist
DROP TABLE IF EXISTS fact_daily_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_store;

-- 1. Date Dimension
CREATE TABLE dim_date (
    date_key        INTEGER PRIMARY KEY,  -- Format: YYYYMMDD
    date            TEXT NOT NULL UNIQUE, -- Format: YYYY-MM-DD
    d               TEXT NOT NULL,        -- Format: d_1 .. d_1913
    day_name        TEXT NOT NULL,        -- Monday .. Sunday
    day_of_week     INTEGER NOT NULL,     -- 1 (Saturday) .. 7 (Friday)
    month           INTEGER NOT NULL,     -- 1 .. 12
    month_name      TEXT NOT NULL,        -- January .. December
    year            INTEGER NOT NULL,     -- 2011 .. 2016
    is_weekend      INTEGER NOT NULL,     -- 1 if Sat/Sun else 0
    event_name      TEXT NOT NULL,        -- Event name or 'None'
    event_type      TEXT NOT NULL,        -- Event type or 'None'
    is_event        INTEGER NOT NULL,     -- 1 if holiday/event else 0
    snap_flag       INTEGER NOT NULL      -- 1 if SNAP day in CA else 0
);

-- 2. Product Dimension
CREATE TABLE dim_product (
    item_id         TEXT PRIMARY KEY,     -- Unique SKU identifier
    dept_id         TEXT NOT NULL,        -- Department (FOODS_1)
    cat_id          TEXT NOT NULL,        -- Category (FOODS)
    avg_price       REAL NOT NULL,        -- Average retail price
    min_price       REAL NOT NULL,        -- Minimum historic price
    max_price       REAL NOT NULL         -- Maximum historic price
);

-- 3. Store Dimension
CREATE TABLE dim_store (
    store_id        TEXT PRIMARY KEY,     -- Store identifier (CA_1)
    state_id        TEXT NOT NULL,        -- State (CA)
    store_name      TEXT NOT NULL         -- Descriptive name
);

-- 4. Fact Daily Sales Table
CREATE TABLE fact_daily_sales (
    sales_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key        INTEGER NOT NULL,
    item_id         TEXT NOT NULL,
    store_id        TEXT NOT NULL,
    units_sold      INTEGER NOT NULL,
    sell_price      REAL NOT NULL,
    revenue         REAL NOT NULL,
    is_zero_demand  INTEGER NOT NULL,     -- 1 if zero units sold, 0 if demand > 0
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (item_id) REFERENCES dim_product(item_id),
    FOREIGN KEY (store_id) REFERENCES dim_store(store_id)
);

-- Performance Indexes for Analytical Queries
CREATE INDEX idx_fact_date ON fact_daily_sales(date_key);
CREATE INDEX idx_fact_item ON fact_daily_sales(item_id);
CREATE INDEX idx_fact_item_date ON fact_daily_sales(item_id, date_key);
