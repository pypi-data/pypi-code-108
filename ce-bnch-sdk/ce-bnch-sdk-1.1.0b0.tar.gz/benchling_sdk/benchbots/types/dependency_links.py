from __future__ import annotations

from dataclasses import dataclass
from typing import List, Type, TypeVar, Union

from dataclasses_json import dataclass_json, DataClassJsonMixin
from dataclasses_json.core import Json
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass_json
@dataclass
class ApiIdentifiedLink(JsonSchemaMixin):
    name: str
    resourceId: str


@dataclass_json
@dataclass
class NamedApiIdentifiedLink(ApiIdentifiedLink):
    resourceName: str


@dataclass_json
@dataclass
class SchemaFieldLink(NamedApiIdentifiedLink):
    pass


@dataclass_json
@dataclass
class SchemaLink(NamedApiIdentifiedLink):
    fieldDefinitions: List[SchemaFieldLink]


@dataclass_json
@dataclass
class WorkflowTaskOutputSchemaLink:
    fieldDefinitions: List[SchemaFieldLink]


@dataclass_json
@dataclass
class WorkflowTaskSchemaLink(SchemaLink):
    fieldDefinitions: List[SchemaFieldLink]
    output: WorkflowTaskOutputSchemaLink
    resourceType: str = "workflow-task-schema"


@dataclass_json
@dataclass
class DropdownOptionLink(NamedApiIdentifiedLink):
    pass


@dataclass_json
@dataclass
class WorkflowTaskStatusLink(NamedApiIdentifiedLink):
    resourceType: str = "workflow-task-status"


@dataclass_json
@dataclass
class DropdownLink(NamedApiIdentifiedLink):
    options: List[DropdownOptionLink]


@dataclass_json
@dataclass
class NamedResourceLink(NamedApiIdentifiedLink):
    pass


@dataclass_json
@dataclass
class UnnamedResourceLink(ApiIdentifiedLink):
    pass


T = TypeVar("T", bound="DependencyLinks")


@dataclass_json
@dataclass
class _DependencyLinks(DataClassJsonMixin):
    dependencies: List[
        Union[
            SchemaLink,
            DropdownLink,
            NamedResourceLink,
            UnnamedResourceLink,
            WorkflowTaskStatusLink,
            WorkflowTaskSchemaLink,
        ]
    ]


class DependencyLinks(_DependencyLinks):
    @classmethod
    def from_dict(cls: Type[T], kvs: Json, *, infer_missing=False) -> T:
        # from_dict is not supported properly by dataclasses-json because it's a union type.
        # See https://github.com/lidatong/dataclasses-json/issues/222.
        dependency_link = super().from_dict(kvs, infer_missing=infer_missing)
        for i, dependency in enumerate(dependency_link.dependencies):
            assert isinstance(dependency, dict)
            if "resourceType" in dependency and dependency["resourceType"] == "workflow-task-schema":
                dependency_link.dependencies[i] = WorkflowTaskSchemaLink.from_dict(dependency)
            elif "resourceType" in dependency and dependency["resourceType"] == "workflow-task-status":
                dependency_link.dependencies[i] = WorkflowTaskStatusLink.from_dict(dependency)
            elif "fieldDefinitions" in dependency:
                dependency_link.dependencies[i] = SchemaLink.from_dict(dependency)
            elif "options" in dependency:
                dependency_link.dependencies[i] = DropdownLink.from_dict(dependency)
            elif "resourceName" in dependency:
                dependency_link.dependencies[i] = NamedResourceLink.from_dict(dependency)
            else:
                dependency_link.dependencies[i] = UnnamedResourceLink.from_dict(dependency)
        return dependency_link

    @classmethod
    def from_file(cls: Type[T], file_path: str) -> T:
        with open(file_path) as f:
            contents = f.read()
        return cls.from_json(contents) if contents else cls(dependencies=[])
