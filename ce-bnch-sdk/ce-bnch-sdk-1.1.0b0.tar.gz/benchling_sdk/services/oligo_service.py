from typing import Any, Dict, Iterable, List, Optional, Union

from benchling_api_client.api.oligos import (
    archive_oligos,
    bulk_create_oligos,
    bulk_get_oligos,
    create_oligo,
    get_oligo,
    list_oligos,
    unarchive_oligos,
    update_oligo,
)
from benchling_api_client.models.entity_archive_reason import EntityArchiveReason
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.logging_helpers import check_for_csv_bug_fix, log_deprecation
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    none_as_unset,
    optional_array_query_param,
    schema_fields_query_param,
)
from benchling_sdk.models import (
    AsyncTaskLink,
    DnaOligo,
    ListOligosSort,
    Oligo,
    OligoCreate,
    OligosArchivalChange,
    OligosArchive,
    OligosBulkCreateRequest,
    OligosPaginatedList,
    OligosUnarchive,
    OligoUpdate,
    RnaOligo,
)
from benchling_sdk.services.base_service import BaseService


class OligoService(BaseService):
    """
    Oligos (Deprecated).

    Oligos are short linear DNA sequences that can be attached as primers to full DNA sequences. Just like other
    entities, they support schemas, tags, and aliases.

    Please migrate to the corresponding DNA/RNA Oligos endpoints.

    See https://benchling.com/api/reference#/Oligos
    See https://benchling.com/api/reference#/DNA%20Oligos
    See https://benchling.com/api/reference#/RNA%20Oligos
    """

    @api_method
    def get_by_id(self, oligo_id: str) -> DnaOligo:
        """
        Get an Oligo by ID (Deprecated).

        Please migrate to the corresponding DNA/RNA Oligos endpoints.

        See https://benchling.com/api/reference#/Oligos/getOligo
        See https://benchling.com/api/reference#/DNA%20Oligos/getDNAOligo
        See https://benchling.com/api/reference#/RNA%20Oligos/getRNAOligo
        """
        log_deprecation("oligos.get_by_id", "dna_oligos.get_by_id or rna_oligos.get_by_id")
        response = get_oligo.sync_detailed(client=self.client, oligo_id=oligo_id)
        return model_from_detailed(response)

    @api_method
    def _oligos_page(
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
        sort: Optional[ListOligosSort] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[OligosPaginatedList]:
        """Deprecate in favor of dna_oligos._dna_oligos_page or rna_oligos._rna_oligos_page."""
        log_deprecation("oligos._oligos_page", "dna_oligos._dna_oligos_page or rna_oligos._rna_oligos_page")
        return list_oligos.sync_detailed(  # type: ignore
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
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        sort: Optional[ListOligosSort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[Oligo]:
        """
        List Oligos (Deprecated).

        Please migrate to the corresponding DNA/RNA Oligos endpoints.

        See https://benchling.com/api/reference#/Oligos/listOligos
        See https://benchling.com/api/reference#/DNA%20Oligos/listDNAOligos
        See https://benchling.com/api/reference#/RNA%20Oligos/listRNAOligos
        """
        log_deprecation("oligos.list", "dna_oligos.list or rna_oligos.list")
        check_for_csv_bug_fix("mentioned_in", mentioned_in)
        check_for_csv_bug_fix("mentions", mentions)

        def api_call(next_token: NextToken) -> Response[OligosPaginatedList]:
            return self._oligos_page(
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
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                schema_fields=schema_fields,
                creator_ids=creator_ids,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: OligosPaginatedList) -> Optional[List[Oligo]]:
            return body.oligos

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, oligo: OligoCreate) -> DnaOligo:
        """
        Create an Oligo (Deprecated).

        Please migrate to the corresponding DNA/RNA Oligos endpoints.

        See https://benchling.com/api/reference#/Oligos/createOligo
        See https://benchling.com/api/reference#/DNA%20Oligos/createDNAOligo
        See https://benchling.com/api/reference#/RNA%20Oligos/createRNAOligo
        """
        log_deprecation("oligos.create", "dna_oligos.create or rna_oligos.create")
        response = create_oligo.sync_detailed(client=self.client, json_body=oligo)
        return model_from_detailed(response)

    @api_method
    def update(self, oligo_id: str, oligo: OligoUpdate) -> DnaOligo:
        """
        Update an Oligo (Deprecated).

        Please migrate to the corresponding DNA/RNA Oligos endpoints.

        See https://benchling.com/api/reference#/Oligos/updateOligo
        See https://benchling.com/api/reference#/DNA%20Oligos/updateDNAOligo
        See https://benchling.com/api/reference#/RNA%20Oligos/updateRNAOligo
        """
        log_deprecation("oligos.update", "dna_oligos.update or rna_oligos.update")
        response = update_oligo.sync_detailed(client=self.client, oligo_id=oligo_id, json_body=oligo)
        return model_from_detailed(response)

    @api_method
    def archive(self, oligo_ids: Iterable[str], reason: EntityArchiveReason) -> OligosArchivalChange:
        """
        Archive Oligos (Deprecated).

        Please migrate to the corresponding DNA/RNA Oligos endpoints.

        See https://benchling.com/api/reference#/Oligos/archiveOligos
        See https://benchling.com/api/reference#/DNA%20Oligos/archiveDNAOligos
        See https://benchling.com/api/reference#/RNA%20Oligos/archiveRNAOligos
        """
        log_deprecation("oligos.archive", "dna_oligos.archive or rna_oligos.archive")
        archive_request = OligosArchive(reason=reason, oligo_ids=list(oligo_ids))
        response = archive_oligos.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, oligo_ids: Iterable[str]) -> OligosArchivalChange:
        """
        Unarchive Oligos (Deprecated).

        Please migrate to the corresponding DNA/RNA Oligos endpoints.

        See https://benchling.com/api/reference#/Oligos/unarchiveOligos
        See https://benchling.com/api/reference#/DNA%20Oligos/unarchiveDNAOligos
        See https://benchling.com/api/reference#/RNA%20Oligos/unarchiveRNAOligos
        """
        log_deprecation("oligos.unarchive", "dna_oligos.unarchive or rna_oligos.unarchive")
        unarchive_request = OligosUnarchive(oligo_ids=list(oligo_ids))
        response = unarchive_oligos.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_get(self, oligo_ids: Iterable[str]) -> Optional[List[Union[DnaOligo, RnaOligo]]]:
        """
        Bulk get Oligos.

        See https://benchling.com/api/reference#/Oligos/bulkGetOligos
        """
        oligo_id_string = ",".join(oligo_ids)
        response = bulk_get_oligos.sync_detailed(client=self.client, oligo_ids=oligo_id_string)
        oligos_results = model_from_detailed(response)
        return oligos_results.oligos

    @api_method
    def bulk_create(self, oligos: Iterable[OligoCreate]) -> AsyncTaskLink:
        """
        Bulk create DNA Oligos (Deprecated).

        Please migrate to the corresponding DNA/RNA Oligos endpoints.

        See https://benchling.com/api/reference#/Oligos/bulkCreateOligos
        See https://benchling.com/api/reference#/DNA%20Oligos/bulkCreateDNAOligos
        See https://benchling.com/api/reference#/RNA%20Oligos/bulkCreateRNAOligos
        """
        log_deprecation("oligos.bulk_create", "dna_oligos.bulk_create or rna_oligos.bulk_create")
        body = OligosBulkCreateRequest(list(oligos))
        response = bulk_create_oligos.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
