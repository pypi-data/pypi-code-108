from typing import List, Dict

from schema.insight_engine_request import InsightEngineRequest
from schema.insight_engine_response import InsightEngineResponse, Insight

from enginelib.claim_focus import ClaimFocus
from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.decor.policy import Policy
from enginelib.decor.flow import Flow
from enginelib.mpe.interface import Prerequisite


class MultiPolicy:
    def __init__(self, flow: Flow, engine_id: str):
        self.flow = flow
        self.engine_id = engine_id

    def evaluate(self, request: InsightEngineRequest) -> InsightEngineResponse:
        response = InsightEngineResponse()
        response.engine_name = self.engine_id
        response.insights = list()

        cue = ClaimFocus(claim=request.claim, request=request)
        for clue in cue.lines:
            response.insights.extend(self._assess(clue))
        return response

    def _assess(self, clue: ClaimLineFocus) -> List[Insight]:
        prerequisite = Prerequisite(clue)
        if not prerequisite.execute():
            return [prerequisite.insight]

        insights: List[Insight] = list()
        policies: Dict[str, List[dict]] = dict()
        for row in prerequisite.rows:
            policy_name = row['policy_name']
            policies.setdefault(policy_name, list()).append(row)

        for policy_name, rows in policies.items():
            if len(rows) != 1:
                self._log(f'Error: not able to narrow master table down to one row '
                          f'for policy {policy_name} when procedureCode is {clue.procedure_code}.')
                continue

            row = rows[0]

            response = Policy(
                request=clue.request,
                decision_tree=self.flow,
                historical_claims=list(),
                data=row,
                engine_id=self.engine_id
            ).evaluate()

            for insight in response.insights:
                insight.policy_name = policy_name
                if 'policy_excerpt' in row and row['policy_excerpt']:
                    # Overwrites any previous defense for this insight with the policy_excerpt:
                    insight.defense = Policy.create_defense(text=row['policy_excerpt'])
                insights.append(insight)

        return insights

    @staticmethod
    def _log(*args, **kwargs):
        print(*args, **kwargs)
