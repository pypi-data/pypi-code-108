import datetime
from typing import Any, Dict, Iterable, List, Optional, Union

from benchling_api_client.api.workflow_tasks import (
    archive_workflow_tasks,
    bulk_copy_workflow_tasks,
    bulk_create_workflow_tasks,
    bulk_update_workflow_tasks,
    copy_workflow_task,
    create_workflow_task,
    get_workflow_task,
    list_workflow_tasks,
    unarchive_workflow_tasks,
    update_workflow_task,
)
from benchling_api_client.extensions import UnknownType
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import (
    none_as_unset,
    optional_array_query_param,
    schema_fields_query_param,
)
from benchling_sdk.models import (
    AsyncTaskLink,
    ListWorkflowTasksScheduledOn,
    WorkflowTask,
    WorkflowTaskArchiveReason,
    WorkflowTaskBulkCreate,
    WorkflowTaskBulkUpdate,
    WorkflowTaskCreate,
    WorkflowTasksArchivalChange,
    WorkflowTasksArchive,
    WorkflowTasksBulkCopyRequest,
    WorkflowTasksBulkCreateRequest,
    WorkflowTasksBulkUpdateRequest,
    WorkflowTasksPaginatedList,
    WorkflowTasksUnarchive,
    WorkflowTaskUpdate,
)
from benchling_sdk.services.base_service import BaseService


class WorkflowTaskService(BaseService):
    """
    Workflow Tasks.

    Workflow tasks encapsulate a single unit of work.

    See https://benchling.com/api/reference#/Workflow%20Tasks
    """

    @api_method
    def get_by_id(self, workflow_task_id: str) -> WorkflowTask:
        """
        Get a workflow task.

        See https://benchling.com/api/reference#/Workflow%20Tasks/getWorkflowTask
        """
        response = get_workflow_task.sync_detailed(client=self.client, workflow_task_id=workflow_task_id)
        return model_from_detailed(response)

    @api_method
    def _workflow_tasks_page(
        self,
        ids: Optional[Iterable[str]] = None,
        workflow_task_group_ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        status_ids: Optional[Iterable[str]] = None,
        assignee_ids: Optional[Iterable[str]] = None,
        watcher_ids: Optional[Iterable[str]] = None,
        responsible_team_ids: Optional[Iterable[str]] = None,
        execution_origin_ids: Optional[Iterable[str]] = None,
        execution_types: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        creator_ids: Optional[Iterable[str]] = None,
        scheduled_on: Union[None, ListWorkflowTasksScheduledOn, datetime.date, UnknownType] = None,
        scheduled_on_lt: Optional[datetime.date] = None,
        scheduled_on_lte: Optional[datetime.date] = None,
        scheduled_on_gte: Optional[datetime.date] = None,
        scheduled_on_gt: Optional[datetime.date] = None,
        modified_at: Optional[datetime.date] = None,
        display_ids: Optional[Iterable[str]] = None,
        linked_item_ids_any_of: Optional[Iterable[str]] = None,
        linked_item_ids_all_of: Optional[Iterable[str]] = None,
        linked_item_ids_none_of: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[WorkflowTasksPaginatedList]:
        return list_workflow_tasks.sync_detailed(  # type: ignore
            client=self.client,
            ids=none_as_unset(optional_array_query_param(ids)),
            workflow_task_group_ids=none_as_unset(optional_array_query_param(workflow_task_group_ids)),
            schema_id=none_as_unset(schema_id),
            status_ids=none_as_unset(optional_array_query_param(status_ids)),
            assignee_ids=none_as_unset(optional_array_query_param(assignee_ids)),
            watcher_ids=none_as_unset(optional_array_query_param(watcher_ids)),
            responsible_team_ids=none_as_unset(optional_array_query_param(responsible_team_ids)),
            execution_origin_ids=none_as_unset(optional_array_query_param(execution_origin_ids)),
            execution_types=none_as_unset(optional_array_query_param(execution_types)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
            scheduled_on=none_as_unset(scheduled_on),
            scheduled_onlt=none_as_unset(scheduled_on_lt),
            scheduled_onlte=none_as_unset(scheduled_on_lte),
            scheduled_ongte=none_as_unset(scheduled_on_gte),
            scheduled_ongt=none_as_unset(scheduled_on_gt),
            modified_at=none_as_unset(modified_at),
            display_ids=none_as_unset(optional_array_query_param(display_ids)),
            linked_item_idsany_of=none_as_unset(optional_array_query_param(linked_item_ids_any_of)),
            linked_item_idsall_of=none_as_unset(optional_array_query_param(linked_item_ids_all_of)),
            linked_item_idsnone_of=none_as_unset(optional_array_query_param(linked_item_ids_none_of)),
            archive_reason=none_as_unset(archive_reason),
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
        )

    def list(
        self,
        ids: Optional[Iterable[str]] = None,
        workflow_task_group_ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        status_ids: Optional[Iterable[str]] = None,
        assignee_ids: Optional[Iterable[str]] = None,
        watcher_ids: Optional[Iterable[str]] = None,
        responsible_team_ids: Optional[Iterable[str]] = None,
        execution_origin_ids: Optional[Iterable[str]] = None,
        execution_types: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        creator_ids: Optional[Iterable[str]] = None,
        scheduled_on: Union[None, ListWorkflowTasksScheduledOn, datetime.date, UnknownType] = None,
        scheduled_on_lt: Optional[datetime.date] = None,
        scheduled_on_lte: Optional[datetime.date] = None,
        scheduled_on_gte: Optional[datetime.date] = None,
        scheduled_on_gt: Optional[datetime.date] = None,
        modified_at: Optional[datetime.date] = None,
        display_ids: Optional[Iterable[str]] = None,
        linked_item_ids_any_of: Optional[Iterable[str]] = None,
        linked_item_ids_all_of: Optional[Iterable[str]] = None,
        linked_item_ids_none_of: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[WorkflowTask]:
        """
        List workflow tasks.

        See https://benchling.com/api/reference#/Workflow%20Tasks/listWorkflowTasks
        """

        def api_call(next_token: NextToken) -> Response[WorkflowTasksPaginatedList]:
            return self._workflow_tasks_page(
                ids=ids,
                workflow_task_group_ids=workflow_task_group_ids,
                schema_id=schema_id,
                status_ids=status_ids,
                assignee_ids=assignee_ids,
                watcher_ids=watcher_ids,
                responsible_team_ids=responsible_team_ids,
                execution_origin_ids=execution_origin_ids,
                execution_types=execution_types,
                schema_fields=schema_fields,
                name=name,
                name_includes=name_includes,
                creator_ids=creator_ids,
                scheduled_on=scheduled_on,
                scheduled_on_lt=scheduled_on_lt,
                scheduled_on_lte=scheduled_on_lte,
                scheduled_on_gte=scheduled_on_gte,
                scheduled_on_gt=scheduled_on_gt,
                modified_at=modified_at,
                display_ids=display_ids,
                linked_item_ids_any_of=linked_item_ids_any_of,
                linked_item_ids_all_of=linked_item_ids_all_of,
                linked_item_ids_none_of=linked_item_ids_none_of,
                archive_reason=archive_reason,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: WorkflowTasksPaginatedList) -> Optional[List[WorkflowTask]]:
            return body.workflow_tasks

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, workflow_task: WorkflowTaskCreate) -> WorkflowTask:
        """
        Create a new workflow task.

        See https://benchling.com/api/reference#/Workflow%20Tasks/createWorkflowTask
        """
        response = create_workflow_task.sync_detailed(client=self.client, json_body=workflow_task)
        return model_from_detailed(response)

    @api_method
    def update(self, workflow_task_id: str, workflow_task: WorkflowTaskUpdate) -> WorkflowTask:
        """
        Update a workflow task.

        See https://benchling.com/api/reference#/Workflow%20Tasks/updateWorkflowTask
        """
        response = update_workflow_task.sync_detailed(
            client=self.client, workflow_task_id=workflow_task_id, json_body=workflow_task
        )
        return model_from_detailed(response)

    @api_method
    def copy(self, workflow_task_id: str) -> WorkflowTask:
        """
        Copy workflow task.

        Creates a new workflow task with the same fields and assignee as the provided task and creates
        a relationship between the two tasks.

        See https://benchling.com/api/reference#/Workflow%20Tasks/copyWorkflowTask
        """
        response = copy_workflow_task.sync_detailed(
            client=self.client,
            workflow_task_id=workflow_task_id,
        )
        return model_from_detailed(response)

    @api_method
    def archive(
        self, workflow_task_ids: Iterable[str], reason: WorkflowTaskArchiveReason
    ) -> WorkflowTasksArchivalChange:
        """
        Archive one or more workflow tasks.

        See https://benchling.com/api/reference#/Workflow%20Tasks/archiveWorkflowTasks
        """
        archive_request = WorkflowTasksArchive(reason=reason, workflow_task_ids=list(workflow_task_ids))
        response = archive_workflow_tasks.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, workflow_task_ids: Iterable[str]) -> WorkflowTasksArchivalChange:
        """
        Unarchive one or more workflow tasks.

        See https://benchling.com/api/reference#/Workflow%20Tasks/unarchiveWorkflowTasks
        """
        unarchive_request = WorkflowTasksUnarchive(workflow_task_ids=list(workflow_task_ids))
        response = unarchive_workflow_tasks.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_create(self, workflow_tasks: Iterable[WorkflowTaskBulkCreate]) -> AsyncTaskLink:
        """
        Create one or more workflow tasks.

        See https://benchling.com/api/reference#/Workflow%20Tasks/bulkCreateWorkflowTasks
        """
        body = WorkflowTasksBulkCreateRequest(list(workflow_tasks))
        response = bulk_create_workflow_tasks.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def bulk_update(self, workflow_tasks: Iterable[WorkflowTaskBulkUpdate]) -> AsyncTaskLink:
        """
        Update one or more workflow tasks.

        See https://benchling.com/api/reference#/Workflow%20Tasks/bulkUpdateWorkflowTasks
        """
        body = WorkflowTasksBulkUpdateRequest(list(workflow_tasks))
        response = bulk_update_workflow_tasks.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def bulk_copy(self, workflow_task_ids: Iterable[str]) -> AsyncTaskLink:
        """
        Bulk copy workflow tasks.

        Bulk creates new workflow tasks where each new task has the same fields and assignee as one of
        the provided tasks and creates a relationship between the provided task and its copy

        See https://benchling.com/api/reference#/Workflow%20Tasks/bulkCopyWorkflowTasks
        """
        body = WorkflowTasksBulkCopyRequest(list(workflow_task_ids))
        response = bulk_copy_workflow_tasks.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
