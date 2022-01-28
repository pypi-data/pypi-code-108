# main runner
import pandas as pd
from dateutil.relativedelta import relativedelta

from amendment_forecast import utils
from amendment_forecast.models import DATE_COLUMN_NAME, VALUE_COLUMN_NAME, initialize_model
# import utils
# from models import DATE_COLUMN_NAME, VALUE_COLUMN_NAME, initialize_model

FREQUENCY_MAPPING = {
    "week": "W-MON",
    "month": "MS"
}


def get_train_end_date(time_series_df, training_holdout):
    """ Determines the start date for the test data and throws a warning if less than 1 year of training data is included
    """
    training_rows = int(len(time_series_df) * training_holdout)
    train_end_date = time_series_df.iloc[training_rows][DATE_COLUMN_NAME]

    if (train_end_date - time_series_df[DATE_COLUMN_NAME].min()).days < 365:
        print("Warning: Less than 1 year of data provided for training")

    return train_end_date


def run_forecast_ensemble(
        dataframe,
        date_column,
        target_column,
        forecast_horizon_years,
        aggregate_operation="sum",
        training_holdout_pct=0.3,
        frequency="week",
        period_format=None,
        model_list=None,
        prediction_lag=0.0):
    # Initialize with copy of input date
    dataframe[DATE_COLUMN_NAME] = pd.to_datetime(dataframe[date_column])
    df = dataframe.copy()

    # Creates time series and ensures proper naming and frequency
    frequency = FREQUENCY_MAPPING.get(frequency)
    df = utils.create_time_series_from_records(
        df,
        target_column,
        aggregate_operation,
        period_format)
    df = df[[DATE_COLUMN_NAME, VALUE_COLUMN_NAME]]

    # Create Future Forecast Periods
    start_date = pd.to_datetime(dataframe[DATE_COLUMN_NAME]).max() + relativedelta(days=1)
    end_date = start_date + relativedelta(years=forecast_horizon_years)
    # Add additional period if lag is requested
    if prediction_lag != 0:
        if frequency == "W-MON":
            delta = relativedelta(days=7)
        elif frequency == "MS":
            delta = relativedelta(months=1)
        end_date = end_date + delta
    period_list = pd.date_range(start=start_date, end=end_date, freq=frequency)

    # Mark dataframe with training/testing split
    train_end_date = get_train_end_date(df, training_holdout_pct)

    # Assemble ensemble of models
    if model_list:
        named_model_list = model_list
    else:
        named_model_list = [
            "GreyKite",
            "FBProphet",
            "Naive",
            "XGBoost",
            "RandomForest",
            "SARIMA"
        ]

    # For each model, run a full evaluation and add to the ensemble results
    ensemble = []
    for model_name in named_model_list:
        print(f"    Running --{model_name}")
        model = initialize_model(model_name)
        model_dict = model.evaluate(
            dataframe=df,
            train_end_date=train_end_date,
            frequency=frequency,
            forecast_period_list=period_list)
        weight = model_dict["performance_metrics"]["r2"]
        if weight < 0:
            weight = 0
        elif model_name == "Naive":
            weight = 0
        model_dict["weight"] = weight
        ensemble.append(model_dict)

    # Combine outputs to calculate ensemble effectiveness
    print("Creating Ensemble")
    total_weight = sum([model["weight"] for model in ensemble])
    if total_weight == 0:
        total_weight = 1
    return_dataframe = df.copy().set_index(DATE_COLUMN_NAME)
    for model in ensemble:
        model["weight"] = model["weight"] / total_weight
        return_dataframe = pd.merge(
            left=return_dataframe,
            right=model["forecast_dataframe"],
            how="outer",
            left_index=True,
            right_index=True)
        if model["weight"] > 0:
            train_df = model["train_dataframe"]
            train_df[f"weighted_predicted_values_{model['name']}"] = train_df[f"predicted_values_{model['name']}"] * model["weight"]
            return_dataframe = pd.merge(
                left=return_dataframe,
                right=model["train_dataframe"],
                how="outer",
                left_index=True,
                right_index=True)
            forecast_df = model["forecast_dataframe"]
            forecast_df[f"forecast_values_{model['name']}"] = forecast_df[f"forecast_values_{model['name']}"] * model["weight"]
            forecast_df.rename(columns={f"forecast_values_{model['name']}": f"weighted_forecast_values_{model['name']}"}, inplace=True)
            return_dataframe = pd.merge(
                left=return_dataframe,
                right=forecast_df[[f"weighted_forecast_values_{model['name']}"]],
                how="outer",
                left_index=True,
                right_index=True)
    # Create Ensemble Predictions
    ensemble_prediction_columns = [column for column in return_dataframe.columns if column.startswith("weighted_predicted_values")]
    ensemble_prediction_eval = " + ".join(ensemble_prediction_columns)
    return_dataframe["predicted_values_Ensemble"] = return_dataframe.eval(ensemble_prediction_eval)

    # Create ensemble weighted forecast
    ensemble_forecast_columns = [column for column in return_dataframe.columns if column.startswith("weighted_forecast_values")]
    ensemble_forecast_eval = " + ".join(ensemble_forecast_columns)
    return_dataframe["forecast_values_Ensemble"] = return_dataframe.eval(ensemble_forecast_eval)
    forecast_columns = [column for column in return_dataframe.columns if column.startswith("forecast_values")]
    if prediction_lag != 0:
        return_dataframe = utils.apply_lag(return_dataframe, forecast_columns, prediction_lag)

    # Calculate ensemble metrics
    ensemble_train_df = return_dataframe[~return_dataframe["predicted_values_Ensemble"].isnull()]
    performance_metrics = utils.get_model_statistics(ensemble_train_df["predicted_values_Ensemble"], ensemble_train_df["y"])
    consolidated_metrics = utils.consolidate_scores(performance_metrics, ensemble_train_df["y"].mean())

    # Filter to only the required columns
    return_columns = ["y"] + forecast_columns
    return_dataframe = return_dataframe[return_columns]

    # Add ensemble to list
    ensemble.append({
        "name": "ensemble",
        "ensemble_dataframe": return_dataframe,
        "performance_metrics": performance_metrics,
        "consolidated_metrics": consolidated_metrics
    })

    # Create degraded accuracies for all models
    training_years = (df[DATE_COLUMN_NAME].max() - df[DATE_COLUMN_NAME].min()).days / 365
    for model in ensemble:
        degraded_accuracies = {}
        degraded_fit = {}
        for year in range(1, forecast_horizon_years + 1):
            multiplier = 1.0
            years_outside_of_training = max(year - training_years, 0)
            if years_outside_of_training > 0:
                for yy in range(1, int(year) + 1):
                    if yy > (2 * training_years):
                        multiplier *= 0.5
                    elif yy > training_years:
                        multiplier *= 0.95
            degraded_accuracies[year] = multiplier * model["consolidated_metrics"]["accuracy"]
            degraded_fit[year] = multiplier * model["consolidated_metrics"]["fit"]
        model["degraded_accuracies"] = degraded_accuracies
        model["degraded_fit"] = degraded_fit

    return ensemble
