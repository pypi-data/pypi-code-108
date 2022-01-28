from typing import Any, Callable, Optional, TypeVar, Union

import typer

from benchling_sdk.benchbots.benchling_store import AllSchemaEmbeddable, BenchlingStore, Resource, Schema
from benchling_sdk.benchbots.dependencies.dependency_resolver import DependencyResolver
from benchling_sdk.benchbots.helpers.find import MultipleMatchesError
from benchling_sdk.benchbots.types.manifest import (
    DropdownDependency,
    EntitySchemaDependency,
    NamedResourceDependency,
    SchemaDependency,
    WorkflowTaskSchemaDependency,
    WorkflowTaskStatusDependency,
)
from benchling_sdk.models import DropdownOption, DropdownSummary, WorkflowTaskStatus

T = TypeVar("T")


def _prompt_until_success(
    initial_value: str,
    resolver: Callable[[str], Optional[T]],
    object_type_str: str,
    dependency_name: str,
) -> T:
    value = initial_value
    while True:
        try:
            resolved_object = resolver(value)
        except MultipleMatchesError:
            value = typer.prompt(
                f'Multiple matches found for dependency "{dependency_name}" '
                f'named "{value}". '
                f"Please enter the correct {object_type_str}'s API ID."
            )
            continue

        if resolved_object:
            return resolved_object
        else:
            value = typer.prompt(
                f'No {object_type_str} found for dependency "{dependency_name}" '
                f'with id or name "{value}". '
                f"Please enter the correct {object_type_str}'s API ID or name"
            )


class BenchlingDependencyResolver(DependencyResolver):
    benchling_store: BenchlingStore

    def __init__(self, benchling_store: BenchlingStore):
        self.benchling_store = benchling_store

    def resolve_schema_by_id_or_name(
        self,
        schema_dependency: Union[EntitySchemaDependency, SchemaDependency, WorkflowTaskSchemaDependency],
        initial_id_or_name: str,
    ) -> Schema:
        entity_type = (
            schema_dependency.resourceProperties.type
            if isinstance(schema_dependency, EntitySchemaDependency)
            else None
        )
        schema_type_repr = (
            f"{entity_type} {schema_dependency.resourceType}"
            if entity_type
            else schema_dependency.resourceType
        )
        # error: Incompatible return value type (got "object", expected "Union[AssayResultSchema...]")
        # I think it might be a MyPy issue; see https://github.com/python/mypy/issues/6898
        return _prompt_until_success(  # type: ignore
            initial_value=initial_id_or_name,
            resolver=lambda id_or_name: self.benchling_store.get_schema_by_id_or_name(
                schema_dependency.resourceType, entity_type, id_or_name
            ),
            object_type_str=schema_type_repr,
            dependency_name=schema_dependency.name,
        )

    def resolve_field_by_id_or_name(
        self,
        schema: AllSchemaEmbeddable,
        initial_id_or_name: str,
        dependency_name: str,
    ) -> Any:
        return _prompt_until_success(
            initial_value=initial_id_or_name,
            resolver=lambda id_or_name: self.benchling_store.get_schema_field_by_id_or_name(
                schema, id_or_name
            ),
            object_type_str="field",
            dependency_name=dependency_name,
        )

    def resolve_dropdown_by_id_or_name(
        self,
        dropdown_dependency: DropdownDependency,
        initial_id_or_name: str,
    ) -> DropdownSummary:
        return _prompt_until_success(
            initial_value=initial_id_or_name,
            resolver=self.benchling_store.get_dropdown_by_id_or_name,
            object_type_str="dropdown",
            dependency_name=dropdown_dependency.name,
        )

    def resolve_option_by_id_or_name(
        self,
        dropdown: DropdownSummary,
        initial_id_or_name: str,
        dependency_name: str,
    ) -> DropdownOption:
        return _prompt_until_success(
            initial_value=initial_id_or_name,
            resolver=lambda id_or_name: self.benchling_store.get_dropdown_option_by_id_or_name(
                dropdown.id, id_or_name
            ),
            object_type_str="option",
            dependency_name=dependency_name,
        )

    def resolve_workflow_task_status_by_id_or_name(
        self,
        workflow_task_status_dependency: WorkflowTaskStatusDependency,
        initial_id_or_name: str,
    ) -> WorkflowTaskStatus:
        return _prompt_until_success(
            initial_value=initial_id_or_name,
            resolver=lambda id_or_name: self.benchling_store.get_workflow_task_status_by_id_or_name(
                id_or_name
            ),
            object_type_str="workflow-task-status",
            dependency_name=workflow_task_status_dependency.name,
        )

    def resolve_resource_by_id_or_name(
        self,
        resource_dependency: NamedResourceDependency,
        initial_id_or_name: str,
    ) -> Resource:
        # error: Incompatible return value type (got "object", expected "Union[AaSequence...]")
        # I think it might be a MyPy issue; see https://github.com/python/mypy/issues/6898
        return _prompt_until_success(  # type: ignore
            initial_value=initial_id_or_name,
            resolver=lambda id_or_name: self.benchling_store.get_resource_by_id_or_name(
                resource_dependency.resourceType, id_or_name
            ),
            object_type_str=resource_dependency.resourceType,
            dependency_name=resource_dependency.name,
        )
