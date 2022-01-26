from abc import ABC, abstractmethod

class SROMTimeSeriesForecaster(ABC):
    """
    == BASE / ABSTRACT == \
    An Forecaster class implements the default version of the pipeline which other Auto pipelines \
    will build upon.
    """

    @abstractmethod
    def fit(self, X, y=None):
        pass

    @abstractmethod
    def predict(self, X):
        pass
