"""
Proposal Id parser
"""
from typing import Union

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.unique_bud import UniqueBud


class ProposalIdBud(UniqueBud):
    def __init__(self):
        super().__init__(constant_name=BudName.proposal_id.value, metadata_key="proposal_id")

    def setter(self, fits_obj: L0FitsAccess) -> Union[str, SpilledDirt]:
        if fits_obj.ip_task_type == "observe":
            return getattr(fits_obj, self.metadata_key)
        return SpilledDirt
