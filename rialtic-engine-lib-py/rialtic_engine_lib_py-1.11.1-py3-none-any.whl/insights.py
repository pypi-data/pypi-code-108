from typing import TypeVar

from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.tree_node import ResultTreeNode
from fhir.resources.claim import ClaimItem

from enginelib.simple_insight import SimpleInsight
from schema.insight_engine_response import InsightType

A = TypeVar('A')

ClaimLine = ClaimItem

ClaimLineInsight = ResultTreeNode[ClaimLineFocus, SimpleInsight]


def stub(id: str) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.Error, "TODO: " + id)
    )


def insight_line_valid(s: str) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.ClaimLineValid, s)
    )


def insight_claim_not_payable(s: str, **kwargs) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.ClaimNotPayable, s, defense=kwargs.get('defense', None),
                                       defenseuuid=kwargs.get('defenseuuid', None))
    )


def insight_not_applicable(s: str) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.NotApplicable, s)
    )


def insight_line_not_payable(s: str, **kwargs) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.ClaimLineNotPayable, s, defense=kwargs.get('defense', None),
                                       defenseuuid=kwargs.get('defenseuuid', None))
    )


def insight_recode_line(s: str, **kwargs) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.RecodeClaimLine, s, defense=kwargs.get('defense', None),
                                       defenseuuid=kwargs.get('defenseuuid', None))
    )


def insight_line_require_manual_review(s: str, **kwargs) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.ManualReview, s, defense=kwargs.get('defense', None),
                                       defenseuuid=kwargs.get('defenseuuid', None))
    )


def insight_line_error(s: str) -> ResultTreeNode[A, SimpleInsight]:
    return ResultTreeNode[A, SimpleInsight](
        lambda *request: SimpleInsight(InsightType.Error, s)
    )