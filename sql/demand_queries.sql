-- ====================================================================
-- RETAIL DEMAND FORECASTING & INVENTORY PLANNING: SQL ANALYTICS SUITE
-- Database: database/retail_demand.db
-- Purpose: Practical, interview-defensible SQL queries for Demand Planning
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: High-Level Executive Demand & Financial KPIs
-- Demonstrates: Basic Aggregations, ROUND, COUNT DISTINCT
-- --------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT f.item_id) AS total_skus,
    COUNT(DISTINCT f.date_key) AS total_days,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.units_sold) * 1.0 / COUNT(DISTINCT f.date_key), 2) AS avg_daily_units_all_skus,
    ROUND(SUM(f.revenue) / COUNT(DISTINCT f.date_key), 2) AS avg_daily_revenue,
    ROUND(AVG(f.sell_price), 2) AS avg_unit_price
FROM fact_daily_sales f;


-- --------------------------------------------------------------------
-- QUERY 2: Top 10 Best-Selling SKUs by Revenue and Unit Volume
-- Demonstrates: JOIN, GROUP BY, ORDER BY, LIMIT, Revenue Ranking
-- --------------------------------------------------------------------
SELECT 
    f.item_id,
    p.dept_id,
    p.cat_id,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(AVG(f.units_sold), 2) AS avg_daily_units,
    ROUND(p.avg_price, 2) AS avg_price
FROM fact_daily_sales f
JOIN dim_product p ON f.item_id = p.item_id
GROUP BY f.item_id, p.dept_id, p.cat_id, p.avg_price
ORDER BY total_revenue DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 3: Monthly & Yearly Demand Trend Analysis
-- Demonstrates: Multi-table JOIN, Date grouping, Seasonality identification
-- --------------------------------------------------------------------
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT d.date_key) AS days_in_month,
    SUM(f.units_sold) AS monthly_units_sold,
    ROUND(SUM(f.revenue), 2) AS monthly_revenue,
    ROUND(SUM(f.units_sold) * 1.0 / COUNT(DISTINCT d.date_key), 2) AS avg_daily_demand
FROM fact_daily_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- --------------------------------------------------------------------
-- QUERY 4: Day-of-Week Seasonality & Weekend Sales Lift
-- Demonstrates: CASE Statement, Aggregations, Weekend vs. Weekday demand
-- --------------------------------------------------------------------
SELECT 
    d.day_name,
    d.day_of_week,
    CASE WHEN d.is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_category,
    SUM(f.units_sold) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(AVG(daily_agg.day_units), 2) AS avg_units_per_day
FROM dim_date d
JOIN fact_daily_sales f ON d.date_key = f.date_key
JOIN (
    -- Subquery: Total units sold across all items per day
    SELECT date_key, SUM(units_sold) AS day_units
    FROM fact_daily_sales
    GROUP BY date_key
) daily_agg ON d.date_key = daily_agg.date_key
GROUP BY d.day_name, d.day_of_week, d.is_weekend
ORDER BY d.day_of_week;


-- --------------------------------------------------------------------
-- QUERY 5: Promotional / Holiday Event Demand Lift Analysis
-- Demonstrates: Conditional Aggregation (CASE), Demand Uplift Calculation
-- --------------------------------------------------------------------
SELECT 
    CASE WHEN d.is_event = 1 THEN 'Holiday / Special Event Day' ELSE 'Regular Day' END AS day_type,
    COUNT(DISTINCT d.date_key) AS total_days_count,
    SUM(f.units_sold) AS total_units,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.units_sold) * 1.0 / COUNT(DISTINCT d.date_key), 2) AS avg_units_per_day,
    ROUND(SUM(f.revenue) / COUNT(DISTINCT d.date_key), 2) AS avg_revenue_per_day
FROM fact_daily_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY CASE WHEN d.is_event = 1 THEN 'Holiday / Special Event Day' ELSE 'Regular Day' END;


-- --------------------------------------------------------------------
-- QUERY 6: 7-Day and 28-Day Rolling Moving Averages for Demand Smoothing
-- Demonstrates: SQL Window Functions (AVG OVER ROWS BETWEEN PRECEDING)
-- --------------------------------------------------------------------
WITH daily_item_sales AS (
    SELECT 
        f.item_id,
        d.date,
        f.date_key,
        f.units_sold
    FROM fact_daily_sales f
    JOIN dim_date d ON f.date_key = d.date_key
)
SELECT 
    item_id,
    date,
    units_sold,
    ROUND(AVG(units_sold) OVER (
        PARTITION BY item_id 
        ORDER BY date_key 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7d_avg_demand,
    ROUND(AVG(units_sold) OVER (
        PARTITION BY item_id 
        ORDER BY date_key 
        ROWS BETWEEN 27 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_28d_avg_demand
FROM daily_item_sales
WHERE item_id = 'FOODS_1_001'
ORDER BY date_key DESC
LIMIT 30;


-- --------------------------------------------------------------------
-- QUERY 7: Day-over-Day Demand Velocity & Acceleration using LAG()
-- Demonstrates: Window Function LAG() for Demand Shock Detection
-- --------------------------------------------------------------------
WITH department_daily_sales AS (
    SELECT 
        d.date,
        d.date_key,
        SUM(f.units_sold) AS total_dept_units
    FROM fact_daily_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.date, d.date_key
)
SELECT 
    date,
    total_dept_units,
    LAG(total_dept_units, 1) OVER (ORDER BY date_key) AS previous_day_units,
    (total_dept_units - LAG(total_dept_units, 1) OVER (ORDER BY date_key)) AS day_over_day_change,
    ROUND(
        (total_dept_units - LAG(total_dept_units, 1) OVER (ORDER BY date_key)) * 100.0 / 
        NULLIF(LAG(total_dept_units, 1) OVER (ORDER BY date_key), 0), 
        2
    ) AS pct_growth
FROM department_daily_sales
ORDER BY date_key DESC
LIMIT 20;


-- --------------------------------------------------------------------
-- QUERY 8: Intermittent Demand & Zero-Demand Days Analysis
-- Demonstrates: Zero-sales percentage calculation per SKU
-- --------------------------------------------------------------------
SELECT 
    f.item_id,
    COUNT(*) AS total_tracked_days,
    SUM(CASE WHEN f.units_sold = 0 THEN 1 ELSE 0 END) AS zero_demand_days,
    SUM(CASE WHEN f.units_sold > 0 THEN 1 ELSE 0 END) AS positive_demand_days,
    ROUND(SUM(CASE WHEN f.units_sold = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS zero_demand_pct,
    ROUND(AVG(f.units_sold), 2) AS avg_daily_demand,
    ROUND(MAX(f.units_sold), 0) AS max_single_day_demand
FROM fact_daily_sales f
GROUP BY f.item_id
ORDER BY zero_demand_pct DESC
LIMIT 15;


-- --------------------------------------------------------------------
-- QUERY 9: ABC Revenue Classification (Pareto 80/15/5 Rule) in pure SQL
-- Demonstrates: Multi-CTE, Window SUM OVER, Cumulative Percentage, CASE
-- --------------------------------------------------------------------
WITH sku_revenue AS (
    SELECT 
        item_id,
        SUM(revenue) AS sku_total_rev,
        SUM(units_sold) AS sku_total_units
    FROM fact_daily_sales
    GROUP BY item_id
),
revenue_ranked AS (
    SELECT 
        item_id,
        sku_total_rev,
        sku_total_units,
        SUM(sku_total_rev) OVER (ORDER BY sku_total_rev DESC) AS running_cumulative_rev,
        SUM(sku_total_rev) OVER () AS grand_total_rev
    FROM sku_revenue
),
abc_classified AS (
    SELECT 
        item_id,
        ROUND(sku_total_rev, 2) AS total_revenue,
        sku_total_units AS total_units,
        ROUND((running_cumulative_rev * 100.0 / grand_total_rev), 2) AS cumulative_rev_pct,
        CASE 
            WHEN (running_cumulative_rev * 1.0 / grand_total_rev) <= 0.80 THEN 'A'
            WHEN (running_cumulative_rev * 1.0 / grand_total_rev) <= 0.95 THEN 'B'
            ELSE 'C'
        END AS abc_category
    FROM revenue_ranked
)
SELECT 
    abc_category,
    COUNT(item_id) AS sku_count,
    ROUND(COUNT(item_id) * 100.0 / (SELECT COUNT(*) FROM dim_product), 2) AS sku_pct,
    ROUND(SUM(total_revenue), 2) AS category_revenue,
    ROUND(SUM(total_revenue) * 100.0 / (SELECT SUM(revenue) FROM fact_daily_sales), 2) AS rev_contribution_pct
FROM abc_classified
GROUP BY abc_category
ORDER BY abc_category;
