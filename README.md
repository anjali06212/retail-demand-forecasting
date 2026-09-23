# Retail Demand Forecasting & Inventory Planning

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Star_Schema-green.svg)](https://www.sqlite.org/)
[![Excel](https://img.shields.io/badge/Excel-Dynamic_Formulas-success.svg)](https://products.office.com/excel)

An end-to-end, interview-defensible data analytics and demand planning portfolio project. Mined and analyzed 5.2 years of daily retail point-of-sale data from Walmart (Kaggle M5 benchmark) to build a structured demand analysis pipeline, SQLite star schema database, ABC-XYZ SKU segmentation, explainable time-series forecasting models, basic inventory replenishment parameters, and a multi-tab Microsoft Excel planning workbook with live dynamic formulas.

---

## 📌 Project Architecture

```
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
Business Insights & Interview Preparation
```

---

## 1. 🏢 Business Problem
In retail supply chains, stockouts lead to lost revenue and customer churn, while excess inventory ties up working capital and causes spoilage in perishable grocery categories. Balancing service levels and inventory buffers requires translating raw point-of-sale data into actionable demand forecasts, SKU-level prioritization, and calculated reorder triggers.

## 2. 🎯 Why Demand Planning?
Demand planning connects sales data with procurement decisions. Rather than relying on static ordering rules or opaque black-box machine learning, supply chain planners use structured demand segmentation (ABC-XYZ) and explainable time-series baselines to establish defensible safety stock levels and reorder points.

## 3. 📂 Dataset
This project uses the Kaggle Walmart M5 Forecasting benchmark dataset:
* `calendar.csv`: Contains calendar dates, day of week, month, year, event/holiday names, and state SNAP assistance flags.
* `sales_train_validation.csv`: Contains historical daily unit sales quantities across products and stores (`d_1` to `d_1913`).
* `sell_prices.csv`: Contains weekly store-item selling prices (`wm_yr_wk`, `sell_price`).

## 4. 🔍 Project Scope
To maintain complete analytical depth while keeping data processing fast and transparent across Python, SQLite, and Excel:
* **Store**: `Store CA_1`
* **Department**: `Department FOODS_1` (Grocery category)
* **Products**: **216 unique SKUs**
* **Historical Horizon**: **1,913 consecutive days** (January 29, 2011 to April 24, 2016 / ~5.2 years)
* **Total Observation Grid**: **413,208 SKU-day records** ($216 \times 1,913$, with zero missing SKU-date combinations)

---

## 5. 🛠️ Tools & Technologies
* **Python (3.11)**: `pandas` for data wrangling, `numpy` for mathematical calculations, `statsmodels` for time-series modeling, `openpyxl` for Excel workbook generation, `matplotlib` for charts.
* **SQL (SQLite)**: Dimensional star schema design, table DDL, aggregations, window functions (`AVG() OVER`), `LAG()`, CTEs.
* **Microsoft Excel**: Multi-tab analytical planning workbook, formatted KPI cards, conditional formatting, and dynamic live formulas (`ROUND`, `SQRT`).

---

## 6. 🧹 Data Preparation & Cleaning (`src/01_data_preparation.py`)
* Filtered raw data for Store `CA_1` and Department `FOODS_1`.
* Reshaped wide daily sales columns (`d_1`..`d_1913`) into tidy long format: `(date, item_id, store_id, units_sold)`.
* Merged with `calendar.csv` on day index `d` to attach day name, month, year, event flags, and SNAP indicators.
* Merged with `sell_prices.csv` on `(store_id, item_id, wm_yr_wk)` to calculate `revenue = units_sold * sell_price`.
* Saved output to `data_processed/clean_retail_demand.csv`.

---

## 7. 🗄️ SQL Star Schema & Demand Analytics (`sql/`)

Database: `database/retail_demand.db`

### Star Schema Architecture:
* **`dim_date`**: `date_key` (PK), `date`, `day_name`, `day_of_week`, `month`, `month_name`, `year`, `is_weekend`, `event_name`, `event_type`, `is_event`, `snap_flag`.
* **`dim_product`**: `item_id` (PK), `dept_id`, `cat_id`, `avg_price`, `min_price`, `max_price`.
* **`dim_store`**: `store_id` (PK), `state_id`, `store_name` (`Store CA_1`).
* **`fact_daily_sales`**: `sales_id` (PK), `date_key` (FK), `item_id` (FK), `store_id` (FK), `units_sold`, `sell_price`, `revenue`, `is_zero_demand`.

### Key SQL Analytics Demonstrated (`sql/demand_queries.sql`):
1. **Executive Demand KPIs**: Aggregations across units sold, revenue, and active SKUs.
2. **Top / Bottom SKU Rankings**: Product revenue and volume rankings.
3. **Monthly & Yearly Trends**: Historical sales volume and seasonality.
4. **Day-of-Week Seasonality**: Quantifying weekend demand lift (+46% on Saturdays vs. weekdays).
5. **Promotional / Event Day Lift**: Comparing holiday/event days against regular baseline days.
6. **Rolling Moving Averages**: 7-day and 28-day window smoothing (`AVG() OVER (ROWS BETWEEN ... PRECEDING)`).
7. **Day-over-Day Demand Acceleration**: Measuring daily velocity using `LAG()`.
8. **Intermittent Demand Analysis**: Zero-demand day percentage per SKU.
9. **Pure SQL ABC Classification**: Cumulative revenue contribution via CTEs and window sums.

---

## 8. 📊 Exploratory Data Analysis (`src/03_eda_analysis.py`)
Key findings visualized in `outputs/charts/`:
* **Weekend Peak**: Demand spikes significantly on Saturday (average 381.2 units/day) and Sunday (330.8 units/day) compared to Monday–Friday (261.3 units/day).
* **Intermittent Demand**: 59.29% of daily SKU-level records have zero units sold, illustrating real-world retail intermittency.
* **Annual Seasonality**: Demand shows consistent mid-year peaks and end-of-year holiday shifts.

---

## 9. 📦 ABC-XYZ Demand Segmentation (`src/04_abc_xyz_analysis.py`)

All 216 SKUs were categorized across two complementary dimensions:

### A. ABC Analysis (Pareto Revenue Contribution):
* **Class A (Top 80% Revenue)**: 109 SKUs (50.5% of items) generate **$79.7\%$ of total revenue** (\$1,038,843).
* **Class B (80% – 95% Revenue)**: 62 SKUs (28.7% of items) generate **$15.3\%$ of total revenue** (\$199,242).
* **Class C (95% – 100% Revenue)**: 45 SKUs (20.8% of items) generate **$5.0\%$ of total revenue** (\$65,344).

### B. XYZ Analysis (Demand Predictability via Coefficient of Variation):
$$CV = \frac{\sigma_{\text{daily demand}}}{\mu_{\text{daily demand}}}$$
* **Class X ($CV \le 0.50$)**: 0 SKUs (Steady demand).
* **Class Y ($0.50 < CV \le 1.00$)**: 9 SKUs (Moderate variability / seasonal).
* **Class Z ($CV > 1.00$)**: 207 SKUs (High variability / intermittent).

### C. 9-Box Policy Matrix:
* **`AY` (9 SKUs)**: High value, seasonal $\rightarrow$ Weekly review, seasonal forecasting, 95% service level.
* **`AZ` (100 SKUs)**: High value, erratic $\rightarrow$ Dedicated planner review, dynamic safety buffer.
* **`BZ` (62 SKUs)**: Moderate value, erratic $\rightarrow$ Bi-weekly review, standard buffer.
* **`CZ` (45 SKUs)**: Low value, erratic $\rightarrow$ Monthly review, minimum batch reorder, zero/low buffer.

---

## 10. 📈 Explainable Demand Forecasting (`src/05_forecasting.py`)

### Setup & Methodology:
* **Evaluation Period**: 28-day forward holdout horizon (`2016-03-28` to `2016-04-24`, days `d_1886` to `d_1913`).
* **Training Period**: `2011-01-29` to `2016-03-27` (1,885 historical days, `d_1` to `d_1885`).
* **Forecast Design**: Strict **fixed-origin out-of-sample forecast** from cutoff date `2016-03-27`. No test-period observations were used in model fitting (zero data leakage).

### Evaluated Models:
1. **Naive (7-Day Seasonal Lag)**: Repeats the 7 days preceding the cutoff across 4 weeks.
2. **7-Day Simple Moving Average (SMA)**: Constant forecast equal to the average of the last 7 training days.
3. **28-Day Simple Moving Average (SMA)**: Constant forecast equal to the average of the last 28 training days.
4. **Holt-Winters Exponential Smoothing**: Statistical model with additive trend and weekly 7-day seasonality.

---

## 11. 🎯 Forecast Evaluation Metrics & Results

Evaluated across all 216 SKUs $\times$ 28 test days ($N = 6,048$ observations):

$$\text{MAE} = \frac{1}{N}\sum |\text{Actual} - \text{Forecast}| \qquad \text{RMSE} = \sqrt{\frac{1}{N}\sum (\text{Actual} - \text{Forecast})^2}$$
$$\text{WAPE} = \frac{\sum |\text{Actual} - \text{Forecast}|}{\sum \text{Actual}} \times 100\% \qquad \text{Forecast Bias} = \frac{\sum (\text{Forecast} - \text{Actual})}{\sum \text{Actual}} \times 100\%$$

*(Note: WAPE is used instead of MAPE because MAPE divides by actual demand, causing division-by-zero on zero-demand days).*

### Empirical Results:

| Model | MAE (Units) | RMSE (Units) | WAPE % | Forecast Bias % | Evaluation Finding |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **28-Day Simple Moving Average** | **1.177** | **2.084** | **88.81%** | **+17.95%** | **Best-performing method on the 28-day holdout** |
| **7-Day Simple Moving Average** | 1.395 | 2.683 | 105.26% | +41.81% | Over-reacts to short-term spikes |
| **Naive (7-Day Seasonal Lag)** | 1.645 | 3.402 | 124.07% | +41.80% | Vulnerable to weekly noise shifts |
| **Holt-Winters Exponential Smoothing** | 1.742 | 3.654 | 131.41% | +68.16% | Trend extrapolation overshoots during zero spells |

*Insight: The 28-day SMA performed best because it smooths out short-term intermittency noise across a 4-week replenishment cycle.*

---

## 12. 🛡️ Basic Inventory Planning (`src/06_inventory_planning.py`)

Using explainable supply chain formulas calculated at the individual SKU level:

### Documented Assumptions:
* **Supplier Lead Time ($L$)**: **7 Days** (1 calendar week delivery SLA).
* **Target Service Levels**:
  * **Class A Items**: **95% Cycle Service Level** ($Z = 1.65$).
  * **Class B & C Items**: **90% Cycle Service Level** ($Z = 1.28$).

### Formulas:
1. **Lead-Time Demand ($LTD$)**:
   $$\text{LTD} = \text{Average Daily Demand} \times \text{Lead Time}$$
2. **Safety Stock ($SS$)**:
   $$\text{Safety Stock} = Z \times \sigma_{\text{daily demand}} \times \sqrt{\text{Lead Time}}$$
3. **Reorder Point ($ROP$)**:
   $$\text{Reorder Point} = \text{Lead-Time Demand} + \text{Safety Stock}$$

### Class-Level Averages:
| ABC Class | Avg Daily Demand | Lead-Time Demand (7d) | Safety Stock Buffer (SS) | Suggested Reorder Point (ROP) |
| :---: | :---: | :---: | :---: | :---: |
| **Class A** | 2.16 units/day | 15.09 units | 11.24 units | **26.33 units** |
| **Class B** | 0.73 units/day | 5.13 units | 4.63 units | **9.76 units** |
| **Class C** | 0.36 units/day | 2.55 units | 2.92 units | **5.47 units** |

---

## 13. 📑 Excel Demand Planning Workbook

File: `outputs/Retail_Demand_Forecasting_Inventory_Plan.xlsx`

* **Tab 1: Executive Summary**: High-level KPI summary cards and project governance overview.
* **Tab 2: Demand & Product Analysis**: Top 25 SKU rankings, pricing, volume, and revenue share.
* **Tab 3: ABC-XYZ Matrix**: 9-Box summary table and complete 216 SKU classification.
* **Tab 4: Forecast & Inventory Plan**: Model benchmark table and interactive SKU Inventory Calculator with **live dynamic Excel formulas**:
  * Lead-Time Demand: `=ROUND(D15 * F15, 2)`
  * Safety Stock: `=ROUND(H15 * E15 * SQRT(F15), 2)`
  * Reorder Point: `=ROUND(I15 + J15, 2)`

---

## 14. 💡 Key Business Findings
1. **Weekend Concentration**: Saturday and Sunday demand is $+46\%$ higher than weekday averages. Replenishment shipments must arrive before Friday to prevent weekend stockouts.
2. **High Intermittency**: 59.29% of SKU-day observations had zero sales. A 28-day moving average provided a more resilient baseline than Holt-Winters.
3. **Revenue Skew**: 109 Class A items drive $79.7\%$ of revenue. Applying a 95% service level on Class A while holding 90% on Class B/C protects revenue while controlling working capital.

---

## 15. 📋 Explicit Assumptions
* Supplier Lead Time is assumed to be 7 calendar days.
* Target Service Levels are assumed to be 95% for Class A and 90% for Class B and C.
* Normal distribution of lead-time demand is assumed for standard safety stock formula calculations.
* Fixed purchase order costs and warehouse holding costs are not provided in the dataset; therefore, arbitrary cost optimization models (e.g., EOQ) are omitted.

---

## 16. ⚠️ Limitations
* **POS Sales vs. Inventory Availability**: The dataset contains transaction records, not on-hand shelf inventory. Zero-demand days are treated as *intermittent demand / potential stockout indicators* rather than confirmed stockouts.
* **Intermittent Forecasting Errors**: Daily SKU-level demand with 59.3% zero sales inherently exhibits high percentage error (WAPE ~88.8%), which is normal in grocery retail and justifies the need for Safety Stock buffers.
* **Focused Scope**: Results represent Store `CA_1` and Department `FOODS_1` from historical M5 data.

---

## 17. 🚀 How to Run the Pipeline

```bash
# 1. Prepare and clean raw data
python src/01_data_preparation.py

# 2. Build and populate SQLite database
python src/02_create_database.py

# 3. Generate EDA charts
python src/03_eda_analysis.py

# 4. Perform ABC-XYZ demand segmentation
python src/04_abc_xyz_analysis.py

# 5. Run 28-day forecasting and evaluation
python src/05_forecasting.py

# 6. Calculate inventory safety stock & ROP
python src/06_inventory_planning.py

# 7. Generate Excel workbook
python src/07_generate_excel_workbook.py
```

---

## 18. 🔮 Future Improvements
* **Croston's Method**: Implement specialized intermittent demand forecasting models (Croston / TSB) to decompose demand into non-zero quantity and inter-arrival intervals.
* **Multi-Store Expansion**: Extend the SQLite schema to compare demand seasonality across Texas (`TX_1`) and Wisconsin (`WI_1`).
* **BI Dashboard**: Build an interactive dashboard (e.g., in Power BI or Tableau) connected to the SQLite database for executive visual reporting.
