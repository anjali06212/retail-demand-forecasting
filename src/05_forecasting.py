import os
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def run_forecasting():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data_processed", "clean_retail_demand.csv")
    output_dir = os.path.join(base_dir, "outputs")
    chart_dir = os.path.join(output_dir, "charts")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(chart_dir, exist_ok=True)

    print("=" * 60)
    print("PHASE 6 & 7: DEMAND FORECASTING & EVALUATION (28-DAY HORIZON)")
    print("=" * 60)

    # 1. Load Data & Train/Test Split
    print("[1/5] Loading clean dataset and creating 28-day train/test split...")
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])

    # Test set: Last 28 days (d_1886 to d_1913)
    test_dates = df['date'].drop_duplicates().sort_values().iloc[-28:]
    test_start_date = test_dates.min()
    test_end_date = test_dates.max()

    train_df = df[df['date'] < test_start_date].copy()
    test_df = df[df['date'] >= test_start_date].copy()

    print(f"  Train period: {train_df['date'].min().strftime('%Y-%m-%d')} to {train_df['date'].max().strftime('%Y-%m-%d')} ({train_df['d'].nunique()} days)")
    print(f"  Test period:  {test_start_date.strftime('%Y-%m-%d')} to {test_end_date.strftime('%Y-%m-%d')} (28 days)")

    # 2. Forecasting Models across all 216 SKUs
    print("[2/5] Running 4 Forecasting Models (Naive, 7-Day SMA, 28-Day SMA, Holt-Winters)...")
    items = df['item_id'].unique()
    all_predictions = []
    
    for idx, item in enumerate(items, 1):
        if idx % 50 == 0 or idx == len(items):
            print(f"  Processing SKU {idx}/{len(items)}...")

        item_train = train_df[train_df['item_id'] == item].sort_values('date').set_index('date')
        item_test = test_df[test_df['item_id'] == item].sort_values('date').set_index('date')

        train_series = item_train['units_sold'].astype(float)
        actuals = item_test['units_sold'].values
        dates = item_test.index

        # Model 1: Naive (Seasonal Persistence - same day of week from last week)
        naive_forecast = train_series.iloc[-7:].values
        # Repeat 7-day pattern for 4 weeks (28 days)
        naive_28d = np.tile(naive_forecast, 4)[:28]

        # Model 2: 7-Day Moving Average (Flat constant forecast from last 7-day mean)
        sma_7_val = max(0.0, train_series.iloc[-7:].mean())
        sma_7_28d = np.full(28, round(sma_7_val, 2))

        # Model 3: 28-Day Moving Average (Flat constant forecast from last 28-day mean)
        sma_28_val = max(0.0, train_series.iloc[-28:].mean())
        sma_28_28d = np.full(28, round(sma_28_val, 2))

        # Model 4: Holt-Winters Exponential Smoothing (Additive trend + weekly 7-day seasonality)
        try:
            # Use last 365 days of training for stability and speed
            recent_train = train_series.iloc[-365:] if len(train_series) >= 365 else train_series
            hw_model = ExponentialSmoothing(
                recent_train,
                trend='add',
                seasonal='add',
                seasonal_periods=7,
                initialization_method='estimated'
            ).fit(smoothing_level=0.2, smoothing_trend=0.05, smoothing_seasonal=0.2)
            hw_forecast = hw_model.forecast(28).values
            hw_28d = np.clip(np.round(hw_forecast, 2), 0, None)
        except Exception:
            # Fallback to 7-Day SMA if optimization fails
            hw_28d = sma_7_28d

        for i in range(28):
            all_predictions.append({
                'date': dates[i].strftime('%Y-%m-%d'),
                'item_id': item,
                'actual': float(actuals[i]),
                'forecast_naive': float(naive_28d[i]),
                'forecast_sma_7': float(sma_7_28d[i]),
                'forecast_sma_28': float(sma_28_28d[i]),
                'forecast_holt_winters': float(hw_28d[i])
            })

    pred_df = pd.DataFrame(all_predictions)

    # 3. Forecast Evaluation Metrics
    print("[3/5] Calculating Evaluation Metrics (MAE, RMSE, WAPE %, Forecast Bias %)...")
    models = ['forecast_naive', 'forecast_sma_7', 'forecast_sma_28', 'forecast_holt_winters']
    model_labels = {
        'forecast_naive': 'Naive (7-Day Seasonal Lag)',
        'forecast_sma_7': '7-Day Simple Moving Average',
        'forecast_sma_28': '28-Day Simple Moving Average',
        'forecast_holt_winters': 'Holt-Winters Exponential Smoothing'
    }

    eval_results = []
    total_actual = pred_df['actual'].sum()

    for m in models:
        actual = pred_df['actual'].values
        pred = pred_df[m].values

        mae = np.mean(np.abs(actual - pred))
        rmse = np.sqrt(np.mean((actual - pred) ** 2))
        wape = (np.sum(np.abs(actual - pred)) / total_actual) * 100
        bias = (np.sum(pred - actual) / total_actual) * 100

        eval_results.append({
            'Model_Key': m,
            'Model_Name': model_labels[m],
            'MAE': round(mae, 3),
            'RMSE': round(rmse, 3),
            'WAPE_Pct': round(wape, 2),
            'Forecast_Bias_Pct': round(bias, 2)
        })

    eval_summary = pd.DataFrame(eval_results).sort_values(by='WAPE_Pct').reset_index(drop=True)
    best_model_key = eval_summary.loc[0, 'Model_Key']
    best_model_name = eval_summary.loc[0, 'Model_Name']
    print(f"\n--- Empirical Model Evaluation Results ---")
    print(eval_summary[['Model_Name', 'MAE', 'RMSE', 'WAPE_Pct', 'Forecast_Bias_Pct']].to_string(index=False))
    print(f"\n  -> Best Performing Model: {best_model_name} (WAPE: {eval_summary.loc[0, 'WAPE_Pct']}%)")

    # Attach Best Forecast column
    pred_df['best_forecast'] = pred_df[best_model_key]

    # Save outputs
    pred_out_path = os.path.join(output_dir, "forecast_predictions_28d.csv")
    pred_df.to_csv(pred_out_path, index=False)
    print(f"\n[4/5] Saved 28-day predictions to {pred_out_path}")

    summary_out_path = os.path.join(output_dir, "forecast_evaluation_summary.csv")
    eval_summary.to_csv(summary_out_path, index=False)
    print(f"  Saved evaluation summary to {summary_out_path}")

    # SKU-level evaluation table
    sku_evals = []
    for item in items:
        sub = pred_df[pred_df['item_id'] == item]
        item_act = sub['actual'].sum()
        item_best_pred = sub['best_forecast'].sum()
        item_mae = np.mean(np.abs(sub['actual'] - sub['best_forecast']))
        item_wape = (np.sum(np.abs(sub['actual'] - sub['best_forecast'])) / item_act * 100) if item_act > 0 else 0.0
        item_bias = ((item_best_pred - item_act) / item_act * 100) if item_act > 0 else 0.0

        sku_evals.append({
            'item_id': item,
            'test_actual_units': round(item_act, 1),
            'test_forecast_units': round(item_best_pred, 1),
            'mae': round(item_mae, 3),
            'wape_pct': round(min(item_wape, 500.0), 2),
            'bias_pct': round(item_bias, 2)
        })

    sku_eval_df = pd.DataFrame(sku_evals)
    sku_eval_out = os.path.join(output_dir, "forecast_evaluation_by_sku.csv")
    sku_eval_df.to_csv(sku_eval_out, index=False)
    print(f"  Saved SKU-level evaluation to {sku_eval_out}")

    # 5. Visualizations
    print("[5/5] Generating Forecast Comparison & Time-Series Charts...")

    # Chart 1: Model Comparison (WAPE %)
    plt.figure(figsize=(8, 4.5), dpi=300)
    bars = plt.barh(eval_summary['Model_Name'], eval_summary['WAPE_Pct'], color='#3b82f6', edgecolor='#1e293b', height=0.55)
    plt.title('Forecasting Model Accuracy Comparison (WAPE % - Lower is Better)', pad=15)
    plt.xlabel('Weighted Absolute Percentage Error (WAPE %)')
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 0.5, bar.get_y() + bar.get_height()/2.0, f"{w:.2f}%", ha='left', va='center', fontsize=9, fontweight='bold')
    plt.xlim(0, max(eval_summary['WAPE_Pct']) * 1.15)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    chart1_path = os.path.join(chart_dir, "forecast_model_comparison_wape.png")
    plt.savefig(chart1_path)
    plt.close()

    # Chart 2: Total Department Actual vs Best Forecast Trend (28 Days)
    daily_pred = pred_df.groupby('date').agg(
        actual=('actual', 'sum'),
        best_forecast=('best_forecast', 'sum'),
        sma_7=('forecast_sma_7', 'sum'),
        holt_winters=('forecast_holt_winters', 'sum')
    ).reset_index()
    daily_pred['date'] = pd.to_datetime(daily_pred['date'])

    plt.figure(figsize=(11, 5), dpi=300)
    plt.plot(daily_pred['date'], daily_pred['actual'], marker='o', color='#0f172a', linewidth=2.2, label='Actual Daily Demand')
    plt.plot(daily_pred['date'], daily_pred['holt_winters'], marker='s', linestyle='--', color='#2563eb', linewidth=2.0, label='Holt-Winters Forecast')
    plt.plot(daily_pred['date'], daily_pred['sma_7'], linestyle=':', color='#f59e0b', linewidth=1.8, label='7-Day SMA Forecast')
    plt.title('28-Day Holdout Forecast vs. Actual Demand (Total Department Level)', pad=15)
    plt.xlabel('Date')
    plt.ylabel('Total Daily Units Sold')
    plt.legend(frameon=True, loc='upper right')
    plt.tight_layout()
    chart2_path = os.path.join(chart_dir, "forecast_actual_vs_predicted_trend.png")
    plt.savefig(chart2_path)
    plt.close()

    print("\n[SUCCESS] Forecasting and Evaluation Completed Successfully!")
    print("=" * 60)

if __name__ == '__main__':
    run_forecasting()
