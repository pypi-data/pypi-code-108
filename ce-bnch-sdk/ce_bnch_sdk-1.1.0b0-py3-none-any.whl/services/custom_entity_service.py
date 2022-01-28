from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.custom_entities import (
    archive_custom_entities,
    bulk_create_custom_entities,
    bulk_get_custom_entities,
    bulk_update_custom_entities,
    create_custom_entity,
    get_custom_entity,
    list_custom_entities,
    unarchive_custom_entities,
    update_custom_entity,
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
    AsyncTaskLink,
    CustomEntitiesArchivalChange,
    CustomEntitiesArchive,
    CustomEntitiesBulkCreateRequest,
    CustomEntitiesBulkUpdateRequest,
    CustomEntitiesPaginatedList,
    CustomEntitiesUnarchive,
    CustomEntity,
    CustomEntityBulkCreate,
    CustomEntityBulkUpdate,
    CustomEntityCreate,
    CustomEntityUpdate,
    ListCustomEntitiesSort,
)
from benchling_sdk.services.base_service import BaseService


class CustomEntityService(BaseService):
    """
    Custom Entities.

    Benchling supports custom entities for biological entities that are neither sequences or proteins. Custom
    entities must have an entity schema set and can have both schema fields and custom fields.

    See https://benchling.com/api/reference#/Custom%20Entities
    """

    @api_method
    def get_by_id(self, entity_id: str) -> CustomEntity:
        """
        Get a custom entity.

        See https://benchling.com/api/reference#/Custom%20Entities/getCustomEntity
        """
        response = get_custom_entity.sync_detailed(client=self.client, custom_entity_id=entity_id)
        return model_from_detailed(response)

    @api_method
    def _custom_entities_page(
        self,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        sort: Optional[ListCustomEntitiesSort] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[CustomEntitiesPaginatedList]:
        return list_custom_entities.sync_detailed(  # type: ignore
            client=self.client,
            schema_id=none_as_unset(schema_id),
            modified_at=none_as_unset(modified_at),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            folder_id=none_as_unset(folder_id),
            mentioned_in=none_as_unset(optional_array_query_param(mentioned_in)),
            project_id=none_as_unset(project_id),
            registry_id=none_as_unset(registry_id),
            archive_reason=none_as_unset(archive_reason),
            mentions=none_as_unset(optional_array_query_param(mentions)),
            sort=none_as_unset(sort),
            ids=none_as_unset(optional_array_query_param(ids)),
            entity_registry_idsany_of=none_as_unset(optional_array_query_param(entity_registry_ids_any_of)),
            namesany_of=none_as_unset(optional_array_query_param(names_any_of)),
            namesany_ofcase_sensitive=none_as_unset(optional_array_query_param(names_any_of_case_sensitive)),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        ids: Optional[Iterable[str]] = None,
        entity_registry_ids_any_of: Optional[Iterable[str]] = None,
        names_any_of: Optional[Iterable[str]] = None,
        names_any_of_case_sensitive: Optional[Iterable[str]] = None,
        creator_ids: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        sort: Optional[ListCustomEntitiesSort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[CustomEntity]:
        """
        List custom entities.

        See https://benchling.com/api/reference#/Custom%20Entities/listCustomEntities
        """
        check_for_csv_bug_fix("mentioned_in", mentioned_in)
        check_for_csv_bug_fix("mentions", mentions)

        def api_call(next_token: NextToken) -> Response[CustomEntitiesPaginatedList]:
            return self._custom_entities_page(
                schema_id=schema_id,
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                folder_id=folder_id,
                mentioned_in=mentioned_in,
                project_id=project_id,
                registry_id=registry_id,
                archive_reason=archive_reason,
                mentions=mentions,
                ids=ids,
                entity_registry_ids_any_of=entity_registry_ids_any_of,
                names_any_of=names_any_of,
                names_any_of_case_sensitive=names_any_of_case_sensitive,
                creator_ids=creator_ids,
                schema_fields=schema_fields,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: CustomEntitiesPaginatedList) -> Optional[List[CustomEntity]]:
            return body.custom_entities

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, entity: CustomEntityCreate) -> CustomEntity:
        """
        Create a custom entity.

        See https://benchling.com/api/reference#/Custom%20Entities/createCustomEntity
        """
        response = create_custom_entity.sync_detailed(client=self.client, json_body=entity)
        return model_from_detailed(response)

    @api_method
    def update(self, entity_id: str, entity: CustomEntityUpdate) -> CustomEntity:
        """
        Update a custom entity.

        See https://benchling.com/api/reference#/Custom%20Entities/updateCustomEntity
        """
        response = update_custom_entity.sync_detailed(
            client=self.client, custom_entity_id=entity_id, json_body=entity
        )
        return model_from_detailed(response)

    @api_method
    def archive(self, entity_ids: Iterable[str], reason: EntityArchiveReason) -> CustomEntitiesArchivalChange:
        """
        Archive custom entities.

        See https://benchling.com/api/reference#/Custom%20Entities/archiveCustomEntities
        """
        archive_request = CustomEntitiesArchive(reason=reason, custom_entity_ids=list(entity_ids))
        response = archive_custom_entities.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, entity_ids: Iterable[str]) -> CustomEntitiesArchivalChange:
        """
        Unarchive custom entities.

        See https://benchling.com/api/reference#/Custom%20Entities/unarchiveCustomEntities
        """
        unarchive_request = CustomEntitiesUnarchive(custom_entity_ids=list(entity_ids))
        response = unarchive_custom_entities.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_get(self, entity_ids: Iterable[str]) -> Optional[List[CustomEntity]]:
        """
        Bulk get custom entities.

        See https://benchling.com/api/reference#/Custom%20Entities/bulkGetCustomEntities
        """
        entity_id_string = ",".join(entity_ids)
        response = bulk_get_custom_entities.sync_detailed(
            client=self.client, custom_entity_ids=entity_id_string
        )
        custom_entities = model_from_detailed(response)
        return custom_entities.custom_entities

    @api_method
    def bulk_create(self, entities: Iterable[CustomEntityBulkCreate]) -> AsyncTaskLink:
        """
        Bulk create custom entities.

        See https://benchling.com/api/reference#/Custom%20Entities/bulkCreateCustomEntities
        """
        body = CustomEntitiesBulkCreateRequest(list(entities))
        response = bulk_create_custom_entities.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def bulk_update(self, entities: Iterable[CustomEntityBulkUpdate]) -> AsyncTaskLink:
        """
        Bulk update custom entities.

        See https://benchling.com/api/reference#/Custom%20Entities/bulkUpdateCustomEntities
        """
        body = CustomEntitiesBulkUpdateRequest(list(entities))
        response = bulk_update_custom_entities.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
