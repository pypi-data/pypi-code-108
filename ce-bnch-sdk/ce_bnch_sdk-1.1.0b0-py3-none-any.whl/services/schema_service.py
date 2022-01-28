from typing import List, Optional

from benchling_api_client.api.schemas import (
    get_batch_schema,
    get_box_schema,
    get_container_schema,
    get_entity_schema,
    get_entry_schema,
    get_location_schema,
    get_plate_schema,
    get_request_schema,
    get_request_task_schema,
    get_result_schema,
    get_run_schema,
    get_workflow_task_schema,
    list_assay_result_schemas,
    list_assay_run_schemas,
    list_batch_schemas,
    list_box_schemas,
    list_container_schemas,
    list_entity_schemas,
    list_entry_schemas,
    list_location_schemas,
    list_plate_schemas,
    list_request_schemas,
    list_request_task_schemas,
    list_workflow_task_schemas,
)
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.models import (
    AssayResultSchema,
    AssayResultSchemasPaginatedList,
    AssayRunSchema,
    AssayRunSchemasPaginatedList,
    BatchSchema,
    BatchSchemasPaginatedList,
    BoxSchema,
    BoxSchemasPaginatedList,
    ContainerSchema,
    ContainerSchemasPaginatedList,
    EntitySchema,
    EntitySchemasPaginatedList,
    EntrySchemaDetailed,
    EntrySchemasPaginatedList,
    LocationSchema,
    LocationSchemasPaginatedList,
    PlateSchema,
    PlateSchemasPaginatedList,
    RequestSchema,
    RequestSchemasPaginatedList,
    RequestTaskSchema,
    RequestTaskSchemasPaginatedList,
    WorkflowTaskSchema,
    WorkflowTaskSchemasPaginatedList,
)
from benchling_sdk.services.base_service import BaseService


class SchemaService(BaseService):
    """
    Schemas.

    Schemas represent custom configuration of objects in Benchling. See https://docs.benchling.com/docs/schemas in
    our documentation on how Schemas impact our developers.

    See API docs at https://benchling.com/api/reference#/Schemas
    """

    @api_method
    def get_assay_result_schema_by_id(self, schema_id: str) -> AssayResultSchema:
        """
        Get a Result schema by ID.

        See https://benchling.com/api/reference#/Schemas/getResultSchema
        """
        response = get_result_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _assay_result_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[AssayResultSchemasPaginatedList]:
        """
        Get a Result schema by ID.

        See https://benchling.com/api/reference#/Schemas/getResultSchema
        """
        return list_assay_result_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_assay_result_schemas(
        self,
        *,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[AssayResultSchema]:
        """
        List assay result schemas.

        See https://benchling.com/api/reference#/Schemas/listAssayResultSchemas
        """

        def api_call(next_token: NextToken) -> Response[AssayResultSchemasPaginatedList]:
            return self._assay_result_schemas_page(
                modified_at=modified_at,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: AssayResultSchemasPaginatedList) -> Optional[List[AssayResultSchema]]:
            return body.assay_result_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_assay_run_schema_by_id(self, schema_id: str) -> AssayRunSchema:
        """
        Get a Run schema by ID.

        See https://benchling.com/api/reference#/Schemas/getRunSchema
        """
        response = get_run_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _assay_run_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[AssayRunSchemasPaginatedList]:
        return list_assay_run_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_assay_run_schemas(
        self,
        *,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[AssayRunSchema]:
        """
        List assay run schemas.

        See https://benchling.com/api/reference#/Schemas/listAssayRunSchemas
        """

        def api_call(next_token: NextToken) -> Response[AssayRunSchemasPaginatedList]:
            return self._assay_run_schemas_page(
                modified_at=modified_at,
                next_token=next_token,
                page_size=page_size,
            )

        def runs_extractor(body: AssayRunSchemasPaginatedList) -> Optional[List[AssayRunSchema]]:
            return body.assay_run_schemas

        return PageIterator(api_call, runs_extractor)

    @api_method
    def get_batch_schemas_by_id(self, schema_id: str) -> BatchSchema:
        """
        Get a batch schema by ID.

        See https://benchling.com/api/reference#/Schemas/getBatchSchema
        """
        response = get_batch_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _batch_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[BatchSchemasPaginatedList]:
        return list_batch_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_batch_schemas(
        self,
        *,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[BatchSchema]:
        """
        List batch schemas.

        See https://benchling.com/api/reference#/Schemas/listBatchSchemas
        """

        def api_call(next_token: NextToken) -> Response[BatchSchemasPaginatedList]:
            return self._batch_schemas_page(
                modified_at=modified_at,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: BatchSchemasPaginatedList) -> Optional[List[BatchSchema]]:
            return body.batch_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_box_schema_by_id(self, schema_id: str) -> BoxSchema:
        """
        Get a box schema by ID.

        See https://benchling.com/api/reference#/Schemas/getBoxSchema
        """
        response = get_box_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _box_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[BoxSchemasPaginatedList]:
        return list_box_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_box_schemas(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[BoxSchema]:
        """
        List box schemas.

        See https://benchling.com/api/reference#/Schemas/listBoxSchemas
        """

        def api_call(next_token: NextToken) -> Response[BoxSchemasPaginatedList]:
            return self._box_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: BoxSchemasPaginatedList) -> Optional[List[BoxSchema]]:
            return body.box_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_container_schema_by_id(self, schema_id: str) -> ContainerSchema:
        """
        Get a container schema by ID.

        See https://benchling.com/api/reference#/Schemas/getContainerSchema
        """
        response = get_container_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _container_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[ContainerSchemasPaginatedList]:
        return list_container_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_container_schemas(
        self,
        *,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[ContainerSchema]:
        """
        List container schemas.

        See https://benchling.com/api/reference#/Schemas/listContainerSchemas
        """

        def api_call(next_token: NextToken) -> Response[ContainerSchemasPaginatedList]:
            return self._container_schemas_page(
                modified_at=modified_at,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: ContainerSchemasPaginatedList) -> List[ContainerSchema]:
            return body.container_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_entity_schema_by_id(self, schema_id: str) -> EntitySchema:
        """
        Get an entity schema by ID.

        See https://benchling.com/api/reference#/Schemas/getEntitySchema
        """
        response = get_entity_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _entity_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[EntitySchemasPaginatedList]:
        return list_entity_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_entity_schemas(
        self,
        *,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[EntitySchema]:
        """
        List entity schemas.

        See https://benchling.com/api/reference#/Schemas/listEntitySchemas
        """

        def api_call(next_token: NextToken) -> Response[EntitySchemasPaginatedList]:
            return self._entity_schemas_page(
                modified_at=modified_at,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: EntitySchemasPaginatedList) -> Optional[List[EntitySchema]]:
            return body.entity_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_entry_schema_by_id(self, schema_id: str) -> EntrySchemaDetailed:
        """
        Get an Entry schema by ID.

        See https://benchling.com/api/reference#/Schemas/getEntrySchema
        """
        response = get_entry_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _entry_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[EntrySchemasPaginatedList]:
        return list_entry_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_entry_schemas(
        self,
        *,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[EntrySchemaDetailed]:
        """
        List Entry schemas.

        See https://benchling.com/api/reference#/Schemas/listEntrySchemas
        """

        def api_call(next_token: NextToken) -> Response[EntrySchemasPaginatedList]:
            return self._entry_schemas_page(
                modified_at=modified_at,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: EntrySchemasPaginatedList) -> Optional[List[EntrySchemaDetailed]]:
            return body.entry_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_location_schema_by_id(self, schema_id: str) -> LocationSchema:
        """
        Get a location schema by ID.

        See https://benchling.com/api/reference#/Schemas/getLocationSchema
        """
        response = get_location_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _location_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[LocationSchemasPaginatedList]:
        return list_location_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_location_schemas(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[LocationSchema]:
        """
        List location schemas.

        See https://benchling.com/api/reference#/Schemas/listLocationSchemas
        """

        def api_call(next_token: NextToken) -> Response[LocationSchemasPaginatedList]:
            return self._location_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: LocationSchemasPaginatedList) -> List[LocationSchema]:
            return body.location_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_plate_schema_by_id(self, schema_id: str) -> PlateSchema:
        """
        Get a plate schema by ID.

        See https://benchling.com/api/reference#/Schemas/getPlateSchema
        """
        response = get_plate_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _plate_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[PlateSchemasPaginatedList]:
        return list_plate_schemas.sync_detailed(  # type:ignore
            client=self.client,
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_plate_schemas(
        self,
        *,
        page_size: Optional[int] = 50,
    ) -> PageIterator[PlateSchema]:
        """
        List plate schemas.

        See https://benchling.com/api/reference#/Schemas/listPlateSchemas
        """

        def api_call(next_token: NextToken) -> Response[PlateSchemasPaginatedList]:
            return self._plate_schemas_page(
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: PlateSchemasPaginatedList) -> Optional[List[PlateSchema]]:
            return body.plate_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_request_schema_by_id(self, schema_id: str) -> RequestSchema:
        """
        Get a Request schema by ID.

        See https://benchling.com/api/reference#/Schemas/getRequestSchema
        """
        response = get_request_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _request_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[RequestSchemasPaginatedList]:
        return list_request_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_request_schemas(
        self,
        *,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[RequestSchema]:
        """
        List Request schemas.

        See https://benchling.com/api/reference#/Schemas/listRequestSchemas
        """

        def api_call(next_token: NextToken) -> Response[RequestSchemasPaginatedList]:
            return self._request_schemas_page(
                modified_at=modified_at,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: RequestSchemasPaginatedList) -> Optional[List[RequestSchema]]:
            return body.request_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_request_task_schema_by_id(self, schema_id: str) -> RequestTaskSchema:
        """
        Get a Request Task schema by ID.

        See https://benchling.com/api/reference#/Schemas/getRequestTaskSchema
        """
        response = get_request_task_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _request_task_schemas_page(
        self,
        *,
        next_token: Optional[str] = None,
        modified_at: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[RequestTaskSchemasPaginatedList]:
        return list_request_task_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_request_task_schemas(
        self, *, modified_at: Optional[str] = None, page_size: Optional[int] = 50
    ) -> PageIterator[RequestTaskSchema]:
        """
        List Request Task schemas.

        See https://benchling.com/api/reference#/Schemas/listRequestTaskSchemas
        """

        def api_call(
            next_token: NextToken,
        ) -> Response[RequestTaskSchemasPaginatedList]:
            return self._request_task_schemas_page(
                modified_at=modified_at, next_token=next_token, page_size=page_size
            )

        def results_extractor(body: RequestTaskSchemasPaginatedList) -> Optional[List[RequestTaskSchema]]:
            return body.request_task_schemas

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_workflow_task_schema_by_id(self, schema_id: str) -> WorkflowTaskSchema:
        """
        Get a Workflow Task schema by ID.

        See https://benchling.com/api/reference#/Schemas/getWorkflowTaskSchema
        """
        response = get_workflow_task_schema.sync_detailed(client=self.client, schema_id=schema_id)
        return model_from_detailed(response)

    @api_method
    def _workflow_task_schemas_page(
        self,
        *,
        modified_at: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[WorkflowTaskSchemasPaginatedList]:
        return list_workflow_task_schemas.sync_detailed(  # type:ignore
            client=self.client,
            modified_at=none_as_unset(modified_at),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list_workflow_task_schemas(
        self, *, modified_at: Optional[str] = None, page_size: Optional[int] = 50
    ) -> PageIterator[WorkflowTaskSchema]:
        """
        List Workflow Task schemas.

        See https://benchling.com/api/reference#/Schemas/listWorkflowTaskSchemas
        """

        def api_call(
            next_token: NextToken,
        ) -> Response[WorkflowTaskSchemasPaginatedList]:
            return self._workflow_task_schemas_page(
                modified_at=modified_at, next_token=next_token, page_size=page_size
            )

        def results_extractor(body: WorkflowTaskSchemasPaginatedList) -> Optional[List[WorkflowTaskSchema]]:
            return body.workflow_task_schemas

        return PageIterator(api_call, results_extractor)
