from typing import Any

import pandas as pd

from qpd_pandas import QPDPandasEngine
from qpd_test.benchmark_suite import BenchmarkTests


class PandasBenchmarkTests(BenchmarkTests.Tests):
    def _test_select(self):
        for n, q, s in self._test_select(10, 100, 1000, 10000, repeat=3):
            print(n, q, s)

    def test_select_where(self):
        for n, q, s in self._test_select_where(10, 100, 1000, 10000, 100000, repeat=3):
            print(n, q, s)

    def _test_integration_1(self):
        for n, q, s in self._test_integration_1(10, 100, 1000, repeat=3):
            print(n, q, s)

    def make_qpd_engine(self):
        return QPDPandasEngine()

    def to_native_df(self, data: Any, columns: Any) -> Any:  # pragma: no cover
        if isinstance(data, pd.DataFrame):
            return data
        return pd.DataFrame(data, columns=columns)
