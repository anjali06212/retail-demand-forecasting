# Demand Planner & Data Analyst Interview Preparation Guide

This guide prepares you to explain and defend every methodology, formula, SQL query, Python script, Excel model, and business decision used in the **Retail Demand Forecasting & Inventory Planning** project.

---

## 🧭 Section 1: Project Overview & Strategy

### Q1: Can you give a 60-second elevator pitch of this project?
> **Answer**:
> *"In this project, I built an end-to-end retail demand forecasting and inventory replenishment pipeline using 5.2 years of daily point-of-sale data from Walmart (Kaggle M5 benchmark), focusing on the grocery department (`FOODS_1`) at store `CA_1`.*
> 
> *I designed a Star Schema in SQLite and engineered SQL analytics to uncover seasonality, weekend lift (+46%), and intermittent demand patterns. I segmented 216 SKUs using ABC-XYZ analysis to prioritize inventory focus. I then evaluated 4 explainable forecasting models over a 28-day forward horizon using WAPE and Forecast Bias, where a 28-Day Simple Moving Average proved most robust (88.8% WAPE). Finally, I translated the demand forecasts into inventory replenishment parameters—calculating Lead-Time Demand, Safety Stock, and Reorder Points—delivered via an interactive dynamic Excel workbook."*

---

### Q2: Why did you choose the Walmart M5 dataset?
> **Answer**:
> *"The M5 dataset is an industry benchmark for retail demand planning because it reflects real-world supply chain complexities: hierarchical product categories, calendar events, promotions, price fluctuations, and genuine intermittent demand with zero-sales days.*
> 
> *Working with this data allowed me to demonstrate data wrangling, SQL modeling, statistical forecasting, and inventory calculations on messy, authentic retail data."*

---

### Q3: Why did you choose store `CA_1` and department `FOODS_1` instead of the full dataset?
> **Answer**:
> *"The raw dataset contains 30,490 time series and ~58 million observations across 10 stores. Processing this directly in Excel causes memory bottlenecks and crashes.*
> 
> *By focusing on `FOODS_1` in `CA_1` (216 SKUs across 1,913 days = 413,208 records), I maintained full historical depth (~5.2 years), rich daily seasonality, price elasticity, and realistic intermittent demand, while keeping the data fast, clean, and fully operational across SQLite, Python, and Excel without loss of analytical depth."*

---

### Q4: Why did you use explainable time-series models instead of complex Machine Learning (like LightGBM or Neural Networks)?
> **Answer**:
> *"In real-world demand planning and supply chain operations, explainability and defensibility are paramount. Complex machine learning models often act as 'black boxes' and can severely overfit or produce erratic spikes on intermittent, zero-heavy retail data.*
> 
> *By testing Naive, 7-day SMA, 28-day SMA, and Holt-Winters Exponential Smoothing, every forecast can be mathematically traced, explained to supply chain stakeholders, and audited against forecast bias without relying on opaque feature engineering."*

---

## 📐 Section 2: Demand Planning & Statistical Metrics

### Q5: Why did you use WAPE instead of MAPE for forecast evaluation?
> **Answer**:
> *"In retail store-level data, many days have zero sales (in our dataset, 59.29% of SKU-days had zero demand). The formula for MAPE is:*
> 
> $$\text{MAPE} = \frac{1}{n}\sum \left|\frac{\text{Actual} - \text{Forecast}}{\text{Actual}}\right| \times 100\%$$
> 
> *When $\text{Actual} = 0$, MAPE divides by zero, resulting in infinity. Even if actual demand is 1 unit and forecast is 3, MAPE reports a 200% error, heavily skewing the average on slow-moving items.*
> 
> *Instead, I used **WAPE (Weighted Absolute Percentage Error)**:*
> 
> $$\text{WAPE} = \frac{\sum |\text{Actual} - \text{Forecast}|}{\sum \text{Actual}} \times 100\%$$
> 
> *WAPE weights absolute errors by overall sales volume across the entire 28-day period. It never divides by zero and is the gold standard metric in retail supply chain planning."*

---

### Q6: What is the difference between MAE and RMSE?
> **Answer**:
> * **MAE (Mean Absolute Error)**: Measures the average magnitude of absolute errors:
>   $$\text{MAE} = \frac{1}{N}\sum |\text{Actual} - \text{Forecast}|$$
>   *It treats all errors linearly (an error of 10 is simply twice as bad as an error of 5).*
> * **RMSE (Root Mean Squared Error)**: Squares errors before averaging and taking the square root:
>   $$\text{RMSE} = \sqrt{\frac{1}{N}\sum (\text{Actual} - \text{Forecast})^2}$$
>   *Because errors are squared, RMSE heavily penalizes large forecast outliers.*

---

### Q7: What is Forecast Bias and why is it important in Inventory Planning?
> **Answer**:
> *"Forecast Bias measures the systematic tendency of a model to consistently over-forecast or under-forecast demand:*
> 
> $$\text{Forecast Bias} = \frac{\sum (\text{Forecast} - \text{Actual})}{\sum \text{Actual}} \times 100\%$$
> 
> * **Positive Bias ($+17.95\%$ for 28-Day SMA)**: Indicates a tendency to over-forecast $\rightarrow$ leads to higher safety buffers, excess inventory, and holding costs.*
> * **Negative Bias**: Indicates systematic under-forecasting $\rightarrow$ leads to stockout risk, lost revenue, and dissatisfied customers.*
> 
> *Tracking bias ensures the supply chain team understands directional risk before committing to purchase orders."*

---

### Q8: Why did the 28-Day Moving Average perform best on the 28-day holdout?
> **Answer**:
> *"Our empirical validation on the 28-day holdout showed:
> * **28-Day SMA**: MAE = 1.177, RMSE = 2.084, WAPE = 88.81%, Bias = +17.95%
> * **7-Day SMA**: MAE = 1.395, RMSE = 2.683, WAPE = 105.26%, Bias = +41.81%
> * **Naive (7-Day Lag)**: MAE = 1.645, RMSE = 3.402, WAPE = 124.07%, Bias = +41.80%
> * **Holt-Winters**: MAE = 1.742, RMSE = 3.654, WAPE = 131.41%, Bias = +68.16%
> 
> *Because grocery store items experience frequent zero-sales days followed by occasional buying spikes on weekends, Holt-Winters interprets a zero followed by a spike as an aggressive trend and overshoots the future horizon. The 28-day SMA smooths out short-term intermittency noise, providing a more stable baseline expectation over a monthly replenishment horizon."*

---

### Q9: Why is the WAPE error around ~88.8%? Is that normal in retail?
> **Answer**:
> *"Yes, at the daily individual SKU level with 59.29% zero-demand days, high percentage error is completely expected.
> 
> When an item sells 0 units on Tuesday and 1 unit on Wednesday, any continuous forecast between 0.5 and 1.5 units generates substantial percentage deviation. In retail demand planning, SKU-level forecasts are smoothed and aggregated into weekly replenishment orders, and Safety Stock buffers are specifically designed to absorb this daily variance."*

---

### Q10: How did you ensure there was no data leakage in your forecasting evaluation?
> **Answer**:
> *"I implemented a strict, out-of-sample **fixed-origin forecast**:
> * **Training cutoff**: `2016-03-27` (`d_1885`). All model fitting and parameter estimation used only historical data up to this date.
> * **Holdout period**: `2016-03-28` to `2016-04-24` (`d_1886` to `d_1913`, 28 days).
> * The 7-day and 28-day moving averages calculated the mean over the final 7 and 28 days of the training set and projected that constant forward baseline.
> * Zero actual observations from the test period were used during forecasting."*

---

## 📦 Section 3: ABC-XYZ SKU Demand Segmentation

### Q11: How did you perform the ABC-XYZ Analysis?
> **Answer**:
> * **ABC Analysis (Revenue Value Contribution)**:
>   * Ranked all SKUs by total historical revenue and computed cumulative contribution (Pareto principle).
>   * **Class A (0% – 80% Revenue)**: 109 SKUs (50.5% of items generate 79.7% of revenue).
>   * **Class B (80% – 95% Revenue)**: 62 SKUs (28.7% of items generate 15.3% of revenue).
>   * **Class C (95% – 100% Revenue)**: 45 SKUs (20.8% of items generate 5.0% of revenue).
> * **XYZ Analysis (Demand Predictability)**:
>   * Calculated the **Coefficient of Variation ($CV$)** for each SKU:
>     $$CV = \frac{\sigma_{\text{daily demand}}}{\mu_{\text{daily demand}}}$$
>   * **Class X ($CV \le 0.50$)**: Steady, highly predictable demand (0 SKUs).
>   * **Class Y ($0.50 < CV \le 1.00$)**: Moderate variability, seasonal demand (9 SKUs).
>   * **Class Z ($CV > 1.00$)**: Erratic, lumpy, intermittent demand (207 SKUs).
> 
> *The concentration in Class Z is a direct reflection of high intermittency at the individual store-SKU level."*

---

### Q12: What is the practical business value of the ABC-XYZ 9-Box Matrix?
> **Answer**:
> *"It dictates tailored replenishment and planning policies rather than treating all SKUs the same:
> * **`AY` (High Value, Seasonal)**: Automated seasonal forecasting, weekly reviews, high service level (95%).
> * **`AZ` (High Value, Erratic)**: High business risk! Requires dedicated demand planner review, supplier lead-time tracking, and a dynamic safety stock buffer.
> * **`BZ` (Moderate Value, Erratic)**: Bi-weekly replenishment review with standard buffers.
> * **`CZ` (Low Value, Erratic)**: Minimal planner time; order in minimum batches or evaluate for product rationalization/delisting."*

---

## 🛡️ Section 4: Basic Inventory Planning & Formulas

### Q13: What is Lead-Time Demand and how did you calculate it?
> **Answer**:
> *"Lead-Time Demand ($LTD$) is the expected number of units that will be sold while waiting for an order to arrive from the supplier.*
> 
> $$\text{Lead-Time Demand} = \text{Average Daily Demand} \times \text{Lead Time (Days)}$$
> 
> *In our model, assuming a standard supplier delivery lead time of $L = 7 \text{ days}$, if an item sells on average $2.16 \text{ units/day}$, its expected lead-time demand is $2.16 \times 7 = 15.12 \text{ units}$."*

---

### Q14: What is Safety Stock and what formula did you use?
> **Answer**:
> *"Safety Stock is the buffer inventory held to protect against demand variability and prevent stockouts during the supplier lead time.
> 
> $$\text{Safety Stock} = Z \times \sigma_{\text{daily demand}} \times \sqrt{\text{Lead Time}}$$
> 
> * **$Z$ (Z-Score)**: Determined by the target Cycle Service Level.
>   * For **Class A** items, we targeted **95% Service Level** $\rightarrow Z = 1.65$.
>   * For **Class B & C** items, we targeted **90% Service Level** $\rightarrow Z = 1.28$.
> * **$\sigma_{\text{daily demand}}$**: Standard deviation of historical daily sales.
> * **$\sqrt{\text{Lead Time}}$**: Accounts for the fact that demand variance compounds over the 7-day delivery period."*

---

### Q15: What is a Reorder Point (ROP)?
> **Answer**:
> *"The Reorder Point is the inventory level that triggers a purchase order.
> 
> $$\text{Reorder Point} = \text{Lead-Time Demand} + \text{Safety Stock} = (\mu_d \times L) + (Z \times \sigma_d \times \sqrt{L})$$
> 
> *When inventory on hand drops to or below the ROP, an order must be placed immediately so that the shipment arrives right as inventory reaches the safety stock level."*

---

### Q16: Why did you assume a 7-day lead time and specific service levels?
> **Answer**:
> *"The Walmart M5 dataset contains sales transactions and pricing, but does not disclose supplier contract lead times or corporate service level mandates.
> 
> Rather than fabricating supplier data, I explicitly documented $L = 7 \text{ days}$ (1 calendar week) as a standard retail replenishment assumption, with 95% service level for high-value Class A items and 90% for Class B/C items. This demonstrates practical supply chain formula application while remaining completely transparent about assumptions."*

---

### Q17: Why did you not calculate EOQ (Economic Order Quantity) or holding cost optimization?
> **Answer**:
> *"EOQ requires explicit cost parameters: fixed order cost per purchase order ($S$) and inventory holding cost percentage ($H$, including warehouse space, insurance, capital cost).
> 
> The Walmart M5 dataset does not disclose purchase order administrative costs or warehouse holding costs. Rather than inventing arbitrary cost assumptions, I kept the model grounded in mathematically verifiable demand and lead-time metrics."*

---

### Q18: Does zero sales on a day mean the store stocked out?
> **Answer**:
> *"No, not necessarily. This is a crucial data limitation to recognize:
> 
> The dataset records **point-of-sale transactions**, not on-hand shelf inventory. A day with zero sales could occur because:
> 1. True zero customer demand (intermittent demand for slow movers).
> 2. An unobserved stockout (the item was out of stock on the shelf).
> 
> Therefore, in our project, we accurately describe these as **'zero-demand days'** or **'intermittent demand'** rather than claiming definitive stockouts."*

---

## 💾 Section 5: SQL & Data Modeling

### Q19: How is your database designed and why did you choose a Star Schema?
> **Answer**:
> *"I designed a dimensional Star Schema in SQLite consisting of:
> * **`dim_date`**: Calendar hierarchy, day of week, month, year, weekend flags, event names, and SNAP assistance flags.
> * **`dim_product`**: Product metadata, department, category, and pricing statistics.
> * **`dim_store`**: Store identifier (`Store CA_1`) and geographic location.
> * **`fact_daily_sales`**: Granular daily transactions (`date_key`, `item_id`, `store_id`, `units_sold`, `sell_price`, `revenue`, `is_zero_demand`).
> 
> *A Star Schema eliminates redundancy, structures data cleanly for analytics, and allows fast aggregations using SQL window functions."*

---

### Q20: How did you compute rolling 7-day and 28-day moving averages in SQL?
> **Answer**:
> *"I used SQL window functions with explicit frame clauses:
> ```sql
> AVG(units_sold) OVER (
>     PARTITION BY item_id 
>     ORDER BY date_key 
>     ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
> ) AS rolling_7d_avg_demand
> ```
> *`PARTITION BY item_id` ensures each SKU's rolling window is calculated independently, while `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` calculates the moving mean over a 7-day window."*

---

### Q21: How did you implement ABC Pareto analysis directly in SQL?
> **Answer**:
> *"I used Common Table Expressions (CTEs) and cumulative window sums:
> ```sql
> WITH sku_rev AS (
>     SELECT item_id, SUM(revenue) AS total_rev 
>     FROM fact_daily_sales 
>     GROUP BY item_id
> ),
> ranked AS (
>     SELECT item_id, total_rev,
>            SUM(total_rev) OVER (ORDER BY total_rev DESC) AS cum_rev,
>            SUM(total_rev) OVER () AS grand_rev
>     FROM sku_rev
> )
> SELECT item_id, total_rev,
>        CASE 
>            WHEN (cum_rev * 1.0 / grand_rev) <= 0.80 THEN 'A'
>            WHEN (cum_rev * 1.0 / grand_rev) <= 0.95 THEN 'B'
>            ELSE 'C'
>        END AS abc_class
> FROM ranked;
> ```
> *This avoids procedural loops and executes as a clean set-based query."*

---

## 📊 Section 6: Excel Workbook & Business Insights

### Q22: What dynamic formulas did you build in the Excel workbook?
> **Answer**:
> *"In Tab 4 (`Forecast & Inventory Plan`), I implemented live, dynamic Excel formulas across all 216 SKUs:
> * **Lead-Time Demand**: `=ROUND(D15 * F15, 2)` (Avg Daily Demand $\times$ Lead Time)
> * **Safety Stock**: `=ROUND(H15 * E15 * SQRT(F15), 2)` ($Z \times \text{StdDev} \times \sqrt{\text{Lead Time}}$)
> * **Reorder Point**: `=ROUND(I15 + J15, 2)` (LTD $+$ Safety Stock)
> 
> *This allows supply chain planners to adjust lead times or service level Z-scores and watch the replenishment triggers recalculate instantly."*

---

### Q23: What key supply chain business insights did this project reveal?
> **Answer**:
> 1. **Weekend Concentration**: Average Saturday sales ($381.2 \text{ units}$) are $+46\%$ higher than weekday averages ($261.3 \text{ units}$). Replenishment deliveries should arrive on Thursday/Friday.
> 2. **Extreme Intermittency**: $59.29\%$ of daily records had zero sales. A 28-day moving average proved significantly more resilient than seasonal Holt-Winters.
> 3. **Revenue Concentration (Pareto)**: 109 Class A items generate $79.7\%$ of revenue. By maintaining a 95% service level ($Z=1.65$) on Class A while holding 90% ($Z=1.28$) on Class B/C, working capital is protected without risking core revenue.

---

### Q24: What would you improve if given real company data in the future?
> **Answer**:
> *"With access to proprietary enterprise data, I would expand this in three ways:
> 1. **Integrate Real On-Hand Inventory**: Combine POS transactions with daily stock-on-hand levels to calculate true on-shelf availability and track actual stockout incidents.
> 2. **Supplier Lead Time Variability**: Incorporate historical supplier delivery delays to model stochastic lead times ($\sigma_L$).
> 3. **Interactive BI Dashboards**: Connect the SQLite star schema to a BI visualization tool (like Power BI or Tableau) for automated executive reporting."*
