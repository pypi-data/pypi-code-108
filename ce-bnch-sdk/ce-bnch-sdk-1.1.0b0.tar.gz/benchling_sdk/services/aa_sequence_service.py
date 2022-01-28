from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.aa_sequences import (
    archive_aa_sequences,
    auto_annotate_aa_sequences,
    bulk_create_aa_sequences,
    bulk_get_aa_sequences,
    create_aa_sequence,
    get_aa_sequence,
    list_aa_sequences,
    unarchive_aa_sequences,
    update_aa_sequence,
)
from benchling_api_client.models.entity_archive_reason import EntityArchiveReason
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.logging_helpers import check_for_csv_bug_fix
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    none_as_unset,
    optional_array_query_param,
    schema_fields_query_param,
)
from benchling_sdk.models import (
    AaSequence,
    AaSequenceBulkCreate,
    AaSequenceCreate,
    AaSequencesArchivalChange,
    AaSequencesArchive,
    AaSequencesBulkCreateRequest,
    AaSequencesPaginatedList,
    AaSequencesUnarchive,
    AaSequenceUpdate,
    AsyncTaskLink,
    AutoAnnotateAaSequences,
    ListAASequencesSort,
)
from benchling_sdk.services.base_service import BaseService


class AaSequenceService(BaseService):
    """
    AA Sequences.

    AA Sequences are the working units of cells that make everything run (they help make structures, catalyze
    reactions and allow for signaling - a kind of internal cell communication). On Benchling, these are comprised
    of a string of amino acids and collections of other attributes, such as annotations.

    See https://benchling.com/api/reference#/AA%20Sequences
    """

    @api_method
    def get_by_id(self, aa_sequence_id: str) -> AaSequence:
        """
        Get an AA Sequence.

        See https://benchling.com/api/reference#/AA%20Sequences/getAASequence
        """
        response = get_aa_sequence.sync_detailed(client=self.client, aa_sequence_id=aa_sequence_id)
        return model_from_detailed(response)

    @api_method
    def _aa_sequences_page(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        amino_acids: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        schema_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        name_includes: Optional[str] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        sort: Optional[ListAASequencesSort] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[AaSequencesPaginatedList]:
        return list_aa_sequences.sync_detailed(  # type: ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            amino_acids=none_as_unset(amino_acids),
            folder_id=none_as_unset(folder_id),
            mentioned_in=none_as_unset(optional_array_query_param(mentioned_in)),
            project_id=none_as_unset(project_id),
            registry_id=none_as_unset(registry_id),
            schema_id=none_as_unset(schema_id),
            archive_reason=none_as_unset(archive_reason),
            mentions=none_as_unset(optional_array_query_param(mentions)),
            ids=none_as_unset(optional_array_query_param(ids)),
            entity_registry_idsany_of=none_as_unset(optional_array_query_param(entity_registry_ids_any_of)),
            name_includes=none_as_unset(name_includes),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            sort=none_as_unset(sort),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        amino_acids: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        schema_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        name_includes: Optional[str] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        sort: Optional[ListAASequencesSort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[AaSequence]:
        """
        List AA Sequences.

        See https://benchling.com/api/reference#/AA%20Sequences/listAASequences
        """
        check_for_csv_bug_fix("mentioned_in", mentioned_in)
        check_for_csv_bug_fix("mentions", mentions)

        def api_call(next_token: NextToken) -> Response[AaSequencesPaginatedList]:
            return self._aa_sequences_page(
                modified_at=modified_at,
                name=name,
                amino_acids=amino_acids,
                folder_id=folder_id,
                mentioned_in=mentioned_in,
                project_id=project_id,
                registry_id=registry_id,
                schema_id=schema_id,
                archive_reason=archive_reason,
                mentions=mentions,
                ids=ids,
                entity_registry_ids_any_of=entity_registry_ids_any_of,
                name_includes=name_includes,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                schema_fields=schema_fields,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: AaSequencesPaginatedList) -> Optional[List[AaSequence]]:
            return body.aa_sequences

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, aa_sequence: AaSequenceCreate) -> AaSequence:
        """
        Create an AA Sequence.

        See https://benchling.com/api/reference#/AA%20Sequences/createAASequence
        """
        response = create_aa_sequence.sync_detailed(client=self.client, json_body=aa_sequence)
        return model_from_detailed(response)

    @api_method
    def update(self, aa_sequence_id: str, aa_sequence: AaSequenceUpdate) -> AaSequence:
        """
        Update an AA Sequence.

        See https://benchling.com/api/reference#/AA%20Sequences/updateAASequence
        """
        response = update_aa_sequence.sync_detailed(
            client=self.client, aa_sequence_id=aa_sequence_id, json_body=aa_sequence
        )
        return model_from_detailed(response)

    @api_method
    def archive(
        self, aa_sequence_ids: Iterable[str], reason: EntityArchiveReason
    ) -> AaSequencesArchivalChange:
        """
        Archive an AA Sequence.

        See https://benchling.com/api/reference#/AA%20Sequences/archiveAASequences
        """
        archive_request = AaSequencesArchive(reason=reason, aa_sequence_ids=list(aa_sequence_ids))
        response = archive_aa_sequences.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, aa_sequence_ids: Iterable[str]) -> AaSequencesArchivalChange:
        """
        Unarchive an AA Sequence.

        See https://benchling.com/api/reference#/AA%20Sequences/unarchiveAASequences
        """
        unarchive_request = AaSequencesUnarchive(aa_sequence_ids=list(aa_sequence_ids))
        response = unarchive_aa_sequences.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_get(self, aa_sequence_ids: Iterable[str]) -> Optional[List[AaSequence]]:
        """
        Bulk get AA sequences by ID.

        See https://benchling.com/api/reference#/AA%20Sequences/bulkGetAASequences
        """
        aa_sequence_id_string = ",".join(aa_sequence_ids)
        response = bulk_get_aa_sequences.sync_detailed(
            client=self.client, aa_sequence_ids=aa_sequence_id_string
        )
        aa_sequences_results = model_from_detailed(response)
        return aa_sequences_results.aa_sequences

    @api_method
    def bulk_create(self, aa_sequences: Iterable[AaSequenceBulkCreate]) -> AsyncTaskLink:
        """
        Bulk Create AA sequences.

        See https://benchling.com/api/reference#/AA%20Sequences/bulkCreateAASequences
        """
        body = AaSequencesBulkCreateRequest(list(aa_sequences))
        response = bulk_create_aa_sequences.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def auto_annotate(self, auto_annotate: AutoAnnotateAaSequences) -> AsyncTaskLink:
        """
        Auto-annotate AA sequences with matching features from specified Feature Libraries.

        See https://benchling.com/api/reference#/AA%20Sequences/autoAnnotateAaSequences
        """
        response = auto_annotate_aa_sequences.sync_detailed(client=self.client, json_body=auto_annotate)
        return model_from_detailed(response)
