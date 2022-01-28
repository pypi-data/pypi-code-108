from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.mixtures import (
    archive_mixtures,
    bulk_create_mixtures,
    bulk_update_mixtures,
    create_mixture,
    get_mixture,
    list_mixtures,
    unarchive_mixtures,
    update_mixture,
)
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
    AsyncTaskLink,
    EntityArchiveReason,
    ListMixturesSort,
    Mixture,
    MixtureBulkUpdate,
    MixtureCreate,
    MixturesArchivalChange,
    MixturesArchive,
    MixturesBulkCreateRequest,
    MixturesBulkUpdateRequest,
    MixturesPaginatedList,
    MixturesUnarchive,
    MixtureUpdate,
)
from benchling_sdk.services.base_service import BaseService


class MixtureService(BaseService):
    """
    Mixtures.

    Mixtures are solutions comprised of multiple ingredients where the exact quantities of each
    ingredient are important to track. Each ingredient is uniquely identified by its component entity.

    See https://benchling.com/api/reference#/Mixtures
    """

    @api_method
    def get_by_id(self, mixture_id: str) -> Mixture:
        """
        Get a mixture.

        See https://benchling.com/api/reference#/Mixtures/getMixture
        """
        response = get_mixture.sync_detailed(client=self.client, mixture_id=mixture_id)
        return model_from_detailed(response)

    @api_method
    def _mixtures_page(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[Iterable[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        schema_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[Iterable[str]] = None,
        sort: Optional[ListMixturesSort] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        ingredient_component_entity_ids: Optional[Iterable[str]] = None,
        ingredient_component_entity_ids_any_of: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[MixturesPaginatedList]:
        return list_mixtures.sync_detailed(  # type: ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            folder_id=none_as_unset(folder_id),
            mentioned_in=none_as_unset(optional_array_query_param(mentioned_in)),
            project_id=none_as_unset(project_id),
            registry_id=none_as_unset(registry_id),
            schema_id=none_as_unset(schema_id),
            archive_reason=none_as_unset(archive_reason),
            mentions=none_as_unset(optional_array_query_param(mentions)),
            sort=none_as_unset(sort),
            ids=none_as_unset(optional_array_query_param(ids)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            entity_registry_idsany_of=none_as_unset(optional_array_query_param(entity_registry_ids_any_of)),
            ingredient_component_entity_ids=none_as_unset(
                optional_array_query_param(ingredient_component_entity_ids)
            ),
            ingredient_component_entity_idsany_of=none_as_unset(
                optional_array_query_param(ingredient_component_entity_ids_any_of)
            ),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[Iterable[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        schema_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[Iterable[str]] = None,
        sort: Optional[ListMixturesSort] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        ingredient_component_entity_ids: Optional[Iterable[str]] = None,
        ingredient_component_entity_ids_any_of: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[Mixture]:
        """
        List Mixtures.

        See https://benchling.com/api/reference#/Mixtures/listMixtures
        """
        check_for_csv_bug_fix("mentioned_in", mentioned_in)
        check_for_csv_bug_fix("mentions", mentions)

        def api_call(next_token: NextToken) -> Response[MixturesPaginatedList]:
            return self._mixtures_page(
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                folder_id=folder_id,
                mentioned_in=mentioned_in,
                project_id=project_id,
                registry_id=registry_id,
                schema_id=schema_id,
                archive_reason=archive_reason,
                mentions=mentions,
                ids=ids,
                entity_registry_ids_any_of=entity_registry_ids_any_of,
                ingredient_component_entity_ids=ingredient_component_entity_ids,
                ingredient_component_entity_ids_any_of=ingredient_component_entity_ids_any_of,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                schema_fields=schema_fields,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: MixturesPaginatedList) -> Optional[List[Mixture]]:
            return body.mixtures

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, mixture: MixtureCreate) -> Mixture:
        """
        Create a mixture.

        See https://benchling.com/api/reference#/Mixtures/createMixture
        """
        response = create_mixture.sync_detailed(client=self.client, json_body=mixture)
        return model_from_detailed(response)

    @api_method
    def update(self, mixture_id: str, mixture: MixtureUpdate) -> Mixture:
        """
        Update a mixture.

        See https://benchling.com/api/reference#/Mixtures/updateMixture
        """
        response = update_mixture.sync_detailed(client=self.client, mixture_id=mixture_id, json_body=mixture)
        return model_from_detailed(response)

    @api_method
    def archive(self, mixture_ids: Iterable[str], reason: EntityArchiveReason) -> MixturesArchivalChange:
        """
        Archive mixtures.

        See https://benchling.com/api/reference#/Mixtures/archiveMixtures
        """
        archive_request = MixturesArchive(reason=reason, mixture_ids=list(mixture_ids))
        response = archive_mixtures.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, mixture_ids: Iterable[str]) -> MixturesArchivalChange:
        """
        Unarchive mixtures.

        See https://benchling.com/api/reference#/Mixtures/unarchiveMixtures
        """
        unarchive_request = MixturesUnarchive(mixture_ids=list(mixture_ids))
        response = unarchive_mixtures.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_create(self, mixtures: Iterable[MixtureCreate]) -> AsyncTaskLink:
        """
        Bulk create mixtures.

        See https://benchling.com/api/reference#/Mixtures/bulkCreateMixtures
        """
        body = MixturesBulkCreateRequest(list(mixtures))
        response = bulk_create_mixtures.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def bulk_update(self, mixtures: Iterable[MixtureBulkUpdate]) -> AsyncTaskLink:
        """
        Bulk update mixtures.

        See https://benchling.com/api/reference#/Mixtures/bulkUpdateMixtures
        """
        body = MixturesBulkUpdateRequest(list(mixtures))
        response = bulk_update_mixtures.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
