from http import HTTPStatus
from typing import Any, cast, Dict, Iterable, List, Optional, Union

from benchling_sdk.benchbots.helpers.find import find, find_by_id_or_name
from benchling_sdk.benchbots.types.manifest import EntityType, NamedResourceType, SchemaType
from benchling_sdk.benchling import Benchling
from benchling_sdk.errors import BenchlingError
from benchling_sdk.models import (
    AaSequence,
    AssayResultSchema,
    AssayRunSchema,
    Box,
    BoxSchema,
    Container,
    CustomEntity,
    DnaAlignment,
    DnaSequence,
    DropdownOption,
    DropdownSummary,
    EntitySchema,
    Entry,
    EntrySchemaDetailed,
    Folder,
    LabelTemplate,
    Location,
    Plate,
    PlateSchema,
    Printer,
    Project,
    Registry,
    RequestSchema,
    Schema as BaseSchema,
    WorkflowOutputSchema,
    WorkflowTaskSchema,
    WorkflowTaskStatus,
)
from benchling_sdk.services.base_service import BaseService

Schema = Union[
    AssayResultSchema,
    AssayRunSchema,
    BoxSchema,
    EntitySchema,
    EntrySchemaDetailed,
    PlateSchema,
    RequestSchema,
    BaseSchema,
    WorkflowTaskSchema,
]

AllSchemaEmbeddable = Union[Schema, WorkflowOutputSchema]


Resource = Union[
    AaSequence,
    Box,
    Container,
    CustomEntity,
    DnaAlignment,
    DnaSequence,
    Entry,
    Folder,
    LabelTemplate,
    Location,
    Plate,
    Printer,
    Project,
    Registry,
]


class BenchlingStore:
    _benchling: Benchling
    _schemas: Dict[SchemaType, List[Schema]]
    _dropdowns: Optional[List[DropdownSummary]]
    _dropdown_options_by_dropdown_id: Dict[str, List[DropdownOption]]
    _workflow_task_statuses: Optional[List[WorkflowTaskStatus]]

    def __init__(self, benchling: Benchling) -> None:
        self._benchling = benchling
        self._schemas = {}
        self._dropdowns = None
        self._dropdown_options_by_dropdown_id = {}
        self._workflow_task_statuses = None

    def _fetch_schema_pages(self, schema_type: SchemaType) -> Iterable[Iterable[Schema]]:
        schema_type_to_list_fn = {
            SchemaType.ENTITY_SCHEMA: self._benchling.schemas.list_entity_schemas,
            SchemaType.CONTAINER_SCHEMA: self._benchling.schemas.list_container_schemas,
            SchemaType.PLATE_SCHEMA: self._benchling.schemas.list_plate_schemas,
            SchemaType.BOX_SCHEMA: self._benchling.schemas.list_box_schemas,
            SchemaType.LOCATION_SCHEMA: self._benchling.schemas.list_location_schemas,
            SchemaType.ASSAY_RESULT_SCHEMA: self._benchling.schemas.list_assay_result_schemas,
            SchemaType.ASSAY_RUN_SCHEMA: self._benchling.schemas.list_assay_run_schemas,
            SchemaType.REQUEST_SCHEMA: self._benchling.schemas.list_request_schemas,
            SchemaType.ENTRY_SCHEMA: self._benchling.schemas.list_entry_schemas,
            SchemaType.WORKFLOW_TASK_SCHEMA: self._benchling.schemas.list_workflow_task_schemas,
        }
        return schema_type_to_list_fn[schema_type]()  # type: ignore

    def get_schemas(self, schema_type: SchemaType, entity_type: Optional[EntityType]) -> List[Schema]:
        if schema_type not in self._schemas:
            self._schemas[schema_type] = [
                schema for page in self._fetch_schema_pages(schema_type) for schema in page
            ]

        schemas = self._schemas[schema_type]
        if entity_type:
            assert schema_type == SchemaType.ENTITY_SCHEMA
            return [schema for schema in schemas if schema.type == entity_type.value]  # type: ignore
        else:
            return schemas

    def get_schema_by_id_or_name(
        self, schema_type: SchemaType, entity_type: Optional[EntityType], id_or_name: str
    ) -> Optional[Schema]:
        return find_by_id_or_name(self.get_schemas(schema_type, entity_type), id_or_name)

    def get_schema_field_by_id_or_name(self, schema: AllSchemaEmbeddable, id_or_name: str) -> Any:
        return find_by_id_or_name(schema.field_definitions, id_or_name)  # type: ignore

    def get_dropdowns(self) -> List[DropdownSummary]:
        if self._dropdowns is None:
            self._dropdowns = [dropdown for page in self._benchling.dropdowns.list() for dropdown in page]
        return self._dropdowns

    def get_workflow_task_statuses(self) -> List[WorkflowTaskStatus]:
        if self._workflow_task_statuses is None:
            # There is currently no other way to get workflow task status by ID/name other than paging through
            # every workflow task schema
            # In general, unless a user keeps entering non-matches, this should match on the first workflow task schema
            statuses = []
            # Would prefer statuses to be a Set but WorkflowTaskStatus is not hashable
            seen_status_ids = set()
            workflow_task_schemas = self.get_schemas(SchemaType.WORKFLOW_TASK_SCHEMA, entity_type=None)
            for untyped_task in workflow_task_schemas:
                task = cast(WorkflowTaskSchema, untyped_task)
                if task.status_lifecycle and task.status_lifecycle.statuses:
                    for status in task.status_lifecycle.statuses:
                        if status.id not in seen_status_ids:
                            statuses.append(status)
                            seen_status_ids.add(status.id)
            self._workflow_task_statuses = statuses
        return self._workflow_task_statuses

    def get_dropdown_by_id_or_name(self, id_or_name: str) -> Optional[DropdownSummary]:
        return find_by_id_or_name(self.get_dropdowns(), id_or_name)

    def get_dropdown_options(self, dropdown_id: str) -> List[DropdownOption]:
        if dropdown_id not in self._dropdown_options_by_dropdown_id:
            self._dropdown_options_by_dropdown_id[dropdown_id] = cast(
                List[DropdownOption], self._benchling.dropdowns.get_by_id(dropdown_id).options
            )
        return self._dropdown_options_by_dropdown_id[dropdown_id]

    def get_dropdown_option_by_id_or_name(
        self, dropdown_id: str, id_or_name: str
    ) -> Optional[DropdownOption]:
        return find_by_id_or_name(self.get_dropdown_options(dropdown_id), id_or_name)

    def get_workflow_task_status_by_id_or_name(self, id_or_name: str) -> Optional[WorkflowTaskStatus]:
        for status in self.get_workflow_task_statuses():
            if (
                status.id == id_or_name
                or status.display_name == id_or_name
                or str(status.status_type).lower() == id_or_name.lower()
            ):
                return status
        return None

    def _resource_service(self, resource_type: NamedResourceType) -> BaseService:
        resource_type_to_service = {
            NamedResourceType.AA_SEQUENCE: self._benchling.aa_sequences,
            NamedResourceType.BOX: self._benchling.boxes,
            NamedResourceType.CONTAINER: self._benchling.containers,
            NamedResourceType.CUSTOM_ENTITY: self._benchling.custom_entities,
            NamedResourceType.DNA_SEQUENCE: self._benchling.dna_sequences,
            NamedResourceType.ENTRY: self._benchling.entries,
            NamedResourceType.FOLDER: self._benchling.folders,
            NamedResourceType.LABEL_PRINTER: self._benchling.printers,
            NamedResourceType.LABEL_TEMPLATE: self._benchling.label_templates,
            NamedResourceType.LOCATION: self._benchling.locations,
            NamedResourceType.PLATE: self._benchling.plates,
            NamedResourceType.PROJECT: self._benchling.projects,
            NamedResourceType.REGISTRY: self._benchling.registry,
        }
        if resource_type in resource_type_to_service:
            return resource_type_to_service[resource_type]
        else:
            raise NotImplementedError(
                f'The dependency linker does not yet support resources of type "{resource_type}".'
            )

    def get_resource(self, resource_type: NamedResourceType, resource_id: str) -> Optional[Resource]:
        if resource_type == NamedResourceType.ENTRY:
            try:
                return self._benchling.entries.get_entry_by_id(resource_id)
            except BenchlingError as e:
                if e.status_code == HTTPStatus.NOT_FOUND:
                    return None
                else:
                    raise e
        elif resource_type == NamedResourceType.LABEL_PRINTER:
            registries = self._benchling.registry.registries()
            return find(
                [
                    printer
                    for registry in registries
                    for printer in self._benchling.printers.get_list(registry.id)
                ],
                lambda x: x.id == resource_id,
            )
        elif resource_type == NamedResourceType.LABEL_TEMPLATE:
            registries = self._benchling.registry.registries()
            return find(
                [
                    template
                    for registry in registries
                    for template in self._benchling.label_templates.get_list(registry.id)
                ],
                lambda x: x.id == resource_id,
            )
        elif resource_type == NamedResourceType.REGISTRY:
            return find(self._benchling.registry.registries(), lambda x: x.id == resource_id)
        else:
            try:
                # "BaseService" has no attribute "get_by_id"
                return self._resource_service(resource_type).get_by_id(resource_id)  # type: ignore
            except BenchlingError as e:
                if e.status_code == HTTPStatus.NOT_FOUND:
                    return None
                else:
                    raise e

    def _get_resources_by_name(self, resource_type: NamedResourceType, resource_name: str) -> List[Resource]:
        if resource_type == NamedResourceType.ENTRY:
            return [
                resource
                for page in self._benchling.entries.list_entries(name=resource_name)
                for resource in page
            ]
        elif resource_type == NamedResourceType.FOLDER:
            return [
                resource
                for page in self._benchling.folders.list(name_includes=resource_name)
                for resource in page
            ]
        elif resource_type == NamedResourceType.LABEL_PRINTER:
            registries = self._benchling.registry.registries()
            return [
                printer
                for registry in registries
                for printer in self._benchling.printers.get_list(registry.id)
            ]
        elif resource_type == NamedResourceType.LABEL_TEMPLATE:
            registries = self._benchling.registry.registries()
            return [
                template
                for registry in registries
                for template in self._benchling.label_templates.get_list(registry.id)
            ]
        elif resource_type == NamedResourceType.PROJECT:
            return [resource for page in self._benchling.projects.list() for resource in page]
        elif resource_type == NamedResourceType.REGISTRY:
            # Copy list to avoid type error because lists are invariant
            return list(self._benchling.registry.registries())
        else:
            return [
                resource
                # "BaseService" has no attribute "list"
                for page in self._resource_service(resource_type).list(name=resource_name)  # type: ignore
                for resource in page
            ]

    def get_resource_by_name(
        self, resource_type: NamedResourceType, resource_name: str
    ) -> Optional[Resource]:
        return find(
            self._get_resources_by_name(resource_type, resource_name), lambda x: x.name == resource_name
        )

    def get_resource_by_id_or_name(
        self, resource_type: NamedResourceType, id_or_name: str
    ) -> Optional[Resource]:
        return self.get_resource(resource_type, id_or_name) or self.get_resource_by_name(
            resource_type, id_or_name
        )
