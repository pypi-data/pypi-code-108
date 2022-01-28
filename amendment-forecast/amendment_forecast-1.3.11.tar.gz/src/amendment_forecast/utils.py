import pandas as pd
from sklearn import metrics
from datetime import timedelta

from amendment_forecast.models import DATE_COLUMN_NAME, VALUE_COLUMN_NAME
# from models import DATE_COLUMN_NAME, VALUE_COLUMN_NAME


def apply_lag(dataframe, columns, lag):
    for column in columns:
        lag_column = dataframe[column].copy() * lag
        dataframe[column] = dataframe[column] - lag_column
        dataframe[column] = dataframe[column] + lag_column.shift(-1)

    return dataframe


def create_time_series_from_records(df: pd.DataFrame, column_name: str, operation: str, period_format: str = None):
    if period_format:
        df[DATE_COLUMN_NAME] = df[DATE_COLUMN_NAME].dt.strftime(period_format)
        if period_format == "%Y-%W":
            df[DATE_COLUMN_NAME] = pd.to_datetime(df[DATE_COLUMN_NAME].map(lambda x: str(x) + "-0"), format="%Y-%W-%w")
        else:
            df[DATE_COLUMN_NAME] = pd.to_datetime(df[DATE_COLUMN_NAME])
    time_series_df = df.groupby(DATE_COLUMN_NAME, as_index=False).agg({column_name: operation})
    time_series_df.rename(columns={column_name: VALUE_COLUMN_NAME}, inplace=True)

    return time_series_df


def get_model_statistics(y: pd.Series, yhat: pd.Series):
    scores = {
        "mape": metrics.mean_absolute_percentage_error(y, yhat),
        "mae": metrics.mean_absolute_error(y, yhat),
        "mse": metrics.mean_squared_error(y, yhat),
        "rmse": metrics.mean_squared_error(y, yhat, squared=False),
        "r2": metrics.r2_score(y, yhat),
        "medae": metrics.median_absolute_error(y, yhat)
    }

    return scores


def consolidate_scores(metrics: dict, average_actual: float):
    metrics["accuracy_mape"] = 1 - metrics["mape"]
    metrics["accuracy_rmse"] = 1 - (metrics["rmse"] / average_actual)
    metrics["accuracy_mae"] = 1 - (metrics["mae"] / average_actual)
    metrics["accuracy_medae"] = 1 - (metrics["medae"] / average_actual)

    metrics["ae_composite"] = (metrics["accuracy_mae"] + metrics["accuracy_medae"]) / 2
    metrics["accuracy"] = (metrics["ae_composite"] + metrics["accuracy_mape"] + metrics["accuracy_rmse"]) / 3

    metrics["fit"] = metrics["r2"]

    return_metrics = ["accuracy_mape", "accuracy_rmse", "accuracy_mae", "accuracy_medae", "accuracy", "fit"]

    return {metric: metrics[metric] for metric in return_metrics}


def create_backfill_time_series(original_df, frequency):
    curve_df = original_df.copy()

    days_provided = (curve_df["period"].max() - curve_df["period"].min()).days

    # Get Y/Y Percentage
    last_year_start = curve_df["period"].max() - timedelta(days=365)
    last_full_year_mask = curve_df["period"] >= last_year_start
    first_year_end = curve_df["period"].min() + timedelta(days=365)
    first_full_year_mask = curve_df["period"] <= first_year_end

    total_growth = curve_df[last_full_year_mask].y.sum() / curve_df[first_full_year_mask].y.sum()
    annual_growth = total_growth / ((days_provided - 365) / 365)

    # Fill in dates
    curve_df["week"] = curve_df["period"].dt.isocalendar().week
    curve_df["year"] = curve_df["period"].dt.isocalendar().year

    data_start = curve_df["period"].min()
    fillin_start = data_start - timedelta(days=365)
    missing_dates = list(pd.date_range(fillin_start, data_start, freq=frequency))
    missing_dates = [date for date in missing_dates if date < data_start]

    # Loop through and add fillin rows
    rows = []
    for missing_date in missing_dates:
        # Get corresponding provided value
        period_value = missing_date.isocalendar()[1]
        period_year = missing_date.isocalendar()[0]
        period_mask = curve_df["week"] == period_value
        year_mask = curve_df["year"] == (period_year + 1)
        df_compare = curve_df[period_mask & year_mask]

        if len(df_compare) > 0:
            row = {
                "period": missing_date,
                "y": df_compare["y"].values[0] / annual_growth
            }
            rows.append(row)

    df_backfill = pd.DataFrame(rows)[["period", "y"]].rolling(
        window=3,
        min_periods=0,
        on="period").mean()

    return df_backfill
