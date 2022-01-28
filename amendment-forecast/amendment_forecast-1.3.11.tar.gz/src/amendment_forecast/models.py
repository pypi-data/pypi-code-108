# Class to extend for each model

import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

from fbprophet import Prophet
from greykite.framework.templates.autogen.forecast_config import ForecastConfig, MetadataParam, ModelComponentsParam, EvaluationPeriodParam
from greykite.framework.templates.forecaster import Forecaster
from greykite.framework.templates.model_templates import ModelTemplateEnum
from neuralprophet import NeuralProphet
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX

from amendment_forecast import utils
# import utils

# TODO Define loss_functions enum
LOSS_FUNCTIONS = [
    "MSE",
    "MAE",
    "MedAE",
    "MAPE",
    "MedAPE",
    "R2"
]
DATE_COLUMN_NAME = "period"
VALUE_COLUMN_NAME = "y"


class BaseModel:
    """Base class for models to run as part of ensemble"""

    def __init__(self) -> None:
        pass

    def run(self, dataframe: pd.DataFrame, **kwargs) -> tuple:
        pass

    def evaluate(self, dataframe: pd.DataFrame, train_end_date: datetime, frequency: str,
                 forecast_period_list: list) -> dict:
        """Function to evaluate the performance of the model against a particular dataset"""
        actual, predicted, forecast = self.run(
            dataframe=dataframe,
            train_end=train_end_date,
            frequency=frequency,
            forecast_period_list=forecast_period_list)
        result_package = {"name": self.__name__}
        result_package["performance_metrics"] = utils.get_model_statistics(y=actual, yhat=predicted)
        result_package["consolidated_metrics"] = utils.consolidate_scores(result_package["performance_metrics"], actual.mean())
        result_package["forecast_dataframe"] = pd.DataFrame(
                index=pd.Series(forecast.index),
                data={f"forecast_values_{self.__name__}": pd.Series(forecast).values})
        result_package["train_dataframe"] = pd.DataFrame(
                index=pd.Series(actual.index),
                data={
                    f"actual_values_{self.__name__}": actual.values,
                    f"predicted_values_{self.__name__}": predicted
                })

        return result_package


class GreyKite(BaseModel):

    def __init__(self):
        """Initializes greykite model"""
        super().__init__()
        self.__name__ = "GreyKite"
        self.metadata = MetadataParam(
            time_col=DATE_COLUMN_NAME,
            value_col=VALUE_COLUMN_NAME)

    def run(self, dataframe: pd.DataFrame, train_end: datetime, frequency: str, forecast_period_list: list) -> tuple:
        """Runs rolling prediction using the model to return actual and predicted values

        Args:
            dataframe: time series dataframe to evaluate the model on

        Returns:
            dataframes with actual and predicted values
        """
        forecaster = Forecaster()
        self.metadata.freq = frequency
        forecast_horizon=len(forecast_period_list)
        if forecast_horizon >= (len(dataframe) / 3):
            test_horizon = (len(dataframe) / 3) - 1
        else:
            test_horizon = forecast_horizon
        result = forecaster.run_forecast_config(  # result is also stored as `forecaster.forecast_result`.
            df=dataframe,
            config=ForecastConfig(
                model_components_param=ModelComponentsParam(seasonality={"yearly_seasonality": 40}),
                evaluation_period_param=EvaluationPeriodParam(test_horizon=test_horizon),
                model_template=ModelTemplateEnum.SILVERKITE.name,
                coverage=0.95,
                metadata_param=self.metadata,
                forecast_horizon=len(forecast_period_list)
            )
        )
        backtest = result.backtest.df_test[~result.backtest.df_test["actual"].isnull()]
        backtest = backtest[backtest[DATE_COLUMN_NAME] > train_end]
        backtest = backtest.set_index("period")
        forecast_df = result.forecast.df
        forecast_df = forecast_df.set_index("period")
        mask = forecast_df["actual"].isnull()
        forecast = forecast_df.loc[mask, "forecast"]

        return backtest["actual"], backtest["forecast"], forecast


class FBProphet(BaseModel):

    def __init__(self):
        """Initializes prophet model"""
        super().__init__()
        self.__name__ = "FBProphet"

    def run(self, dataframe: pd.DataFrame, train_end: datetime, frequency: str, forecast_period_list: list) -> tuple:
        """Runs rolling prediction using the model to return actual and predicted values

        Args:
            dataframe: time series dataframe to evaluate the model on

        Returns:
            dataframes with actual and predicted values
        """
        df = dataframe.rename(columns={DATE_COLUMN_NAME: "ds", VALUE_COLUMN_NAME: "y"})
        df["y"] = np.log(df["y"])

        model = Prophet(yearly_seasonality=10)
        model.fit(df, iter=1000)

        future = model.make_future_dataframe(periods=len(forecast_period_list), freq=frequency)
        forecast = model.predict(future)
        forecast = forecast.rename(columns={"ds": DATE_COLUMN_NAME}).set_index(DATE_COLUMN_NAME)

        df_forecast = pd.merge(dataframe.set_index(DATE_COLUMN_NAME), forecast, how="outer", left_index=True, right_index=True)
        df_train = df_forecast[~df_forecast[VALUE_COLUMN_NAME].isnull()]
        df_forecast = df_forecast[df_forecast[VALUE_COLUMN_NAME].isnull()]

        actual_values = df_train[VALUE_COLUMN_NAME]
        predicted_values = np.exp(df_train["yhat"])
        forecasted_values = np.exp(df_forecast["yhat"])

        return actual_values, predicted_values, forecasted_values


class FBNeuralProphet(BaseModel):

    def __init__(self):
        """Initializes prophet model"""
        super().__init__()
        self.__name__ = "FBNeuralProphet"

    def run(self, dataframe: pd.DataFrame, train_end: datetime, frequency: str, forecast_period_list: list) -> tuple:
        """Runs rolling prediction using the model to return actual and predicted values

        Args:
            dataframe: time series dataframe to evaluate the model on

        Returns:
            dataframes with actual and predicted values
        """
        df = dataframe.rename(columns={DATE_COLUMN_NAME: "ds", VALUE_COLUMN_NAME: "y"})

        model = NeuralProphet(yearly_seasonality=10)
        model.fit(df=df, freq=frequency)

        future = model.make_future_dataframe(
            df=df,
            periods=len(forecast_period_list),
            n_historic_predictions=len(df))
        forecast = model.predict(future)
        forecast = forecast.rename(columns={"ds": DATE_COLUMN_NAME}).set_index(DATE_COLUMN_NAME)

        df_forecast = pd.merge(
            left=dataframe.set_index(DATE_COLUMN_NAME),
            right=forecast.drop(columns=["y"]),
            how="outer",
            left_index=True,
            right_index=True)
        df_train = df_forecast[~df_forecast[VALUE_COLUMN_NAME].isnull()]
        df_forecast = df_forecast[df_forecast[VALUE_COLUMN_NAME].isnull()]

        actual_values = df_train[VALUE_COLUMN_NAME]
        predicted_values = df_train["yhat1"]
        forecasted_values = df_forecast["yhat1"]

        return actual_values, predicted_values, forecasted_values


class Naive(BaseModel):

    def __init__(self):
        """Initializes naive model"""
        super().__init__()
        self.__name__ = "Naive"
        self.growth_comparison_period_in_years = 1
        self.minimum_training_years = 2

    def run(self, dataframe: pd.DataFrame, train_end: datetime, frequency: str, forecast_period_list: list) -> tuple:
        # Determine training and testing periods to create test and training dataframes
        comparison_period_relativedelta = relativedelta(years=self.growth_comparison_period_in_years)
        train_mask = dataframe[DATE_COLUMN_NAME] <= train_end
        dataframe_test = dataframe[~train_mask]

        def get_growth(dataframe, base_start, base_end, comparison_start, comparison_end):
            # Calculate base period totals
            base_growth_period_mask = \
                (dataframe[DATE_COLUMN_NAME] >= base_start) & \
                (dataframe[DATE_COLUMN_NAME] < base_end)
            base_growth_period_sum = dataframe.loc[base_growth_period_mask, VALUE_COLUMN_NAME].sum()

            # Calculate comparison period totals
            comparison_growth_period_mask = \
                (dataframe[DATE_COLUMN_NAME] >= comparison_start) & \
                (dataframe[DATE_COLUMN_NAME] < comparison_end)
            comparison_growth_period_sum = dataframe.loc[comparison_growth_period_mask, VALUE_COLUMN_NAME].sum()
            # Determine growth_rate as the total change in volume from the base period to the comparison period
            growth_rate = comparison_growth_period_sum / base_growth_period_sum

            return growth_rate

        def run_prediction(prediction_date, frequency):
            training_dataframe = dataframe[dataframe[DATE_COLUMN_NAME] < prediction_date]

            # Handle cases where less data is available
            available_comparison_period = training_dataframe[DATE_COLUMN_NAME].max() - training_dataframe[DATE_COLUMN_NAME].min()
            available_comparison_years = available_comparison_period / np.timedelta64(1, 'Y')
            if available_comparison_years < self.minimum_training_years:
                if available_comparison_years > 1:
                    # Handle rolling comparison
                    # Use defaults if that amount of time is available
                    base_growth_period_start = training_dataframe[DATE_COLUMN_NAME].min()
                    base_growth_period_end = prediction_date + relativedelta(years=-1)
                    comparison_growth_period_start = base_growth_period_start + relativedelta(years=1)

                    # Previous value comes from the day after the base_growth period ends
                    growth_rate = get_growth(
                        dataframe=training_dataframe,
                        base_start=base_growth_period_start,
                        base_end=base_growth_period_end,
                        comparison_start=comparison_growth_period_start,
                        comparison_end=prediction_date
                    )
                    # Get date after end of base period
                    base_mask = training_dataframe[DATE_COLUMN_NAME] < base_growth_period_end
                    previous_date = training_dataframe[~base_mask][DATE_COLUMN_NAME].min()
                    previous_value_mask = dataframe[DATE_COLUMN_NAME] == previous_date
                    previous_value = dataframe.loc[previous_value_mask, VALUE_COLUMN_NAME].sum()

                else:
                    # Growth is linear from beginning to end
                    start_value = training_dataframe.loc[training_dataframe[DATE_COLUMN_NAME] == training_dataframe[DATE_COLUMN_NAME].min(), VALUE_COLUMN_NAME].sum()
                    end_value = training_dataframe.loc[training_dataframe[DATE_COLUMN_NAME] == training_dataframe[DATE_COLUMN_NAME].max(), VALUE_COLUMN_NAME].sum()
                    growth_rate = (((end_value - start_value) / len(training_dataframe)) / end_value) + 1
                    previous_value = end_value
            # Otherwise we can use a normal y/y comparison
            else:
                # Use defaults if that amount of time is available
                base_growth_period_start = prediction_date - (2 * comparison_period_relativedelta)
                comparison_growth_period_start = prediction_date - comparison_period_relativedelta

                growth_rate = get_growth(
                    dataframe=dataframe,
                    base_start=base_growth_period_start,
                    base_end=comparison_growth_period_start,
                    comparison_start=comparison_growth_period_start,
                    comparison_end=prediction_date
                )

                # Determine value to use as the base for the estimation
                if frequency == "W-MON":
                    comparison_growth_period_start = comparison_growth_period_start - relativedelta(days=(comparison_growth_period_start.weekday()))
                previous_value_mask = dataframe[DATE_COLUMN_NAME] == comparison_growth_period_start
                previous_value = dataframe.loc[previous_value_mask, VALUE_COLUMN_NAME].sum()

            return previous_value * growth_rate

        # Loop through individual values
        actual = []
        predicted = []
        for index, row in dataframe_test.iterrows():
            # Determine window to evaluate against for the test datapoint
            prediction_date = row[DATE_COLUMN_NAME]
            predicted_value = run_prediction(prediction_date, frequency)

            # Save prediction
            actual.append(dataframe.loc[index, VALUE_COLUMN_NAME])
            predicted.append(predicted_value)

        forecast = []
        for timestamp in forecast_period_list:
            forecast_value = run_prediction(timestamp, frequency)
            forecast.append(forecast_value)
            new_row = pd.DataFrame({DATE_COLUMN_NAME: [timestamp], "yhat": [forecast_value]})
            dataframe = pd.concat([dataframe, new_row]).reset_index(drop=True)
            mask = dataframe[VALUE_COLUMN_NAME].isnull()
            dataframe.loc[mask, VALUE_COLUMN_NAME] = dataframe.loc[mask, "yhat"]

        dataframe_test["predicted"] = predicted
        dataframe_test = dataframe_test.set_index("period")
        dataframe_test = dataframe_test[np.isfinite(dataframe_test).all(axis=1)]

        dataframe = dataframe.set_index("period")

        return dataframe_test[VALUE_COLUMN_NAME], dataframe_test["predicted"], dataframe["yhat"]


class XGBoost(BaseModel):
    OBJECTIVE = "reg:squarederror"
    N_ESTIMATORS = 100
    PREVIOUS_PERIODS = 0

    def __init__(self):
        """Initializes xgboost model"""
        super().__init__()
        self.__name__ = "XGBoost"

    def create_time_series_features(self, time_series_df, frequency, backtest=False):
        result_df = time_series_df.copy()
        if frequency == "W-MON":
            self.PREVIOUS_PERIODS = 53
            result_df["year"] = result_df.index.year
            result_df["period_number"] = result_df.index.isocalendar().week.astype(str)
        else:
            self.PREVIOUS_PERIODS = 12
            result_df["period_number"] = result_df.index.month.astype(str)
        previous_periods = self.PREVIOUS_PERIODS
        if backtest:
            if len(result_df) < (2 * self.PREVIOUS_PERIODS):
                previous_periods = int(len(result_df) / 2)
        for ii in range(1, previous_periods):
            # Create recent lag periods
            result_df[f"{VALUE_COLUMN_NAME}_{ii}"] = time_series_df[VALUE_COLUMN_NAME].shift(ii)
        period_indexes = pd.get_dummies(result_df.period_number)
        mask = True
        for column in result_df.columns:
            mask = mask & (~result_df[column].isnull())
        dataframe = pd.merge(left=result_df, right=period_indexes, how="left", left_index=True, right_index=True)
        dataframe = dataframe[mask].drop(columns=["period_number"])

        return dataframe

    def step_forecast(self, train_df: pd.DataFrame, test_x: pd.DataFrame, feature_columns: list):
        # fit a xgboost model and make a one step prediction
        # split into input and output columns
        train_x = train_df[feature_columns]
        train_y = train_df[VALUE_COLUMN_NAME]
        # fit model
        model = XGBRegressor(objective=self.OBJECTIVE, n_estimators=self.N_ESTIMATORS)
        model.fit(train_x, train_y)

        # make a one-step prediction
        yhat = model.predict(test_x)

        return yhat[0]

    def full_forecast(self, train_df, feature_columns, forecast_period_list, frequency):
        # fit an xgboost model and make a prediction for the full forecast_horizon
        # split into input and output columns
        train_x = train_df[feature_columns]
        train_y = train_df[VALUE_COLUMN_NAME]

        # fit model
        model = XGBRegressor(objective=self.OBJECTIVE, n_estimators=self.N_ESTIMATORS)
        model.fit(train_x, train_y)

        cc = 0
        previous_record = train_df.rename(columns={"y": "y_0"}).iloc[-1]
        predictions = {}
        for period in forecast_period_list:
            # Initialize previous period
            if cc == 0:
                test_record = previous_record.copy()
                # Update period IDs
                period_id_columns = [col for col in previous_record.index.values if "_" not in col]
                test_record[period_id_columns] = 0
                if frequency == "W-MON":
                    period_id = forecast_period_list[cc].isocalendar()[1]
                else:
                    period_id = forecast_period_list[cc].month
                test_record[str(period_id)] = 1
            else:
                # Copy previous record and update period_id
                previous_record = test_record.copy()
                # Update period IDs
                test_record[str(period_id)] = 0
                if frequency == "W-MON":
                    period_id = forecast_period_list[cc].isocalendar()[1]
                else:
                    period_id = forecast_period_list[cc].month
                test_record[str(period_id)] = 1
            # Update previous values
            for ii in range(0, self.PREVIOUS_PERIODS):
                test_record[f"y_{ii + 1}"] = previous_record[f"y_{ii}"]

            test_x = pd.DataFrame(test_record[feature_columns]).T

            # Run Forecast
            prediction = model.predict(test_x)
            test_record["y_0"] = prediction
            predictions[period] = prediction[0]

            cc += 1
        predictions = pd.Series(predictions)

        return predictions

    def run(self, dataframe: pd.DataFrame, train_end: datetime, frequency: str,
            forecast_period_list: pd.DataFrame) -> tuple:
        original_dataframe = dataframe.copy()

        # Prepare dataframe for backtest
        backfill_dataframe = utils.create_backfill_time_series(original_dataframe, frequency)
        backfill_dataframe = pd.concat([original_dataframe, backfill_dataframe]).sort_values(by="period")
        backfill_dataframe = backfill_dataframe.set_index("period").asfreq(frequency)

        # Parse original dataframe for usage later
        dataframe = original_dataframe.set_index("period").asfreq(frequency)

        # Prepare dataframe
        dataframe_backtest = self.create_time_series_features(backfill_dataframe, frequency, backtest=True)

        predicted = []
        # Split into train and test
        if train_end < dataframe_backtest.index.min():
            train_end = dataframe_backtest.index.min()
        train_mask = dataframe_backtest.index <= train_end
        train = dataframe_backtest[train_mask]
        test = dataframe_backtest[~train_mask]
        feature_columns = list(set(dataframe_backtest.columns) - set(VALUE_COLUMN_NAME))

        # Step over each time period and get result
        for index, row in test.iterrows():
            # split test row into input and output columns
            X, y = pd.DataFrame(row[feature_columns]).T, row[VALUE_COLUMN_NAME]

            # fit model on history and make a prediction
            yhat = self.step_forecast(train, X, feature_columns)

            # store forecast in list of predictions
            predicted.append(yhat)

            # add actual observation to history for the next loop
            train = pd.concat([train, pd.DataFrame(row).T])

        # Run full forecast
        dataframe_forecast = self.create_time_series_features(dataframe, frequency, backtest=False)
        forecast_predictions = self.full_forecast(dataframe_forecast, feature_columns, forecast_period_list, frequency)

        return test[VALUE_COLUMN_NAME], predicted, forecast_predictions


class RandomForest(BaseModel):
    N_ESTIMATORS = 100
    PREVIOUS_PERIODS = 0

    def __init__(self):
        """Initializes random forest model"""
        super().__init__()
        self.__name__ = "RandomForest"

    def create_time_series_features(self, time_series_df, frequency, backtest=False):
        result_df = time_series_df.copy()
        if frequency == "W-MON":
            self.PREVIOUS_PERIODS = 53
            result_df["year"] = result_df.index.year
            result_df["period_number"] = result_df.index.isocalendar().week.astype(str)
        else:
            self.PREVIOUS_PERIODS = 12
            result_df["period_number"] = result_df.index.month.astype(str)
        previous_periods = self.PREVIOUS_PERIODS
        if backtest:
            if len(result_df) < (2 * self.PREVIOUS_PERIODS):
                previous_periods = int(len(result_df) / 2)
        for ii in range(1, previous_periods):
            # Create recent lag periods
            result_df[f"{VALUE_COLUMN_NAME}_{ii}"] = time_series_df[VALUE_COLUMN_NAME].shift(ii)
        period_indexes = pd.get_dummies(result_df.period_number)
        mask = True
        for column in result_df.columns:
            mask = mask & (~result_df[column].isnull())
        dataframe = pd.merge(left=result_df, right=period_indexes, how="left", left_index=True, right_index=True)
        dataframe = dataframe[mask].drop(columns=["period_number"])

        return dataframe

    def step_forecast(self, train_df: pd.DataFrame, test_x: pd.DataFrame, feature_columns: list):
        # fit a rf model and make a one step prediction
        # split into input and output columns
        train_x = train_df[feature_columns]
        train_y = train_df[VALUE_COLUMN_NAME]
        # fit model
        model = RandomForestRegressor(n_estimators=self.N_ESTIMATORS)
        model.fit(train_x, train_y)

        # make a one-step prediction
        yhat = model.predict(test_x)

        return yhat[0]

    def full_forecast(self, train_df, feature_columns, forecast_period_list, frequency):
        # fit an xgboost model and make a prediction for the full forecast_horizon
        # split into input and output columns
        train_x = train_df[feature_columns]
        train_y = train_df[VALUE_COLUMN_NAME]

        # fit model
        model = RandomForestRegressor(n_estimators=self.N_ESTIMATORS)
        model.fit(train_x, train_y)

        cc = 0
        previous_record = train_df.rename(columns={"y": "y_0"}).iloc[-1]
        predictions = {}
        for period in forecast_period_list:
            # Initialize previous period
            if cc == 0:
                test_record = previous_record.copy()
                # Update period IDs
                period_id_columns = [col for col in previous_record.index.values if "_" not in col]
                test_record[period_id_columns] = 0
                if frequency == "W-MON":
                    period_id = forecast_period_list[cc].isocalendar()[1]
                else:
                    period_id = forecast_period_list[cc].month
                test_record[str(period_id)] = 1
            else:
                # Copy previous record and update period_id
                previous_record = test_record.copy()
                # Update period IDs
                test_record[str(period_id)] = 0
                if frequency == "W-MON":
                    period_id = forecast_period_list[cc].isocalendar()[1]
                else:
                    period_id = forecast_period_list[cc].month
                test_record[str(period_id)] = 1
            # Update previous values
            for ii in range(0, self.PREVIOUS_PERIODS):
                test_record[f"y_{ii + 1}"] = previous_record[f"y_{ii}"]

            test_x = pd.DataFrame(test_record[feature_columns]).T

            # Run Forecast
            prediction = model.predict(test_x)
            test_record["y_0"] = prediction
            predictions[period] = prediction[0]

            cc += 1
        predictions = pd.Series(predictions)

        return predictions

    def run(self, dataframe: pd.DataFrame, train_end: datetime, frequency: str,
            forecast_period_list: pd.DataFrame) -> tuple:
        original_dataframe = dataframe.copy()

        # Prepare dataframe for backtest
        backfill_dataframe = utils.create_backfill_time_series(original_dataframe, frequency)
        backfill_dataframe = pd.concat([original_dataframe, backfill_dataframe]).sort_values(by="period")
        backfill_dataframe = backfill_dataframe.set_index("period").asfreq(frequency)

        # Parse original dataframe for usage later
        dataframe = original_dataframe.set_index("period").asfreq(frequency)

        # Prepare dataframe
        dataframe_backtest = self.create_time_series_features(backfill_dataframe, frequency, backtest=True)

        predicted = []
        # Split into train and test
        if train_end < dataframe_backtest.index.min():
            train_end = dataframe_backtest.index.min()
        train_mask = dataframe_backtest.index <= train_end
        train = dataframe_backtest[train_mask]
        test = dataframe_backtest[~train_mask]
        feature_columns = list(set(dataframe_backtest.columns) - set(VALUE_COLUMN_NAME))

        # Step over each time period and get result
        for index, row in test.iterrows():
            # split test row into input and output columns
            X, y = pd.DataFrame(row[feature_columns]).T, row[VALUE_COLUMN_NAME]

            # fit model on history and make a prediction
            yhat = self.step_forecast(train, X, feature_columns)

            # store forecast in list of predictions
            predicted.append(yhat)

            # add actual observation to history for the next loop
            train = pd.concat([train, pd.DataFrame(row).T])

        # Run full forecast
        dataframe_forecast = self.create_time_series_features(dataframe, frequency, backtest=False)
        forecast_predictions = self.full_forecast(dataframe_forecast, feature_columns, forecast_period_list, frequency)

        return test[VALUE_COLUMN_NAME], predicted, forecast_predictions


class SARIMA(BaseModel):

    def __init__(self):
        """Initializes SARIMA model"""
        super().__init__()
        self.__name__ = "SARIMA"

    def run(self, dataframe: pd.DataFrame, train_end: datetime, frequency: str, forecast_period_list: list) -> tuple:
        original_dataframe = dataframe.copy()

        # Prepare dataframe for backtest
        backfill_dataframe = utils.create_backfill_time_series(original_dataframe, frequency)
        backfill_dataframe = pd.concat([original_dataframe, backfill_dataframe]).sort_values(by="period")
        dataframe_backtest = backfill_dataframe.set_index("period").asfreq(frequency)

        # Parse original dataframe for usage later
        dataframe = original_dataframe.set_index("period").asfreq(frequency)

        if frequency == "W-MON":
            m = 52.5
        elif frequency == "MS":
            m = 12

        # Split into train and test
        # Check if enough data is provided to train on a full year
        train_start = dataframe_backtest.index.min()
        if (train_end - train_start).days < 365:
            if (dataframe_backtest.index.max() - train_start).days > 540:
                train_end = train_start + relativedelta(years=1)
        train_mask = dataframe_backtest.index <= train_end
        train = dataframe_backtest[train_mask]
        test = dataframe_backtest[~train_mask]

        # Create step-forward validation
        predicted = pd.DataFrame()
        previous_index = 0
        period_horizon = int(len(forecast_period_list) / 10)

        if period_horizon <= len(test):
            start = period_horizon
            end = len(test)
            step = period_horizon
        else:
            start = len(test)
            end = len(test) + 1
            step = len(test)
        backtest_range = range(start, end, step)
        for ii in backtest_range:
            model = SARIMAX(train, order=(1, 1, 2), seasonal_order=(1, 1, 2, m))
            results = model.fit(method='powell', disp=False)

            # Identify subset of test to forecast against
            test_subset = test.iloc[previous_index:ii]
            previous_index = ii

            # Create predictions and add to list
            predictions = pd.DataFrame(index=test_subset.index, data=results.forecast(steps=step).values)
            predicted = pd.concat([predicted, predictions])

            # Update training dataset
            train = pd.concat([train, test_subset])

            # Handle final test records
            if ((len(test) - ii) < step) & (len(test) - ii > 0):
                model = SARIMAX(train, order=(1, 1, 2), seasonal_order=(1, 1, 2, m))
                results = model.fit(method='powell')

                # Identify subset of test to forecast against
                test_subset = test.iloc[ii:]
                train = pd.concat([train, test_subset])

                # Create predictions and add to list
                predictions = pd.DataFrame(index=test_subset.index,
                                           data=results.forecast(steps=len(test_subset)).values)
                predicted = pd.concat([predicted, predictions])
        predicted[0] = predicted[0].apply(lambda x: x if x > 0 else 1)

        # Create future forecast
        model = SARIMAX(dataframe, order=(1, 1, 2), seasonal_order=(1, 1, 2, m))
        results = model.fit(method='powell', disp=False)
        predictions = results.forecast(steps=len(forecast_period_list))

        forecast = pd.Series(index=forecast_period_list, data=predictions)
        forecast = forecast.apply(lambda x: x if x > 0 else 1)

        return test[VALUE_COLUMN_NAME], predicted[0].values, forecast


def initialize_model(model_name: str):
    named_model = [model for model in BaseModel.__subclasses__() if model_name == model.__name__][0]
    model = named_model()

    return model
