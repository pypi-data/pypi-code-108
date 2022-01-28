from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.rna_oligos import (
    archive_rna_oligos,
    bulk_create_rna_oligos,
    create_rna_oligo,
    get_rna_oligo,
    list_rna_oligos,
    unarchive_rna_oligos,
    update_rna_oligo,
)
from benchling_api_client.models.entity_archive_reason import EntityArchiveReason
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    none_as_unset,
    optional_array_query_param,
    schema_fields_query_param,
)
from benchling_sdk.models import (
    AsyncTaskLink,
    ListRNAOligosSort,
    RnaOligo,
    RnaOligoCreate,
    RnaOligosArchivalChange,
    RnaOligosArchive,
    RnaOligosBulkCreateRequest,
    RnaOligosPaginatedList,
    RnaOligosUnarchive,
    RnaOligoUpdate,
)
from benchling_sdk.services.base_service import BaseService


class RnaOligoService(BaseService):
    """
    RNA Oligos.

    RNA Oligos are short linear RNA sequences that can be attached as primers to full DNA sequences. Just like other
    entities, they support schemas, tags, and aliases.

    See https://benchling.com/api/reference#/RNA%20Oligos
    """

    @api_method
    def get_by_id(self, oligo_id: str) -> RnaOligo:
        """
        Get an RNA Oligo by ID.

        See https://benchling.com/api/reference#/RNA%20Oligos/getRNAOligo
        """
        response = get_rna_oligo.sync_detailed(client=self.client, oligo_id=oligo_id)
        return model_from_detailed(response)

    @api_method
    def _rna_oligos_page(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        bases: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        schema_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        sort: Optional[ListRNAOligosSort] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        name_includes: Optional[str] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[RnaOligosPaginatedList]:
        return list_rna_oligos.sync_detailed(  # type: ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            bases=none_as_unset(bases),
            folder_id=none_as_unset(folder_id),
            mentioned_in=none_as_unset(optional_array_query_param(mentioned_in)),
            project_id=none_as_unset(project_id),
            registry_id=none_as_unset(registry_id),
            schema_id=none_as_unset(schema_id),
            archive_reason=none_as_unset(archive_reason),
            mentions=none_as_unset(optional_array_query_param(mentions)),
            sort=none_as_unset(sort),
            ids=none_as_unset(optional_array_query_param(ids)),
            entity_registry_idsany_of=none_as_unset(optional_array_query_param(entity_registry_ids_any_of)),
            name_includes=none_as_unset(name_includes),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        bases: Optional[str] = None,
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
        sort: Optional[ListRNAOligosSort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[RnaOligo]:
        """
        List RNA Oligos.

        See https://benchling.com/api/reference#/RNA%20Oligos/listRNAOligos
        """

        def api_call(next_token: NextToken) -> Response[RnaOligosPaginatedList]:
            return self._rna_oligos_page(
                modified_at=modified_at,
                name=name,
                bases=bases,
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
                creator_ids=creator_ids,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: RnaOligosPaginatedList) -> Optional[List[RnaOligo]]:
            return body.rna_oligos

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, rna_oligo: RnaOligoCreate) -> RnaOligo:
        """
        Create an RNA Oligo.

        See https://benchling.com/api/reference#/RNA%20Oligos/createRNAOligo
        """
        response = create_rna_oligo.sync_detailed(client=self.client, json_body=rna_oligo)
        return model_from_detailed(response)

    @api_method
    def update(self, oligo_id: str, rna_oligo: RnaOligoUpdate) -> RnaOligo:
        """
        Update an RNA Oligo.

        See https://benchling.com/api/reference#/RNA%20Oligos/updateRNAOligo
        """
        response = update_rna_oligo.sync_detailed(client=self.client, oligo_id=oligo_id, json_body=rna_oligo)
        return model_from_detailed(response)

    @api_method
    def archive(self, rna_oligo_ids: Iterable[str], reason: EntityArchiveReason) -> RnaOligosArchivalChange:
        """
        Archive RNA Oligos.

        See https://benchling.com/api/reference#/RNA%20Oligos/archiveRNAOligos
        """
        archive_request = RnaOligosArchive(reason=reason, rna_oligo_ids=list(rna_oligo_ids))
        response = archive_rna_oligos.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, rna_oligo_ids: Iterable[str]) -> RnaOligosArchivalChange:
        """
        Unarchive RNA Oligos.

        See https://benchling.com/api/reference#/RNA%20Oligos/unarchiveRNAOligos
        """
        unarchive_request = RnaOligosUnarchive(rna_oligo_ids=list(rna_oligo_ids))
        response = unarchive_rna_oligos.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_create(self, rna_oligos: Iterable[RnaOligoCreate]) -> AsyncTaskLink:
        """
        Bulk create RNA Oligos.

        See https://benchling.com/api/reference#/RNA%20Oligos/bulkCreateRNAOligos
        """
        body = RnaOligosBulkCreateRequest(list(rna_oligos))
        response = bulk_create_rna_oligos.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
