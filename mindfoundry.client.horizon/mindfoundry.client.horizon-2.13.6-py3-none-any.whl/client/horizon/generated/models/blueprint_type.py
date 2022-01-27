from enum import Enum


class BlueprintType(str, Enum):
    NONLINEAR = "nonlinear"
    LINEAR = "linear"
    SMALL_DATA = "small_data"
    FAST_FORECASTING = "fast_forecasting"
    LSTM = "lstm"
    TRADING_SIMULATION = "trading_simulation"
    FEATURE_SELECTION = "feature_selection"
    FEATURE_DISCOVERY = "feature_discovery"
    SIGNAL_ENCODING = "signal_encoding"
    VARIATIONAL_FORECASTING = "variational_forecasting"
    STATIONARISATION = "stationarisation"
    TIME_SERIES_REGRESSION = "time_series_regression"
    CLASSIFICATION = "classification"
    CUSTOM = "custom"

    def __str__(self) -> str:
        return str(self.value)
