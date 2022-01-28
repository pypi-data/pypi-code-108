from typing import Any, Optional, TypeVar, Union
from unittest.mock import MagicMock
from uuid import uuid4

from benchling_sdk.benchbots.benchling_store import AllSchemaEmbeddable, Resource, Schema
from benchling_sdk.benchbots.dependencies.dependency_resolver import DependencyResolver
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


class MockDependencyResolver(DependencyResolver):
    def resolve_resource_by_id_or_name(
        self,
        resource_dependency: NamedResourceDependency,
        initial_id_or_name: str,
    ) -> Resource:
        return _mock_dependency_link(initial_id_or_name, resource_dependency.resourceType)

    def resolve_option_by_id_or_name(
        self,
        dropdown: DropdownSummary,
        initial_id_or_name: str,
        dependency_name: str,
    ) -> DropdownOption:
        return _mock_dependency_link(initial_id_or_name, DropdownOption)

    def resolve_schema_by_id_or_name(
        self,
        schema_dependency: Union[EntitySchemaDependency, SchemaDependency, WorkflowTaskSchemaDependency],
        initial_id_or_name: str,
    ) -> Schema:
        return _mock_dependency_link(initial_id_or_name, Schema)

    def resolve_field_by_id_or_name(
        self,
        schema: AllSchemaEmbeddable,
        initial_id_or_name: str,
        dependency_name: str,
    ) -> Any:
        return _mock_dependency_link(initial_id_or_name)

    def resolve_dropdown_by_id_or_name(
        self,
        dropdown_dependency: DropdownDependency,
        initial_id_or_name: str,
    ) -> DropdownSummary:
        return _mock_dependency_link(initial_id_or_name, DropdownSummary)

    def resolve_workflow_task_status_by_id_or_name(
        self, workflow_task_status_dependency: WorkflowTaskStatusDependency, initial_id_or_name: str
    ) -> WorkflowTaskStatus:
        return _mock_dependency_link(initial_id_or_name, WorkflowTaskStatus)


def _mock_dependency_link(initial_id_or_name: str, target_type: Optional[T] = None) -> Any:
    mock_result = MagicMock(target_type) if target_type else MagicMock()
    mock_result.id = _unique_string(base_string=initial_id_or_name, prefix_new_string="mock_id")
    mock_result.name = _unique_string(base_string=initial_id_or_name, prefix_new_string="mock_name")
    return mock_result


def _unique_string(base_string: Optional[str] = None, prefix_new_string: str = "") -> str:
    # We don't REALLY care about true uniqueness as much as a reasonably readable, different-ish string
    unique_suffix = str(uuid4())[:8]
    if base_string:
        return f"{base_string}_{unique_suffix}"
    return f"{prefix_new_string}_{unique_suffix}"
