from typing import List, Optional

from benchling_api_client.api.dna_alignments import (
    create_consensus_alignment,
    create_template_alignment,
    delete_dna_alignment,
    get_dna_alignment,
    list_dna_alignments,
)
from benchling_api_client.types import Response

from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    AsyncTaskLink,
    DnaAlignment,
    DnaAlignmentsPaginatedList,
    DnaAlignmentSummary,
    DnaConsensusAlignmentCreate,
    DnaTemplateAlignmentCreate,
    ListDNAAlignmentsSort,
)
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
    def _dna_alignments_page(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ids: Optional[List[str]] = None,
        names_any_of: Optional[List[str]] = None,
        names_any_of_case_sensitive: Optional[List[str]] = None,
        sequence_ids: Optional[List[str]] = None,
        sort: Optional[ListDNAAlignmentsSort] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[DnaAlignmentsPaginatedList]:
        return list_dna_alignments.sync_detailed(  # type: ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            ids=none_as_unset(optional_array_query_param(ids)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            sequence_ids=none_as_unset(optional_array_query_param(sequence_ids)),
            sort=none_as_unset(sort),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        ids: Optional[List[str]] = None,
        names_any_of: Optional[List[str]] = None,
        names_any_of_case_sensitive: Optional[List[str]] = None,
        sequence_ids: Optional[List[str]] = None,
        sort: Optional[ListDNAAlignmentsSort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[DnaAlignmentSummary]:
        """
        List DNA Alignments.

        See https://benchling.com/api/reference#/DNA%20Alignments/listDNAAlignments
        """

        def api_call(next_token: NextToken) -> Response[DnaAlignmentsPaginatedList]:
            return self._dna_alignments_page(
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                ids=ids,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                sequence_ids=sequence_ids,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: DnaAlignmentsPaginatedList) -> Optional[List[DnaAlignmentSummary]]:
            return body.dna_alignments

        return PageIterator(api_call, results_extractor)

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
