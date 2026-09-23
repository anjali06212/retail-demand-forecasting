# Retail Demand Forecasting & Inventory Planning

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Star_Schema-green.svg)](https://www.sqlite.org/)
[![Excel](https://img.shields.io/badge/Excel-Dynamic_Formulas-success.svg)](https://products.office.com/excel)

An end-to-end, interview-defensible data analytics and demand planning portfolio project. Mined and analyzed 5.2 years of daily retail point-of-sale data from the Walmart M5 Forecasting benchmark to build a structured demand analysis pipeline, SQLite star schema database, ABC-XYZ SKU segmentation, explainable time-series forecasting models, basic inventory replenishment parameters, and a multi-tab Microsoft Excel planning workbook with live dynamic formulas.

---

## 📌 Project Architecture

```text
Raw Walmart M5 Data (calendar.csv, sales_train_validation.csv, sell_prices.csv)
        ↓
Python Data Preparation (Wide-to-Long Melting, Calendar & Pricing Merges)
        ↓
Clean Tidy Demand Dataset (clean_retail_demand.csv - 413,208 records)
        ↓
SQLite Database / Star Schema (dim_date, dim_product, dim_store, fact_daily_sales)
        ↓
SQL Demand Analytics (CTEs, Window Functions, Rolling Means, Seasonality, LAG)
        ↓
Exploratory Data Analysis (Overall Trend, Day-of-Week Lift, Intermittency)
        ↓
ABC-XYZ Demand Segmentation (Pareto 80/15/5 Value & Coefficient of Variation)
        ↓
Explainable Demand Forecasting (Naive, 7-Day SMA, 28-Day SMA, Holt-Winters)
        ↓
Forecast Evaluation (28-Day Holdout: MAE, RMSE, WAPE %, Forecast Bias %)
        ↓
Basic Inventory Planning (Lead-Time Demand, Safety Stock, Reorder Point)
        ↓
Excel Demand Planning Workbook (Multi-Tab Model with Live Formulas)
        ↓
Business Insights
```

1. 🏢 Business Problem
In retail supply chains, stockouts can lead to lost revenue and customer dissatisfaction, while excess inventory can tie up working capital. Balancing service levels and inventory buffers requires translating historical point-of-sale data into actionable demand forecasts, SKU-level prioritization, and calculated reorder triggers.

3. 🎯 Why Demand Planning?
Demand planning connects sales data with procurement decisions. Rather than relying on static ordering rules or opaque black-box machine learning, supply chain planners can use structured demand segmentation such as ABC-XYZ analysis and explainable time-series baselines to establish defensible safety stock levels and reorder points.

5. 📂 Dataset
This project uses the Walmart M5 Forecasting benchmark dataset:
- calendar.csv: Contains calendar dates, day of week, month, year, event/holiday names, and state SNAP assistance flags.
- sales_train_validation.csv: Contains historical daily unit sales quantities across products and stores (d_1 to d_1913).
- sell_prices.csv: Contains weekly store-item selling prices (wm_yr_wk, sell_price).
- 
4. 🔍 Project Scope
To maintain complete analytical depth while keeping data processing fast and transparent across Python, SQLite, and Excel:
- Store: CA_1
- Department: FOODS_1
- Products: 216 unique SKUs
- Historical Horizon: 1,913 consecutive days (January 29, 2011 to April 24, 2016 / ~5.2 years)
- Total Observation Grid: 413,208 SKU-day records (216 × 1,913, with zero missing SKU-date combinations)
- 
5. 🛠️ Tools & Technologies
- Python (3.11): pandas for data wrangling, numpy for mathematical calculations, statsmodels for time-series modeling, openpyxl for Excel workbook generation, matplotlib for charts.
- SQL (SQLite): Dimensional star schema design, table DDL, aggregations, window functions (AVG() OVER), LAG(), CTEs.
- Microsoft Excel: Multi-tab analytical planning workbook, formatted KPI cards, conditional formatting, and dynamic live formulas (ROUND, SQRT).
- 
6. 🧹 Data Preparation & Cleaning
Implemented in src/01_data_preparation.py.
- Filtered raw data for Store CA_1 and Department FOODS_1.
- Reshaped wide daily sales columns (d_1..d_1913) into tidy long format: (date, item_id, store_id, units_sold).
- Merged with calendar.csv on day index d to attach day name, month, year, event flags, and SNAP indicators.
- Merged with sell_prices.csv on (store_id, item_id, wm_yr_wk) to calculate revenue = units_sold * sell_price.
- Saved output to data_processed/clean_retail_demand.csv.

- 7. 🗄️ SQL Star Schema & Demand Analytics
Database:
database/retail_demand.db
Star Schema Architecture
- dim_date: date_key (PK), date, day_name, day_of_week, month, month_name, year, is_weekend, event_name, event_type, is_event, snap_flag.
- dim_product: item_id (PK), dept_id, cat_id, avg_price, min_price, max_price.
- dim_store: store_id (PK), state_id, store_name (Store CA_1).
- fact_daily_sales: sales_id (PK), date_key (FK), item_id (FK), store_id (FK), units_sold, sell_price, revenue, is_zero_demand.
Key SQL Analytics Demonstrated
Implemented in sql/demand_queries.sql:
1. Executive Demand KPIs: Aggregations across units sold, revenue, and active SKUs.
2. Top / Bottom SKU Rankings: Product revenue and volume rankings.
3. Monthly & Yearly Trends: Historical sales volume and seasonality.
4. Day-of-Week Seasonality: Quantifying weekend demand lift (+46% on Saturdays vs. weekdays).
5. Promotional / Event Day Lift: Comparing holiday/event days against regular baseline days.
6. Rolling Moving Averages: 7-day and 28-day window smoothing (AVG() OVER (ROWS BETWEEN ... PRECEDING)).
7. Day-over-Day Demand Acceleration: Measuring daily velocity using LAG().
8. Intermittent Demand Analysis: Zero-demand day percentage per SKU.
9. Pure SQL ABC Classification: Cumulative revenue contribution via CTEs and window sums.
    
8. 📊 Exploratory Data Analysis
Implemented in src/03_eda_analysis.py.
Key findings visualized in outputs/charts/:
- Weekend Peak: Demand spikes significantly on Saturday (average 381.2 units/day) and Sunday (330.8 units/day) compared to Monday–Friday (261.3 units/day).
- Intermittent Demand: 59.29% of daily SKU-level records have zero units sold, illustrating the high intermittency observed in the selected dataset scope.
- Annual Seasonality: Demand shows consistent mid-year peaks and end-of-year holiday shifts.
  
9. 📦 ABC-XYZ Demand Segmentation
Implemented in src/04_abc_xyz_analysis.py.
All 216 SKUs were categorized across two complementary dimensions.
A. ABC Analysis: Pareto Revenue Contribution
- Class A (Top 80% Revenue): 109 SKUs (50.5% of items) generate 79.7% of total revenue ($1,038,843).
- Class B (80% – 95% Revenue): 62 SKUs (28.7% of items) generate 15.3% of total revenue ($199,242).
- Class C (95% – 100% Revenue): 45 SKUs (20.8% of items) generate 5.0% of total revenue ($65,344).
B. XYZ Analysis: Demand Predictability via Coefficient of Variation
CV = Standard Deviation of Daily Demand / Mean Daily Demand

- Class X (CV ≤ 0.50): 0 SKUs.
- Class Y (0.50 < CV ≤ 1.00): 9 SKUs.
- Class Z (CV > 1.00): 207 SKUs.
The strong concentration in Class Z reflects the high variability and intermittency observed in the selected SKU-level demand data.
C. 9-Box Policy Matrix
The ABC-XYZ matrix is used to organize SKUs according to revenue contribution and demand variability:
- AY: High value, seasonal demand → closer review and seasonal forecasting.
- AZ: High value, highly variable demand → closer planner review and appropriate safety buffers.
- BZ: Moderate value, highly variable demand → standard review and buffering approach.
- CZ: Lower value, highly variable demand → lower-priority review based on business requirements.
The ABC and XYZ thresholds are project-defined analytical rules and are not intended to represent universal retail standards.

10. 📈 Explainable Demand Forecasting
Implemented in src/05_forecasting.py.
Setup & Methodology
- Evaluation Period: 28-day forward holdout horizon (2016-03-28 to 2016-04-24, days d_1886 to d_1913).
- Training Period: 2011-01-29 to 2016-03-27 (1,885 historical days, d_1 to d_1885).
- Forecast Design: Strict fixed-origin out-of-sample forecast from cutoff date 2016-03-27. No test-period observations were used in model fitting, preventing data leakage.
Evaluated Models
1. Naive (7-Day Seasonal Lag): Repeats the 7 days preceding the cutoff across 4 weeks.
2. 7-Day Simple Moving Average (SMA): Constant forecast equal to the average of the last 7 training days.
3. 28-Day Simple Moving Average (SMA): Constant forecast equal to the average of the last 28 training days.
4. Holt-Winters Exponential Smoothing: Statistical model with additive trend and weekly 7-day seasonality.
   
11. 🎯 Forecast Evaluation Metrics & Results
Evaluated across all 216 SKUs × 28 test days:
N = 6,048 observations
Metrics
MAE  = Mean Absolute Error
RMSE = Root Mean Squared Error

WAPE = Sum of Absolute Errors / Sum of Actual Demand × 100%

Forecast Bias =
Sum(Forecast - Actual) / Sum(Actual) × 100%

WAPE is used instead of MAPE because MAPE divides by actual demand and therefore becomes problematic when actual demand is zero.
Empirical Results
Model	MAE (Units)	RMSE (Units)	WAPE %	Forecast Bias %	Evaluation Finding
28-Day Simple Moving Average	1.177	2.084	88.81%	+17.95%	Best-performing method on the 28-day holdout
7-Day Simple Moving Average	1.395	2.683	105.26%	+41.81%	Over-reacts to short-term spikes
Naive (7-Day Seasonal Lag)	1.645	3.402	124.07%	+41.80%	Vulnerable to weekly noise shifts
Holt-Winters Exponential Smoothing	1.742	3.654	131.41%	+68.16%	Trend extrapolation overshoots during zero-demand spells


The 28-day SMA was the best-performing method on the selected 28-day holdout based on the reported evaluation metrics. However, its WAPE of 88.81% is still high, so the result should be interpreted as a model comparison rather than evidence of highly accurate forecasting.
The 28-day SMA provided a smoother baseline than the shorter-window methods for the selected intermittent demand data.

12. 🛡️ Basic Inventory Planning
Implemented in src/06_inventory_planning.py.
The project uses simple, explainable supply chain formulas calculated at the individual SKU level.
Documented Assumptions
- Supplier Lead Time (L): 7 Days (assumed planning value).
- Target Service Levels:
  - Class A Items: 95% Cycle Service Level (Z = 1.65).
  - Class B & C Items: 90% Cycle Service Level (Z = 1.28).
These are project assumptions rather than actual supplier or company policies.
Formulas
1. Lead-Time Demand
LTD = Average Daily Demand × Lead Time

2. Safety Stock
Safety Stock = Z × Standard Deviation of Daily Demand × √Lead Time

3. Reorder Point
ROP = Lead-Time Demand + Safety Stock

Class-Level Averages
ABC Class	Avg Daily Demand	Lead-Time Demand (7d)	Safety Stock Buffer (SS)	Suggested Reorder Point (ROP)
Class A	2.16 units/day	15.09 units	11.24 units	26.33 units
Class B	0.73 units/day	5.13 units	4.63 units	9.76 units
Class C	0.36 units/day	2.55 units	2.92 units	5.47 units


These values are planning calculations based on the stated assumptions, not optimized inventory targets.

13. 📑 Excel Demand Planning Workbook
File:
outputs/Retail_Demand_Forecasting_Inventory_Plan.xlsx
The workbook contains four main tabs:
- Tab 1: Executive Summary: High-level KPI summary cards and project overview.
- Tab 2: Demand & Product Analysis: Top 25 SKU rankings, pricing, volume, and revenue share.
- Tab 3: ABC-XYZ Matrix: 9-box summary table and complete 216 SKU classification.
- Tab 4: Forecast & Inventory Plan: Model benchmark table and interactive SKU Inventory Calculator with live dynamic Excel formulas.
Key formulas include:
Lead-Time Demand:
=ROUND(D15 * F15, 2)

Safety Stock:
=ROUND(H15 * E15 * SQRT(F15), 2)

Reorder Point:
=ROUND(I15 + J15, 2)

14. 💡 Key Business Findings
1. Weekend Concentration: Saturday and Sunday demand is approximately 46% higher than weekday averages. This suggests that weekly replenishment planning should account for day-of-week demand patterns.
2. High Intermittency: 59.29% of SKU-day observations had zero demand. The 28-day moving average provided the best-performing baseline among the evaluated forecasting methods on the selected holdout period.
3. 
4. Revenue Skew: 109 Class A items account for 79.7% of total revenue in the selected scope. This provides a basis for prioritizing higher-value SKUs when applying the project's assumed service-level framework.
15. 📋 Explicit Assumptions
- Supplier Lead Time is assumed to be 7 calendar days.
- Target Service Levels are assumed to be 95% for Class A and 90% for Class B and C.
- Normal distribution of lead-time demand is assumed for the standard safety stock formula calculations.
- Fixed purchase order costs and warehouse holding costs are not provided in the dataset; therefore, cost-based optimization models such as EOQ are omitted.
- ABC and XYZ thresholds are project-defined analytical rules rather than universal industry standards.
- 
16. ⚠️ Limitations
- POS Sales vs. Inventory Availability: The dataset contains transaction records, not on-hand inventory or shelf availability data. Therefore, zero-demand days are treated as intermittent demand observations and not confirmed stockouts.
- Intermittent Forecasting Errors: Daily SKU-level demand contains 59.3% zero-demand observations, making forecasting challenging and contributing to the high WAPE observed in the holdout period.
- Forecast Scope: Forecast evaluation is based on a single 28-day holdout period and the selected 216-SKU scope.
- Focused Scope: Results represent Store CA_1 and Department FOODS_1 from the historical M5 benchmark dataset.
- Inventory Planning Assumptions: Lead time and service levels are assumed because actual supplier lead-time, inventory-position, ordering-cost, and holding-cost information is not available in the dataset.
- 
17. 🚀 How to Run the Pipeline
1. Prepare and clean raw data
python src/01_data_preparation.py

2. Build and populate SQLite database
python src/02_create_database.py

3. Generate EDA charts
python src/03_eda_analysis.py

4. Perform ABC-XYZ demand segmentation
python src/04_abc_xyz_analysis.py

5. Run 28-day forecasting and evaluation
python src/05_forecasting.py

6. Calculate inventory safety stock & ROP
python src/06_inventory_planning.py

7. Generate Excel workbook
python src/07_generate_excel_workbook.py

18. 📁 Project Structure
retail-demand-forecasting/
│
├── data/
│   ├── calendar.csv
│   ├── sales_train_validation.csv
│   └── sell_prices.csv
│
├── data_processed/
│   └── clean_retail_demand.csv
│
├── database/
│   └── retail_demand.db
│
├── sql/
│   ├── schema.sql
│   └── demand_queries.sql
│
├── src/
│   ├── 01_data_preparation.py
│   ├── 02_create_database.py
│   ├── 03_eda_analysis.py
│   ├── 04_abc_xyz_analysis.py
│   ├── 05_forecasting.py
│   ├── 06_inventory_planning.py
│   ├── 07_generate_excel_workbook.py
│   ├── audit_project.py
│   ├── run_all.py
│   └── test_sql_queries.py
│
├── outputs/
│   ├── charts/
│   ├── Retail_Demand_Forecasting_Inventory_Plan.xlsx
│   ├── abc_xyz_sku_classification.csv
│   ├── abc_xyz_summary_matrix.csv
│   ├── forecast_evaluation_by_sku.csv
│   ├── forecast_evaluation_summary.csv
│   ├── forecast_predictions_28d.csv
│   └── inventory_planning_table.csv
│
├── README.md
├── INTERVIEW_PREP.md
├── requirements.txt
└── .gitignore

Note: The raw M5 data/ files are intentionally excluded from the Git repository through .gitignore because of their large file sizes. They are required locally to reproduce the data-preparation step.

19. 🔮 Future Improvements
- Intermittent Demand Forecasting: Implement specialized methods such as Croston or TSB to better handle sparse demand patterns.
- Multi-Store Expansion: Extend the analysis to additional M5 stores such as TX_1 and WI_1.
- Longer Forecast Evaluation: Evaluate models across multiple rolling holdout periods instead of a single 28-day holdout.
- BI Dashboard: Build an interactive dashboard using a tool such as Power BI or Tableau connected to the SQLite database for executive visual reporting.
- Real Inventory Integration: Incorporate on-hand inventory, purchase orders, supplier lead times, and stockout information to make inventory planning more realistic.
- Advanced Forecasting: Compare the baseline methods against additional statistical or machine-learning forecasting approaches once a larger and more complete business dataset is available.
