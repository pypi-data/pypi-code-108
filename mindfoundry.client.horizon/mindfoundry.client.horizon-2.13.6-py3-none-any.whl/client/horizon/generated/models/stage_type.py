from enum import Enum


class StageType(str, Enum):
    FEATURE_GENERATION = "feature_generation"
    FILTERING = "filtering"
    PROBLEM_SPECIFICATION = "problem_specification"
    STATIONARISATION = "stationarisation"
    BACKTEST = "backtest"
    LSTM_BACKTEST = "lstm_backtest"
    REFINEMENT = "refinement"
    PREDICTION = "prediction"
    LSTM_PREDICTION = "lstm_prediction"
    TRADING_SPECIFICATION = "trading_specification"
    TRADING_SIMULATION = "trading_simulation"
    CLASSIFICATION_SPECIFICATION = "classification_specification"
    CLASSIFICATION_DISCOVERY = "classification_discovery"
    CLASSIFICATION_BACKTEST = "classification_backtest"

    def __str__(self) -> str:
        return str(self.value)
