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

---

## 🏢 Business Problem

In retail supply chains, stockouts can lead to lost revenue and customer dissatisfaction, while excess inventory can tie up working capital.

Balancing service levels and inventory buffers requires translating historical point-of-sale data into:

- Demand forecasts
- SKU-level prioritization
- Inventory planning parameters
- Calculated reorder triggers

---

## 🎯 Why Demand Planning?

Demand planning connects historical sales data with procurement and inventory decisions.

Rather than relying on static ordering rules or opaque black-box machine learning, this project uses structured and explainable approaches such as:

- ABC-XYZ demand segmentation
- Time-series forecasting baselines
- Safety stock calculations
- Reorder point calculations

This makes the analysis easier to interpret and explain from a business perspective.

---

## 📂 Dataset

This project uses the **Walmart M5 Forecasting benchmark dataset**.

| File | Description |
|---|---|
| `calendar.csv` | Contains calendar dates, day of week, month, year, event/holiday names, and SNAP assistance flags. |
| `sales_train_validation.csv` | Contains historical daily unit sales quantities across products and stores (`d_1` to `d_1913`). |
| `sell_prices.csv` | Contains weekly store-item selling prices (`wm_yr_wk`, `sell_price`). |

---

## 🔍 Project Scope

To maintain analytical depth while keeping data processing fast and transparent across Python, SQLite, and Excel, the project focuses on the following scope:

| Parameter | Value |
|---|---|
| **Store** | `CA_1` |
| **Department** | `FOODS_1` |
| **Products** | **216 unique SKUs** |
| **Historical Horizon** | **1,913 consecutive days** |
| **Date Range** | **January 29, 2011 – April 24, 2016** |
| **Total Observation Grid** | **413,208 SKU-day records** |
| **Missing SKU-Date Combinations** | **0** |

---

## 🛠️ Tools & Technologies

### Python

- **Pandas** for data wrangling and transformation
- **NumPy** for mathematical calculations
- **Statsmodels** for time-series forecasting
- **Openpyxl** for Excel workbook generation
- **Matplotlib** for data visualization

### SQL

- **SQLite** database
- Dimensional star schema
- Table creation and DDL
- Aggregations
- CTEs
- Window functions
- `AVG() OVER`
- `LAG()`

### Microsoft Excel

- Multi-tab analytical planning workbook
- KPI summary cards
- Conditional formatting
- Dynamic formulas
- SKU-level inventory calculations

---

## 🧹 Data Preparation & Cleaning

Implemented in `src/01_data_preparation.py`.

The raw M5 data is processed through the following steps:

1. Filter the dataset for Store `CA_1` and Department `FOODS_1`.
2. Reshape the wide daily sales columns (`d_1` to `d_1913`) into tidy long format.
3. Create the structure:

   `date, item_id, store_id, units_sold`

4. Merge calendar information using the day index `d`.
5. Merge weekly selling prices using:

   `(store_id, item_id, wm_yr_wk)`

6. Calculate:

   `revenue = units_sold × sell_price`

7. Save the processed dataset to:

   `data_processed/clean_retail_demand.csv`

---

## 🗄️ SQL Star Schema & Demand Analytics

Database:

`database/retail_demand.db`

### Star Schema

| Table | Purpose |
|---|---|
| `dim_date` | Date, day-of-week, month, year, weekend, event and SNAP information |
| `dim_product` | Product, department, category and price information |
| `dim_store` | Store and state information |
| `fact_daily_sales` | Daily SKU-level sales, price, revenue and zero-demand information |

### Key SQL Analytics

Implemented in `sql/demand_queries.sql`.

- Executive demand KPIs
- Top and bottom SKU rankings
- Monthly and yearly demand trends
- Day-of-week seasonality
- Event and holiday demand comparisons
- 7-day and 28-day rolling averages
- Day-over-day demand changes using `LAG()`
- Zero-demand and intermittency analysis
- ABC revenue classification using CTEs and window functions

---

## 📊 Exploratory Data Analysis

Implemented in `src/03_eda_analysis.py`.

The analysis focuses on:

- Overall demand trends
- Day-of-week demand patterns
- Monthly seasonality
- Zero-demand observations
- SKU-level demand variability
- Revenue concentration

### Key Findings

- **Saturday:** Average demand of **381.2 units/day**
- **Sunday:** Average demand of **330.8 units/day**
- **Monday–Friday:** Average demand of **261.3 units/day**
- **Zero-demand observations:** **59.29%** of SKU-day records

---

## 📦 ABC-XYZ Demand Segmentation

Implemented in `src/04_abc_xyz_analysis.py`.

ABC-XYZ analysis combines two dimensions:

- **ABC:** Revenue contribution
- **XYZ:** Demand variability

### ABC Classification

| Class | SKUs | Share of SKUs | Revenue Share | Revenue |
|---|---:|---:|---:|---:|
| **A** | 109 | 50.5% | **79.7%** | $1,038,843 |
| **B** | 62 | 28.7% | **15.3%** | $199,242 |
| **C** | 45 | 20.8% | **5.0%** | $65,344 |

### XYZ Classification

The coefficient of variation is calculated as:

```text
CV = Standard Deviation of Daily Demand / Mean Daily Demand
```

| Class | Rule | SKUs |
|---|---|---:|
| **X** | CV ≤ 0.50 | 0 |
| **Y** | 0.50 < CV ≤ 1.00 | 9 |
| **Z** | CV > 1.00 | 207 |

The high proportion of Class Z SKUs reflects the variability and intermittency observed in the selected dataset scope.

> **Note:** ABC and XYZ thresholds are project-defined analytical rules and are not universal retail standards.

---

## 📈 Explainable Demand Forecasting

Implemented in `src/05_forecasting.py`.

### Forecast Setup

- **Training period:** January 29, 2011 – March 27, 2016
- **Holdout period:** March 28, 2016 – April 24, 2016
- **Forecast horizon:** 28 days
- **SKUs evaluated:** 216
- **Total test observations:** 6,048

The forecasting process uses a fixed-origin out-of-sample evaluation. Test-period observations are not used during model fitting.

### Models Evaluated

1. **Naive 7-Day Seasonal Lag**
2. **7-Day Simple Moving Average**
3. **28-Day Simple Moving Average**
4. **Holt-Winters Exponential Smoothing**

---

## 🎯 Forecast Evaluation

The following metrics are used:

```text
MAE  = Mean Absolute Error

RMSE = Root Mean Squared Error

WAPE = Sum of Absolute Errors / Sum of Actual Demand × 100%

Forecast Bias =
Sum(Forecast - Actual) / Sum(Actual) × 100%
```

WAPE is used instead of MAPE because the dataset contains many zero-demand observations.

### Results

| Model | MAE | RMSE | WAPE | Forecast Bias |
|---|---:|---:|---:|---:|
| **28-Day SMA** | **1.177** | **2.084** | **88.81%** | **+17.95%** |
| 7-Day SMA | 1.395 | 2.683 | 105.26% | +41.81% |
| Naive 7-Day | 1.645 | 3.402 | 124.07% | +41.80% |
| Holt-Winters | 1.742 | 3.654 | 131.41% | +68.16% |

The **28-Day SMA performed best among the evaluated methods on the selected 28-day holdout** based on the reported metrics.

However, the WAPE of **88.81% remains high**, so this result should be interpreted as a comparison of baseline methods rather than evidence of highly accurate forecasting.

---

## 🛡️ Basic Inventory Planning

Implemented in `src/06_inventory_planning.py`.

The project uses simple SKU-level inventory planning formulas.

### Assumptions

| Parameter | Value |
|---|---|
| **Supplier Lead Time** | 7 days |
| **Class A Service Level** | 95% |
| **Class A Z-value** | 1.65 |
| **Class B/C Service Level** | 90% |
| **Class B/C Z-value** | 1.28 |

These are **project assumptions**, not actual supplier or company policies.

### Formulas

**Lead-Time Demand**

```text
LTD = Average Daily Demand × Lead Time
```

**Safety Stock**

```text
Safety Stock = Z × Standard Deviation of Daily Demand × √Lead Time
```

**Reorder Point**

```text
ROP = Lead-Time Demand + Safety Stock
```

### Class-Level Planning Results

| ABC Class | Avg Daily Demand | Lead-Time Demand | Safety Stock | Reorder Point |
|---|---:|---:|---:|---:|
| **A** | 2.16 | 15.09 | 11.24 | **26.33** |
| **B** | 0.73 | 5.13 | 4.63 | **9.76** |
| **C** | 0.36 | 2.55 | 2.92 | **5.47** |

These are planning calculations based on the stated assumptions and are not optimized inventory targets.

---

## 📑 Excel Demand Planning Workbook

Generated as:

`outputs/Retail_Demand_Forecasting_Inventory_Plan.xlsx`

The workbook contains four main tabs:

### 1. Executive Summary

- Project overview
- Key demand KPIs
- Summary metrics

### 2. Demand & Product Analysis

- Top 25 SKUs
- Revenue
- Sales volume
- Pricing information
- Revenue contribution

### 3. ABC-XYZ Matrix

- ABC-XYZ 9-box summary
- Complete 216-SKU classification
- Revenue and variability analysis

### 4. Forecast & Inventory Plan

- Forecast model comparison
- Forecast evaluation metrics
- SKU-level inventory calculator
- Live Excel formulas

Example formulas:

```excel
Lead-Time Demand:
=ROUND(D15 * F15, 2)

Safety Stock:
=ROUND(H15 * E15 * SQRT(F15), 2)

Reorder Point:
=ROUND(I15 + J15, 2)
```

---

## 💡 Key Business Findings

### 1. Weekend Demand Concentration

Saturday and Sunday demand is approximately **46% higher than weekday averages**.

This indicates that day-of-week demand patterns should be considered when planning replenishment.

### 2. High Demand Intermittency

**59.29%** of SKU-day observations recorded zero demand.

The **28-day moving average** provided the best-performing baseline among the evaluated forecasting methods on the selected holdout period.

### 3. Revenue Concentration

**109 Class A SKUs account for 79.7% of total revenue** within the selected project scope.

This provides a basis for prioritizing higher-value SKUs when applying the project's assumed service-level framework.

---

## 📋 Assumptions

- Supplier lead time is assumed to be **7 calendar days**.
- Target service levels are assumed to be **95% for Class A** and **90% for Class B and C**.
- Normal distribution of lead-time demand is assumed for the safety stock calculation.
- Purchase-order costs and warehouse holding costs are not available in the dataset.
- ABC and XYZ thresholds are project-defined analytical rules.

---

## ⚠️ Limitations

### POS Sales vs. Inventory Availability

The dataset contains transaction records but does not provide on-hand inventory or shelf availability data.

Therefore, zero-demand days are treated as **intermittent demand observations and not confirmed stockouts**.

### Forecasting Limitations

Daily SKU-level demand contains **59.3% zero-demand observations**, making forecasting challenging and contributing to the high WAPE observed during the holdout period.

### Forecast Evaluation

The forecasting evaluation uses a **single 28-day holdout period** and the selected 216-SKU scope.

### Project Scope

Results represent Store `CA_1` and Department `FOODS_1` from the historical M5 benchmark dataset.

### Inventory Planning

Lead time and service levels are assumed because actual supplier lead-time, inventory-position, ordering-cost, and holding-cost information is not available.

---

## 🚀 How to Run the Pipeline

### 1. Prepare and clean raw data

```bash
python src/01_data_preparation.py
```

### 2. Build the SQLite database

```bash
python src/02_create_database.py
```

### 3. Generate EDA charts

```bash
python src/03_eda_analysis.py
```

### 4. Perform ABC-XYZ segmentation

```bash
python src/04_abc_xyz_analysis.py
```

### 5. Run forecasting and evaluation

```bash
python src/05_forecasting.py
```

### 6. Calculate inventory planning parameters

```bash
python src/06_inventory_planning.py
```

### 7. Generate the Excel workbook

```bash
python src/07_generate_excel_workbook.py
```

---

## 📁 Project Structure

```text
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
```



---

## 🔮 Future Improvements

- **Intermittent Demand Forecasting:** Implement specialized methods such as Croston or TSB.
- **Multi-Store Expansion:** Extend the analysis to additional M5 stores such as `TX_1` and `WI_1`.
- **Longer Forecast Evaluation:** Evaluate models across multiple rolling holdout periods.
- **BI Dashboard:** Build an interactive dashboard using Power BI or Tableau connected to the SQLite database.
- **Real Inventory Integration:** Incorporate on-hand inventory, purchase orders, supplier lead times, and stockout information.
- **Advanced Forecasting:** Compare baseline methods with additional statistical or machine-learning approaches when a larger business dataset is available.
