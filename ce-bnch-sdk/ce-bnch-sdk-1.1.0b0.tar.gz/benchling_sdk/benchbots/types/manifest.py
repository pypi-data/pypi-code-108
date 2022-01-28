from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, List, Optional, Type, TypeVar, Union

from dataclasses_json import dataclass_json
from dataclasses_jsonschema import JsonSchemaMixin
from dataclasses_jsonschema.type_defs import JsonDict
from typing_extensions import Literal
import yaml

from benchling_sdk.benchbots.helpers.case_conversion import to_pascal_case, to_snake_case
from benchling_sdk.models import (
    AaSequence,
    AssayResult,
    AssayRun,
    Box,
    Container,
    CustomEntity,
    DnaSequence,
    Entry,
    Location,
    Mixture,
    Plate,
    Request,
    WorkflowTask,
)


class NamedResourceType(str, Enum):
    AA_SEQUENCE = "aa-sequence"
    BOX = "box"
    CONTAINER = "container"
    CUSTOM_ENTITY = "custom-entity"
    DNA_ALIGNMENT = "dna-alignment"  # Cannot be auto-linked because there is no SDK support
    DNA_OLIGO = "dna-oligo"  # Cannot be auto-linked because there is no SDK support
    DNA_SEQUENCE = "dna-sequence"
    ENTRY = "entry"
    FOLDER = "folder"
    LABEL_PRINTER = "label-printer"
    LABEL_TEMPLATE = "label-template"
    LOCATION = "location"
    MIXTURE = "mixture"
    PLATE = "plate"
    PROJECT = "project"
    REGISTRY = "registry"


class UnnamedResourceType(str, Enum):
    ASSAY_RESULT = "assay-result"
    ASSAY_RUN = "assay-run"
    AUTOMATION_INPUT_GENERATOR = "automation-input-generator"
    AUTOMATION_OUTPUT_PROCESSOR = "automation-output-processor"
    BLOB = "blob"
    REQUEST = "request"


AUTOLINKED_RESOURCE_TYPES = [
    NamedResourceType.AA_SEQUENCE,
    NamedResourceType.BOX,
    NamedResourceType.CONTAINER,
    NamedResourceType.CUSTOM_ENTITY,
    NamedResourceType.DNA_SEQUENCE,
    NamedResourceType.ENTRY,
    NamedResourceType.FOLDER,
    NamedResourceType.LABEL_PRINTER,
    NamedResourceType.LABEL_TEMPLATE,
    NamedResourceType.LOCATION,
    NamedResourceType.MIXTURE,
    NamedResourceType.PLATE,
    NamedResourceType.PROJECT,
    NamedResourceType.REGISTRY,
]


class SchemaType(str, Enum):
    ENTITY_SCHEMA = "entity-schema"
    CONTAINER_SCHEMA = "container-schema"
    PLATE_SCHEMA = "plate-schema"
    BOX_SCHEMA = "box-schema"
    LOCATION_SCHEMA = "location-schema"
    ASSAY_RESULT_SCHEMA = "assay-result-schema"
    ASSAY_RUN_SCHEMA = "assay-run-schema"
    REQUEST_SCHEMA = "request-schema"
    TASK_SCHEMA = "task-schema"
    ENTRY_SCHEMA = "entry-schema"
    WORKFLOW_TASK_SCHEMA = "workflow-task-schema"


SCHEMA_TYPE_TO_INSTANCE = {
    SchemaType.CONTAINER_SCHEMA: Container,
    SchemaType.PLATE_SCHEMA: Plate,
    SchemaType.BOX_SCHEMA: Box,
    SchemaType.LOCATION_SCHEMA: Location,
    SchemaType.ASSAY_RESULT_SCHEMA: AssayResult,
    SchemaType.ASSAY_RUN_SCHEMA: AssayRun,
    SchemaType.REQUEST_SCHEMA: Request,
    SchemaType.ENTRY_SCHEMA: Entry,
    SchemaType.WORKFLOW_TASK_SCHEMA: WorkflowTask,
}


SCHEMA_TYPE_TO_SERVICE_NAME = {
    SchemaType.CONTAINER_SCHEMA: "containers",
    SchemaType.PLATE_SCHEMA: "plates",
    SchemaType.BOX_SCHEMA: "boxes",
    SchemaType.LOCATION_SCHEMA: "locations",
    SchemaType.ASSAY_RESULT_SCHEMA: "assay_results",
    SchemaType.ASSAY_RUN_SCHEMA: "assay_runs",
    SchemaType.REQUEST_SCHEMA: "requests",
    SchemaType.ENTRY_SCHEMA: "notebook",
    SchemaType.WORKFLOW_TASK_SCHEMA: "workflow_tasks",
}


class EntityType(str, Enum):
    AA_SEQUENCE = "aa_sequence"
    CUSTOM_ENTITY = "custom_entity"
    DNA_SEQUENCE = "dna_sequence"
    MIXTURE = "mixture"


ENTITY_TYPE_TO_INSTANCE = {
    EntityType.AA_SEQUENCE: AaSequence,
    EntityType.CUSTOM_ENTITY: CustomEntity,
    EntityType.DNA_SEQUENCE: DnaSequence,
    EntityType.MIXTURE: Mixture,
}

ENTITY_TYPE_TO_SERVICE_NAME = {
    EntityType.AA_SEQUENCE: "aa_sequences",
    EntityType.CUSTOM_ENTITY: "custom_entities",
    EntityType.DNA_SEQUENCE: "dna_sequences",
    EntityType.MIXTURE: "mixtures",
}


@dataclass_json
class ManifestComponent(JsonSchemaMixin):
    pass


class NamedManifestComponent(ManifestComponent):
    name: str

    @property
    def pascal_case_name(self) -> str:
        return to_pascal_case(self.name)

    @property
    def snake_case_name(self) -> str:
        return to_snake_case(self.name)


@dataclass
class BaseDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore
    name: str
    description: Optional[str] = None
    is_resource_named: ClassVar[bool] = True


@dataclass
class SchemaDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore
    """
    Entity schemas are represented separately as `EntitySchemaDependency`.

    Workflow task schemas are represented separately as `WorkflowTaskSchemaDependency`.
    """

    # Unfortunately dataclasses-jsonschema does not support inheritance with `allow_additional_props=False`.
    name: str
    # Exclude workflow task schemas which are special
    resourceType: Union[
        Literal[SchemaType.ENTITY_SCHEMA],
        Literal[SchemaType.CONTAINER_SCHEMA],
        Literal[SchemaType.PLATE_SCHEMA],
        Literal[SchemaType.BOX_SCHEMA],
        Literal[SchemaType.LOCATION_SCHEMA],
        Literal[SchemaType.ASSAY_RESULT_SCHEMA],
        Literal[SchemaType.ASSAY_RUN_SCHEMA],
        Literal[SchemaType.REQUEST_SCHEMA],
        Literal[SchemaType.TASK_SCHEMA],
        Literal[SchemaType.ENTRY_SCHEMA],
    ]
    description: Optional[str] = None
    fieldDefinitions: Optional[List[BaseDependency]] = None
    is_resource_named: ClassVar[bool] = True

    @property
    def instance_pascal_case_name(self) -> str:
        return SCHEMA_TYPE_TO_INSTANCE[self.resourceType].__name__

    @property
    def instance_snake_case_name(self) -> str:
        return to_snake_case(self.instance_pascal_case_name)

    @property
    def service_name(self) -> str:
        return SCHEMA_TYPE_TO_SERVICE_NAME[self.resourceType]


@dataclass
class EntitySchemaResourceProperties(ManifestComponent, allow_additional_props=False):  # type: ignore
    type: EntityType


@dataclass
class EntitySchemaDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore
    # Unfortunately dataclasses-jsonschema does not support inheritance with `allow_additional_props=False`.
    name: str
    resourceType: Literal[SchemaType.ENTITY_SCHEMA]
    resourceProperties: EntitySchemaResourceProperties
    description: Optional[str] = None
    fieldDefinitions: Optional[List[BaseDependency]] = None
    is_resource_named: ClassVar[bool] = True

    @property
    def instance_pascal_case_name(self) -> str:
        return ENTITY_TYPE_TO_INSTANCE[self.resourceProperties.type].__name__

    @property
    def instance_snake_case_name(self) -> str:
        return to_snake_case(self.instance_pascal_case_name)

    @property
    def service_name(self) -> str:
        return ENTITY_TYPE_TO_SERVICE_NAME[self.resourceProperties.type]


@dataclass
class DropdownDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore
    # Unfortunately dataclasses-jsonschema does not support inheritance with `allow_additional_props=False`.
    name: str
    resourceType: Literal["dropdown"]
    description: Optional[str] = None
    options: Optional[List[BaseDependency]] = None
    is_resource_named: ClassVar[bool] = True


@dataclass
class _WorkflowTaskSchemaOutput(ManifestComponent, allow_additional_props=False):  # type: ignore
    fieldDefinitions: Optional[List[BaseDependency]] = None


@dataclass
class WorkflowTaskSchemaDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore

    # Unfortunately dataclasses-jsonschema does not support inheritance with `allow_additional_props=False`.
    name: str
    resourceType: Literal[SchemaType.WORKFLOW_TASK_SCHEMA]
    description: Optional[str] = None
    fieldDefinitions: Optional[List[BaseDependency]] = None
    is_resource_named: ClassVar[bool] = True
    output: Optional[_WorkflowTaskSchemaOutput] = None


@dataclass
class WorkflowTaskStatusDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore
    # Unfortunately dataclasses-jsonschema does not support inheritance with `allow_additional_props=False`.
    name: str
    resourceType: Literal["workflow-task-status"]
    description: Optional[str] = None
    is_resource_named: ClassVar[bool] = True


@dataclass
class NamedResourceDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore
    # Unfortunately dataclasses-jsonschema does not support inheritance with `allow_additional_props=False`.
    name: str
    resourceType: NamedResourceType
    description: Optional[str] = None
    is_resource_named: ClassVar[bool] = True


@dataclass
class UnnamedResourceDependency(NamedManifestComponent, allow_additional_props=False):  # type: ignore
    # Unfortunately dataclasses-jsonschema does not support inheritance with `allow_additional_props=False`.
    name: str  # The dependency still has a name, but the resource itself does not.
    resourceType: UnnamedResourceType
    description: Optional[str] = None
    is_resource_named: ClassVar[bool] = False


@dataclass
class ManifestInfo(ManifestComponent, allow_additional_props=False):  # type: ignore
    name: str
    version: str
    description: Optional[str] = None


Dependency = Union[
    SchemaDependency,
    EntitySchemaDependency,
    DropdownDependency,
    NamedResourceDependency,
    UnnamedResourceDependency,
    WorkflowTaskStatusDependency,
    WorkflowTaskSchemaDependency,
]


@dataclass
class _Manifest(ManifestComponent, allow_additional_props=False):  # type: ignore
    manifestFormatVersion: Literal[1]
    info: ManifestInfo
    dependencies: Optional[List[Dependency]]


T = TypeVar("T", bound="Manifest")


class Manifest(_Manifest):
    @classmethod
    def from_dict(cls: Type[T], data: JsonDict, validate=True, validate_enums: bool = True) -> T:  # type: ignore
        # from_dict is not supported properly by dataclasses-json because it's a union type.
        # See https://github.com/lidatong/dataclasses-json/issues/222.
        manifest = super().from_dict(data)
        if manifest.dependencies:
            for i, dependency in enumerate(manifest.dependencies):
                assert isinstance(dependency, dict)
                if dependency["resourceType"] == "dropdown":
                    manifest.dependencies[i] = DropdownDependency.from_dict(dependency)
                elif dependency["resourceType"] == SchemaType.WORKFLOW_TASK_SCHEMA:
                    manifest.dependencies[i] = WorkflowTaskSchemaDependency.from_dict(dependency)
                elif dependency["resourceType"] == SchemaType.ENTITY_SCHEMA:
                    manifest.dependencies[i] = EntitySchemaDependency.from_dict(dependency)
                elif dependency["resourceType"] == "workflow-task-status":
                    manifest.dependencies[i] = WorkflowTaskStatusDependency.from_dict(dependency)
                elif dependency["resourceType"] in [schema_type.value for schema_type in SchemaType]:
                    manifest.dependencies[i] = SchemaDependency.from_dict(dependency)
                elif dependency["resourceType"] in [
                    resource_type.value for resource_type in NamedResourceType
                ]:
                    manifest.dependencies[i] = NamedResourceDependency.from_dict(dependency)
                else:
                    manifest.dependencies[i] = UnnamedResourceDependency.from_dict(dependency)
        return manifest

    @classmethod
    def from_file(cls: Type[T], file_path: str) -> T:
        with open(file_path) as f:
            manifest_yaml = f.read()
        manifest_dict = yaml.load(manifest_yaml, Loader=yaml.SafeLoader)
        return cls.from_dict(manifest_dict)
