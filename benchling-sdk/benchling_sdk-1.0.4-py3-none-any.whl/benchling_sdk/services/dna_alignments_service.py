from benchling_api_client.api.dna_alignments import (
    create_consensus_alignment,
    create_template_alignment,
    delete_dna_alignment,
    get_dna_alignment,
)
from benchling_api_client.models.async_task_link import AsyncTaskLink
from benchling_api_client.models.dna_alignment import DnaAlignment
from benchling_api_client.models.dna_consensus_alignment_create import DnaConsensusAlignmentCreate
from benchling_api_client.models.dna_template_alignment_create import DnaTemplateAlignmentCreate
from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.services.base_service import BaseService


class DnaAlignmentsService(BaseService):
    """
    DNA Alignments.

    A DNA alignment is a Benchling object representing an alignment of multiple DNA sequences.

    See https://benchling.com/api/reference#/DNA%20Alignments
    """

    @api_method
    def get_by_id(self, dna_alignment_id: str) -> DnaAlignment:
        """
        Get a DNA alignment.

        See https://benchling.com/api/reference#/DNA%20Alignments/getDNAAlignment
        """
        response = get_dna_alignment.sync_detailed(client=self.client, dna_alignment_id=dna_alignment_id)
        return model_from_detailed(response)

    @api_method
    def create_template_alignment(self, template_alignment: DnaTemplateAlignmentCreate) -> AsyncTaskLink:
        """
        Create a template DNA alignment.

        See https://benchling.com/api/reference#/DNA%20Alignments/createTemplateAlignment
        """
        response = create_template_alignment.sync_detailed(client=self.client, json_body=template_alignment)
        return model_from_detailed(response)

    @api_method
    def create_consensus_alignment(self, consensus_alignment: DnaConsensusAlignmentCreate) -> AsyncTaskLink:
        """
        Create a consensus DNA alignment.

        See https://benchling.com/api/reference#/DNA%20Alignments/createConsensusAlignment
        """
        response = create_consensus_alignment.sync_detailed(client=self.client, json_body=consensus_alignment)
        return model_from_detailed(response)

    @api_method
    def delete_alignment(self, dna_alignment_id: str) -> None:
        """
        Delete a DNA alignment.

        See https://benchling.com/api/reference#/DNA%20Alignments/deleteDNAAlignment
        """
        response = delete_dna_alignment.sync_detailed(client=self.client, dna_alignment_id=dna_alignment_id)
        raise_for_status(response)
