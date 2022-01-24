import sys

from klee.internal import Structure, log
from klee.insights import InsightDict, load_insights
from klee.claims import ClaimsDirectory, KleeTestClaim
from klee.cases import InsightEngineTestCase
from typing import Dict, Union, List

class TestCaseBuilder:
    def __init__(self, structure: Structure):
        self.claims_dir: ClaimsDirectory = ClaimsDirectory(structure.claim_dir)
        self.history_dir: str = structure.json_history
        self.output_dir: str = structure.json_cases

        self.insights: InsightDict = load_insights()
        self.claims_dir.load_claims()

        self.init_test_plan()

    def build_all_cases(self) -> Dict[str, InsightEngineTestCase]:
        all_cases = {}
        for node_label, kt_claim in self.get_primary_claims():
            all_cases[node_label] = self.build_test_case(kt_claim)
        return all_cases

    def build_test_case(self, node: Union[str, KleeTestClaim]) -> InsightEngineTestCase:
        """accepts node label or a node itself"""
        kt_claim = self.claims_dir.claims[node] if isinstance(node, str) else node

        if kt_claim.node_id in self.insights:
            # noinspection PyTypeChecker
            kt_case = InsightEngineTestCase(self, kt_claim)
            if not kt_case.test_plan.validate_case(kt_case):
                log.error(f"Unable to verify that {kt_claim.label_id} has been correctly built.")
            else:
                if self.output_dir:
                    kt_case.save_to_folder(self.output_dir)
                if self.history_dir:
                    kt_case.save_to_history(self.history_dir)
                return kt_case
        else:
            log.error(f"Unable to find insights for {kt_claim.label_id}")

    def build_node_labels(self, node_labels: List[str]) -> Dict[str, InsightEngineTestCase]:
        test_cases = {}

        if not node_labels:
            test_cases.update(self.build_all_cases())

        for label in node_labels:
            kt_case = self.build_test_case(label.split('.')[0])
            test_cases[kt_case.claim.label_id] = kt_case

        return test_cases

    def get_primary_claims(self):
        return self.claims_dir.claims.items()

    def init_test_plan(self):
        pass
