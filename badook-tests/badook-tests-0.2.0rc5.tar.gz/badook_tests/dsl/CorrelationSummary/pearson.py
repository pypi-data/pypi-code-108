from __future__ import annotations
from badook_tests.dsl.summary import Summary
from badook_tests.dsl.checks import Calculation


class Pearson(Summary):
    def __init__(self, features: list, name: str):
        super().__init__(features, name)
        if len(features) < 2:
            raise Exception(
                "Feature list in correlation summary must include at least two features.")
        self.method = 'pearson'
        self.type = 'CorrelationSummary'

    @property
    def r_coeff(self):
        return Calculation(self.data, 'r_coeff', self._ctx)
