from __future__ import annotations
from badook_tests.dsl.summary import Summary
from badook_tests.dsl.checks import Calculation


class LabelSummary(Summary):
    def __init__(self, features: list, name: str):
        super().__init__(features, name)
        if len(features) < 2:
            raise Exception(
                "Feature list in label summary must include at least two features.")
        self.type = 'LabelSummary'

    @property
    def avg_agreement(self):
        return Calculation(self.data, 'avg_agreement', self._ctx)

    @property
    def median_agreement(self):
        return Calculation(self.data, 'median_agreement', self._ctx)

    @property
    def fleiss_or_cohens_kappa(self):
        return Calculation(self.data, 'fleiss_or_cohens_kappa', self._ctx)
