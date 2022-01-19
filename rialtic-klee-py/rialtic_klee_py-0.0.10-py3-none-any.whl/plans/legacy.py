from schema.insight_engine_request import HistoryClaim

from klee.cases import InsightEngineTestCase
from klee.plans import EngineTestPlan
from klee.claims import KleeTestClaim
from typing import List

class LegacyTestPlan(EngineTestPlan):
    def claim_line(self, claim: KleeTestClaim) -> int:
        return 1  # assumption here that CLUE #1 produces labelled insight

    def get_history(self, claim: KleeTestClaim) -> List[HistoryClaim]:
        return claim.schema_history

    def get_defense(self, case: InsightEngineTestCase) -> str:
        return case.insight.defense

    def validate_case(self, case: InsightEngineTestCase) -> bool:
        return True
