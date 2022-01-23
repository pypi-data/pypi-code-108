from __future__ import annotations
from badook_tests.dsl.summary import Summary
from badook_tests.dsl.checks import Calculation


class TimeSeriesAnalysisSummary(Summary):
    def __init__(self, features: str, name: str, window_size: int, n_mads_allowed: float, time_column: str = None):
        super().__init__(features, name)
        if not isinstance(features, str):
            raise Exception(
                "Feature name for Hampel filter must be a string")
        self.type = 'TimeSeriesAnalysisSummary'
        self.window_size = window_size
        self.n_mads_allowed = n_mads_allowed
        self.time_column = time_column
        self.partitions = None
        self.agg = None

    @property
    def value(self):
        return Calculation(self.data, 'value', self._ctx)

    @property
    def window_rolling_median(self):
        return Calculation(self.data, 'window_rolling_median', self._ctx)

    @property
    def window_rolling_mad(self):
        return Calculation(self.data, 'window_rolling_MAD', self._ctx)

    @property
    def window_lower_boundary(self):
        return Calculation(self.data, 'window_lower_boundary', self._ctx)

    @property
    def window_upper_boundary(self):
        return Calculation(self.data, 'window_upper_boundary', self._ctx)

    @property
    def is_outlier(self):
        return Calculation(self.data, 'is_outlier', self._ctx)

    def partition_by(self, *args) -> Summary:
        self.partitions = list(args)
        return self

    def set_agg(self, agg: str) -> Summary:
        self.agg = agg
        return self
