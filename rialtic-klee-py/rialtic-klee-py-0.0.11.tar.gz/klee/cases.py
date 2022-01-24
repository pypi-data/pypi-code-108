from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from klee.plans import EngineTestPlan

from os.path import join
from klee.files import save_json, fhir_to_json
from klee.insights import InsightText
from klee.claims import KleeTestClaim

from schema.insight_engine_request import InsightEngineRequest
from schema.insight_engine_response import InsightEngineResponse, \
    Insight, Defense, TranslatedMessage, MessageBundle

class InsightEngineTestCase:
    def __init__(self, test_plan: EngineTestPlan, claim: KleeTestClaim):
        self.insight: InsightText = test_plan.insights[claim.node_id]
        self.test_plan: EngineTestPlan = test_plan
        self.claim: KleeTestClaim = claim

    @property
    def defense(self) -> MessageBundle:
        return MessageBundle(messages=[
            TranslatedMessage(message=self.test_plan.get_defense(self))
        ])

    @property
    def request(self) -> InsightEngineRequest:
        return InsightEngineRequest(claim = self.claim.fhir_claim, transaction_id =
            self.claim.tx_id, history = self.test_plan.get_history(self.claim))

    @property
    def response(self) -> InsightEngineResponse:
        return InsightEngineResponse(insights=[
            Insight(
                type=self.insight.type,
                description=self.insight.text,
                defense=Defense(script=self.defense, referenceData=[]),
                claim_line_sequence_num=self.test_plan.claim_line(self.claim)
            )
        ])

    @property
    def json(self) -> Dict:
        return {
            "insight_engine_request": fhir_to_json(self.request),
            "insight_engine_response": fhir_to_json(self.response),
            'resourceType': "InsightEngineTestCase"
        }

    @property
    def history_list(self) -> List[Dict]:
        return [fhir_to_json(x) for x in self.request.history]

    def save_to_folder(self, directory):
        save_json(self.json, join(directory, self.claim.file_id + '.json'))

    def save_to_history(self, directory):
        save_json(self.history_list, join(directory, self.claim.file_id + '.json'))
