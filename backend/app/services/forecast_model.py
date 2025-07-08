import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def run_forecast(file, days=30, granularity='day'):
    try:
        # STEP 1: Load and detect relevant columns
        df = pd.read_csv(file)
        date_candidates = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'time', 'month'])]
        if not date_candidates:
            raise ValueError("No date-like column found.")
        date_col = date_candidates[0]

        # STEP 2: Convert non-date columns to numeric
        non_date_cols = [col for col in df.columns if col != date_col]
        for col in non_date_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        if not non_date_cols:
            raise ValueError("No numeric column candidates found.")
        value_col = df[non_date_cols].count().idxmax()

        # STEP 3: Clean and standardize dataframe
        df = df[[date_col, value_col]]
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
        df['y'] = pd.to_numeric(df['y'], errors='coerce')
        df['y'] = df['y'].fillna(df['y'].mean())  # ✅ Avoid chained assignment warning
        df.dropna(subset=['ds'], inplace=True)

        if df.empty or len(df) < 5:
            raise ValueError("Not enough clean data to forecast.")

        # STEP 4: Set datetime index and fix frequency warning
        df.set_index('ds', inplace=True)
        inferred_freq = pd.infer_freq(df.index)
        if inferred_freq:
            df = df.asfreq(inferred_freq)

        # STEP 5: Fit ARIMA model
        model = ARIMA(df['y'], order=(5, 1, 0))
        model_fit = model.fit()

        # STEP 6: Generate daily forecast
        start_date = df.index[-1] + pd.Timedelta(days=1)
        forecast = model_fit.forecast(steps=days)
        forecast_df = pd.DataFrame({
            'ds': pd.date_range(start=start_date, periods=days, freq='D'),
            'yhat': forecast
        })

        # STEP 7: Aggregate if needed
        if granularity == 'month':
            forecast_df['month'] = forecast_df['ds'].dt.to_period('M')
            forecast_df = (
                forecast_df.groupby('month')['yhat']
                .mean().reset_index()
                .rename(columns={'month': 'ds'})
            )
            forecast_df['ds'] = forecast_df['ds'].dt.to_timestamp()

        elif granularity == 'year':
            forecast_df['year'] = forecast_df['ds'].dt.to_period('Y')
            forecast_df = (
                forecast_df.groupby('year')['yhat']
                .mean().reset_index()
                .rename(columns={'year': 'ds'})
            )
            forecast_df['ds'] = forecast_df['ds'].dt.to_timestamp()

        return forecast_df

    except Exception as e:
        return {"error": str(e)}
