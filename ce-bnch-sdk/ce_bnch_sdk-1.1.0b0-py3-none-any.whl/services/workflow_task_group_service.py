import datetime
from typing import Iterable, List, Optional

from benchling_api_client.api.workflow_task_groups import (
    archive_workflow_task_groups,
    create_workflow_task_group,
    get_workflow_task_group,
    list_workflow_task_groups,
    unarchive_workflow_task_groups,
    update_workflow_task_group,
)
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    WorkflowTaskGroup,
    WorkflowTaskGroupArchiveReason,
    WorkflowTaskGroupCreate,
    WorkflowTaskGroupsArchivalChange,
    WorkflowTaskGroupsArchive,
    WorkflowTaskGroupsPaginatedList,
    WorkflowTaskGroupsUnarchive,
    WorkflowTaskGroupUpdate,
)
from benchling_sdk.services.base_service import BaseService


class WorkflowTaskGroupService(BaseService):
    """
    Workflow Task Groups.

    Workflow task groups are groups of workflow tasks of the same schema.

    See https://benchling.com/api/reference#/Workflow%20Task%20Groups
    """

    @api_method
    def get_by_id(self, workflow_task_group_id: str) -> WorkflowTaskGroup:
        """
        Get a workflow task group.

        See https://benchling.com/api/reference#/Workflow%20Task%20Groups/getWorkflowTaskGroup
        """
        response = get_workflow_task_group.sync_detailed(
            client=self.client, workflow_task_group_id=workflow_task_group_id
        )
        return model_from_detailed(response)

    @api_method
    def _workflow_task_groups_page(
        self,
        ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        project_id: Optional[str] = None,
        mentioned_in: Optional[Iterable[str]] = None,
        watcher_ids: Optional[Iterable[str]] = None,
        execution_types: Optional[Iterable[str]] = None,
        responsible_team_ids: Optional[Iterable[str]] = None,
        status_ids_any_of: Optional[Iterable[str]] = None,
        status_ids_none_of: Optional[Iterable[str]] = None,
        status_ids_only: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        creator_ids: Optional[Iterable[str]] = None,
        modified_at: Optional[datetime.date] = None,
        display_ids: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[WorkflowTaskGroupsPaginatedList]:
        return list_workflow_task_groups.sync_detailed(  # type: ignore
            client=self.client,
            ids=none_as_unset(optional_array_query_param(ids)),
            schema_id=none_as_unset(schema_id),
            folder_id=none_as_unset(folder_id),
            project_id=none_as_unset(project_id),
            mentioned_in=none_as_unset(optional_array_query_param(mentioned_in)),
            watcher_ids=none_as_unset(optional_array_query_param(watcher_ids)),
            execution_types=none_as_unset(optional_array_query_param(execution_types)),
            responsible_team_ids=none_as_unset(optional_array_query_param(responsible_team_ids)),
            status_idsany_of=none_as_unset(optional_array_query_param(status_ids_any_of)),
            status_idsnone_of=none_as_unset(optional_array_query_param(status_ids_none_of)),
            status_idsonly=none_as_unset(optional_array_query_param(status_ids_only)),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            modified_at=none_as_unset(modified_at),
            display_ids=none_as_unset(optional_array_query_param(display_ids)),
            archive_reason=none_as_unset(archive_reason),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        project_id: Optional[str] = None,
        mentioned_in: Optional[Iterable[str]] = None,
        watcher_ids: Optional[Iterable[str]] = None,
        execution_types: Optional[Iterable[str]] = None,
        responsible_team_ids: Optional[Iterable[str]] = None,
        status_ids_any_of: Optional[Iterable[str]] = None,
        status_ids_none_of: Optional[Iterable[str]] = None,
        status_ids_only: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        creator_ids: Optional[Iterable[str]] = None,
        modified_at: Optional[datetime.date] = None,
        display_ids: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[WorkflowTaskGroup]:
        """
        List workflow task groups.

        See https://benchling.com/api/reference#/Workflow%20Task%20Groups/listWorkflowTaskGroups
        """

        def api_call(next_token: NextToken) -> Response[WorkflowTaskGroupsPaginatedList]:
            return self._workflow_task_groups_page(
                ids=ids,
                schema_id=schema_id,
                folder_id=folder_id,
                project_id=project_id,
                mentioned_in=mentioned_in,
                watcher_ids=watcher_ids,
                execution_types=execution_types,
                responsible_team_ids=responsible_team_ids,
                status_ids_any_of=status_ids_any_of,
                status_ids_none_of=status_ids_none_of,
                status_ids_only=status_ids_only,
                name=name,
                name_includes=name_includes,
                creator_ids=creator_ids,
                modified_at=modified_at,
                display_ids=display_ids,
                archive_reason=archive_reason,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: WorkflowTaskGroupsPaginatedList) -> Optional[List[WorkflowTaskGroup]]:
            return body.workflow_task_groups

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, workflow_task_group: WorkflowTaskGroupCreate) -> WorkflowTaskGroup:
        """
        Create a new workflow task group.

        If no name is specified, uses the workflow schema name and a unique incrementor
        separated by a single whitespace.

        See https://benchling.com/api/reference#/Workflow%20Task%20Groups/createWorkflowTaskGroup
        """
        response = create_workflow_task_group.sync_detailed(client=self.client, json_body=workflow_task_group)
        return model_from_detailed(response)

    @api_method
    def update(
        self, workflow_task_group_id: str, workflow_task_group: WorkflowTaskGroupUpdate
    ) -> WorkflowTaskGroup:
        """
        Update a workflow task group.

        See https://benchling.com/api/reference#/Workflow%20Task%20Groups/updateWorkflowTaskGroup
        """
        response = update_workflow_task_group.sync_detailed(
            client=self.client, workflow_task_group_id=workflow_task_group_id, json_body=workflow_task_group
        )
        return model_from_detailed(response)

    @api_method
    def archive(
        self, workflow_task_group_ids: Iterable[str], reason: WorkflowTaskGroupArchiveReason
    ) -> WorkflowTaskGroupsArchivalChange:
        """
        Archive one or more workflows.

        See https://benchling.com/api/reference#/Workflow%20Task%20Groups/archiveWorkflowTaskGroups
        """
        archive_request = WorkflowTaskGroupsArchive(
            reason=reason, workflow_task_group_ids=list(workflow_task_group_ids)
        )
        response = archive_workflow_task_groups.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, workflow_task_group_ids: Iterable[str]) -> WorkflowTaskGroupsArchivalChange:
        """
        Unarchive one or more workflows.

        See https://benchling.com/api/reference#/Workflow%20Task%20Groups/unarchiveWorkflowTaskGroups
        """
        unarchive_request = WorkflowTaskGroupsUnarchive(workflow_task_group_ids=list(workflow_task_group_ids))
        response = unarchive_workflow_task_groups.sync_detailed(
            client=self.client, json_body=unarchive_request
        )
        return model_from_detailed(response)
