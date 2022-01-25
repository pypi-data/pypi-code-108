import os
from copy import copy
import datetime as dt
from trace import Trace
from typing import List, Optional, Dict, Any, Union

from dataUtils.DBClient import DBClient
from enginelib.claim_focus import ClaimFocus
from enginelib.claim_line_focus import ClaimLineFocus
from fhir.resources.claim import Claim
from schema.insight_engine_request import InsightEngineRequest
from schema.insight_engine_response import InsightEngineResponse, Insight, Defense, TranslatedMessage, MessageBundle, \
    InsightType

from enginelib.decor.flow import Flow
from enginelib.decor.traversal import TreeTraversal
from enginelib.decor.registry import Registry
from enginelib.decor.tree import Tree
from enginelib.errors import MissingFieldError, ClaimError
from enginelib.utils import unique_identifier


class Policy:
    def __init__(self, request: InsightEngineRequest, historical_claims: List[Claim],
                 decision_tree: Union[Tree, Flow], data: Optional[Dict[str, Any]] = None, engine_id: str = ''):
        self.cue = ClaimFocus(claim=request.claim, request=request)
        self.request = request
        self.historical_claims = [
            ClaimFocus(claim=claim, request=InsightEngineRequest.construct(claim=claim))
            for claim in historical_claims
        ]
        self.flow = Flow(decision_tree) if isinstance(decision_tree, Tree) else decision_tree
        self.data: Dict[str, Any] = data or dict()
        self.client = DBClient.GetDBClient(os.environ['APIKEY'])
        self.engine_id = engine_id
        if engine_id:
            self.client.init_defenses(request.transaction_id or 'testing', engine_id=engine_id)

    def check_effective_date(self, clue: ClaimLineFocus) -> Optional[Insight]:
        if 'effective_start_date' not in self.data:
            return None

        start_date = self.data['effective_start_date']
        end_date = self.data.get('effective_end_date', dt.date(9999, 1, 1))

        assert isinstance(start_date, dt.date), \
            'Custom data `effective_start_date`, if present, must be an instance of class `datetime.date`.'
        assert isinstance(end_date, dt.date), \
            'Custom data `effective_end_date`, if present, must be an instance of class `datetime.date`.'
        assert start_date < end_date, \
            'Custom data `effective_start_date`, if present, must come before `effective_end_date`.'

        try:
            from_date: dt.date = clue.service_period.start
        except MissingFieldError as err:
            return Insight(
                id=unique_identifier(self.request.claim.id),
                type=InsightType.Error,
                description=str(err),
                claim_line_sequence_num=clue.sequence,
                defense=Policy.create_defense()
            )

        if from_date < start_date or from_date >= end_date:
            if from_date < start_date:
                relation = 'before this policy became effective'
                critical_date = start_date
            else:
                relation = 'on or after the effective period of this policy ended'
                critical_date = end_date

            message = f'The service date on this claim line ({from_date.strftime("%Y-%m-%d")}) ' \
                      f'comes {relation} ({critical_date.strftime("%Y-%m-%d")}).'

            return Insight(
                id=unique_identifier(self.request.claim.id),
                type=InsightType.NotApplicable,
                description=message,
                claim_line_sequence_num=clue.sequence,
                defense=Policy.create_defense()
            )

    def evaluate(self) -> InsightEngineResponse:
        """Evaluates the policy for each claim line in self.request.claim.

        Returns:
            a response with the response.insights containing the list of insights
        """
        response = InsightEngineResponse()
        response.engine_name = self.engine_id
        response.insights = list()
        for clue in self.cue.lines:
            ins = self.check_effective_date(clue)
            if ins:
                response.insights.append(ins)
                continue
            response.insights.extend(self._assess(clue))

        return response

    def _assess(self, clue: ClaimLineFocus) -> List[Insight]:
        """Assess one claim line according to the decision tree of the policy.

        Args:
            clue: claim line to assess.

        Returns:
            a list of insights for the given claim line (one for each tree in the flow).
        """
        insights: List[Insight] = list()
        registry = Registry(cue=self.cue, clue=clue, ocs=self.historical_claims, data=copy(self.data))

        flow = self.flow
        trace_list: List[Trace] = list()
        while flow:
            label, insight = self._assess_tree(clue, flow.tree, registry)
            conn = flow.connections.get(label, None)
            trace_list.extend(insight.trace)
            if not conn or not conn.ignore_insight:
                insight.trace = copy(trace_list)
                insights.append(insight)
            flow = conn.flow if conn else None

        return insights

    def _assess_tree(self, clue: ClaimLineFocus, tree: Tree, registry: Registry) -> (str, Insight):
        debug = os.getenv('DECOR_DEBUG', '')

        traversal = TreeTraversal(tree, registry)
        try:
            label = traversal.execute()
            # We should add all errors that we want to catch in the following tuple:
        except (MissingFieldError, ClaimError) as err:
            return '', Insight(
                id=unique_identifier(self.request.claim.id),
                type=InsightType.Error,
                description=str(err),
                trace=[traversal.trace],
                claim_line_sequence_num=clue.sequence,
                defense=self.create_defense()
            )

        # Customize insight text with parameters in the registry
        result_class = tree.ResultClass
        insight_type = result_class.insight_type[label]
        insight_text = result_class.insight_text[label]
        insight_text = self._format_insight_text(registry, insight_text, debug=debug)

        # Fetch defense data and create defense object
        if self.engine_id and 'subcode' in registry and registry['subcode']:
            self.client.init_defenses(self.request.transaction_id or 'testing', engine_id=self.engine_id, subcode=registry['subcode'])
        excerpt, uuid = self.client.get_defense_by_node(label)
        defense = self.create_defense(text=excerpt, uuid=uuid)

        return label, Insight(
            id=unique_identifier(self.request.claim.id),
            type=insight_type,
            description=insight_text,
            trace=[traversal.trace],
            claim_line_sequence_num=clue.sequence,
            defense=defense
        )

    def _format_insight_text(self, registry: Registry, text: str, debug: str = '') -> str:
        # DEBUGGING
        if debug == 'parameters':
            self._log(end=f'The function _format_insight_text() was called with text {repr(text)}. ')
            self._log(f'The registry has the following parameters defined: {registry.computed_parameters_values}')

        return registry.format_text(text)

    @staticmethod
    def create_defense(text: str = '', uuid: str = '') -> Defense:
        message = TranslatedMessage()
        message.lang = 'en'
        message.message = text

        script = MessageBundle()
        script.uuid = uuid
        script.messages = [message]

        defense = Defense()
        defense.script = script
        return defense

    @staticmethod
    def _log(*args, **kwargs):
        print(*args, **kwargs)
