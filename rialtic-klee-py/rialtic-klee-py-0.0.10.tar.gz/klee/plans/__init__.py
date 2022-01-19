from schema.insight_engine_request import HistoryClaim
from klee.build import TestCaseBuilder
from klee.cases import InsightEngineTestCase
from klee.claims import KleeTestClaim
from abc import abstractmethod
from typing import List

class EngineTestPlan(TestCaseBuilder):
    @abstractmethod
    def claim_line(self, claim: KleeTestClaim) -> int:
        pass

    @abstractmethod
    def get_history(self, claim: KleeTestClaim) -> List[HistoryClaim]:
        pass

    @abstractmethod
    def get_defense(self, case: InsightEngineTestCase) -> str:
        pass

    @abstractmethod
    def validate_case(self, case: InsightEngineTestCase) -> bool:
        pass

from klee.plans.legacy import LegacyTestPlan
from klee.plans.mpe_test import MPETestPlan

Options = {
    'default': MPETestPlan,
    'legacy_spe': LegacyTestPlan,
    'mpe_test': MPETestPlan,
}