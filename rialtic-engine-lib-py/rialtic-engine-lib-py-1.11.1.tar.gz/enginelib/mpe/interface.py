from copy import copy
from typing import Optional

from schema.insight_engine_response import Insight

from enginelib.claim_focus import ClaimFocus
from enginelib.claim_line_focus import ClaimLineFocus
from enginelib.decor.policy import Policy
from enginelib.decor.registry import Registry
from enginelib.decor.traversal import TreeTraversal
from enginelib.mpe.subtrees.prerequisite import tree, PrerequisiteResult
from enginelib.utils import unique_identifier


class Prerequisite:
    """To control the data source (file, database table name, etc), you can
    set the following environment variables:

        MASTER_TABLE_ENV
        MASTER_TABLE_FILENAME
        MASTER_TABLE_NAME

    Please, refer to the docstring of functions in file `enginelib.rds.multipolicy`
    for more information.
    """

    def __init__(self, clue: ClaimLineFocus):
        self.clue = clue
        self.cue = ClaimFocus(claim=clue.request.claim)
        self.registry = Registry(cue=self.cue, clue=clue, ocs=list(), data=dict())
        self.label: Optional[str] = None
        self.rows = list()
        self.insight: Optional[Insight] = None

    def execute(self) -> bool:
        """ Executes the prerequisite subtree for the clue.

        Returns
            True if there were rows in the master table satisfying all the predicates
                in the prerequisite tree. The selected rows are returned in the form
                of a list of dictionaries, each containing a column_name: value
                for each column in the master table.

                In this case, the `rows` attribute holds the list of selected rows.

            False if no row in the master table satisfied all requirements. An insight
                is generated according to which end-node in the prerequisite tree was
                reached.

                IN this case, the `insight` attribute holds the corresponding insight.
        """
        pre_req_tree = copy(tree)
        pre_req_tree.assemble()
        self.label = TreeTraversal(pre_req_tree, self.registry).execute()

        if self.label == '300Y':
            self.rows = self.registry.data['reference_data_table']
            return True

        simple_insight = PrerequisiteResult.simple_insight(self.label)
        self.insight = Insight(
            id=unique_identifier(self.clue.request.claim.id),
            type=simple_insight.insight_type,
            description=simple_insight.text,
            claim_line_sequence_num=self.clue.sequence,
            defense=Policy.create_defense()
        )
        return False
