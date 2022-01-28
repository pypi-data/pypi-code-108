import datetime
from typing import Any, Dict, Iterable, List, Optional

from benchling_api_client.api.workflow_outputs import (
    archive_workflow_outputs,
    bulk_create_workflow_outputs,
    bulk_update_workflow_outputs,
    create_workflow_output,
    get_workflow_output,
    list_workflow_outputs,
    unarchive_workflow_outputs,
    update_workflow_output,
)
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
    WorkflowOutput,
    WorkflowOutputArchiveReason,
    WorkflowOutputBulkCreate,
    WorkflowOutputBulkUpdate,
    WorkflowOutputCreate,
    WorkflowOutputsArchivalChange,
    WorkflowOutputsArchive,
    WorkflowOutputsBulkCreateRequest,
    WorkflowOutputsBulkUpdateRequest,
    WorkflowOutputsPaginatedList,
    WorkflowOutputsUnarchive,
    WorkflowOutputUpdate,
)
from benchling_sdk.services.base_service import BaseService


class WorkflowOutputService(BaseService):
    """
    Workflow Outputs.

    Workflow outputs are outputs of a workflow task.

    See https://benchling.com/api/reference#/Workflow%20Outputs
    """

    @api_method
    def get_by_id(self, workflow_output_id: str) -> WorkflowOutput:
        """
        Get a workflow output.

        See https://benchling.com/api/reference#/Workflow%20Outputs/getWorkflowOutput
        """
        response = get_workflow_output.sync_detailed(
            client=self.client, workflow_output_id=workflow_output_id
        )
        return model_from_detailed(response)

    @api_method
    def _workflow_outputs_page(
        self,
        ids: Optional[Iterable[str]] = None,
        workflow_task_group_ids: Optional[Iterable[str]] = None,
        workflow_task_ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        watcher_ids: Optional[Iterable[str]] = None,
        responsible_team_ids: Optional[Iterable[str]] = None,
        creation_origin_ids: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        creator_ids: Optional[Iterable[str]] = None,
        modified_at: Optional[datetime.date] = None,
        display_ids: Optional[Iterable[str]] = None,
        linked_item_ids_any_of: Optional[Iterable[str]] = None,
        linked_item_ids_all_of: Optional[Iterable[str]] = None,
        linked_item_ids_none_of: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[WorkflowOutputsPaginatedList]:
        return list_workflow_outputs.sync_detailed(  # type: ignore
            client=self.client,
            ids=none_as_unset(optional_array_query_param(ids)),
            workflow_task_group_ids=none_as_unset(optional_array_query_param(workflow_task_group_ids)),
            workflow_task_ids=none_as_unset(optional_array_query_param(workflow_task_ids)),
            schema_id=none_as_unset(schema_id),
            watcher_ids=none_as_unset(optional_array_query_param(watcher_ids)),
            responsible_team_ids=none_as_unset(optional_array_query_param(responsible_team_ids)),
            creation_origin_ids=none_as_unset(optional_array_query_param(creation_origin_ids)),
            schema_fields=none_as_unset(schema_fields_query_param(schema_fields)),
            name=none_as_unset(name),
            name_includes=none_as_unset(name_includes),
            creator_ids=none_as_unset(optional_array_query_param(creator_ids)),
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
        workflow_task_ids: Optional[Iterable[str]] = None,
        schema_id: Optional[str] = None,
        watcher_ids: Optional[Iterable[str]] = None,
        responsible_team_ids: Optional[Iterable[str]] = None,
        creation_origin_ids: Optional[Iterable[str]] = None,
        schema_fields: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        creator_ids: Optional[Iterable[str]] = None,
        modified_at: Optional[datetime.date] = None,
        display_ids: Optional[Iterable[str]] = None,
        linked_item_ids_any_of: Optional[Iterable[str]] = None,
        linked_item_ids_all_of: Optional[Iterable[str]] = None,
        linked_item_ids_none_of: Optional[Iterable[str]] = None,
        archive_reason: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[WorkflowOutput]:
        """
        List workflow outputs.

        See https://benchling.com/api/reference#/Workflow%20Outputs/listWorkflowOutputs
        """

        def api_call(next_token: NextToken) -> Response[WorkflowOutputsPaginatedList]:
            return self._workflow_outputs_page(
                ids=ids,
                workflow_task_group_ids=workflow_task_group_ids,
                workflow_task_ids=workflow_task_ids,
                schema_id=schema_id,
                watcher_ids=watcher_ids,
                responsible_team_ids=responsible_team_ids,
                creation_origin_ids=creation_origin_ids,
                schema_fields=schema_fields,
                name=name,
                name_includes=name_includes,
                creator_ids=creator_ids,
                modified_at=modified_at,
                display_ids=display_ids,
                linked_item_ids_any_of=linked_item_ids_any_of,
                linked_item_ids_all_of=linked_item_ids_all_of,
                linked_item_ids_none_of=linked_item_ids_none_of,
                archive_reason=archive_reason,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: WorkflowOutputsPaginatedList) -> Optional[List[WorkflowOutput]]:
            return body.workflow_outputs

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, workflow_output: WorkflowOutputCreate) -> WorkflowOutput:
        """
        Create a new workflow output.

        See https://benchling.com/api/reference#/Workflow%20Outputs/createWorkflowOutput
        """
        response = create_workflow_output.sync_detailed(client=self.client, json_body=workflow_output)
        return model_from_detailed(response)

    @api_method
    def update(self, workflow_output_id: str, workflow_output: WorkflowOutputUpdate) -> WorkflowOutput:
        """
        Update a workflow output.

        See https://benchling.com/api/reference#/Workflow%20Outputs/updateWorkflowOutput
        """
        response = update_workflow_output.sync_detailed(
            client=self.client, workflow_output_id=workflow_output_id, json_body=workflow_output
        )
        return model_from_detailed(response)

    @api_method
    def archive(
        self, workflow_output_ids: Iterable[str], reason: WorkflowOutputArchiveReason
    ) -> WorkflowOutputsArchivalChange:
        """
        Archive one or more workflow outputs.

        See https://benchling.com/api/reference#/Workflow%20Outputs/archiveWorkflowOutputs
        """
        archive_request = WorkflowOutputsArchive(reason=reason, workflow_output_ids=list(workflow_output_ids))
        response = archive_workflow_outputs.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, workflow_output_ids: Iterable[str]) -> WorkflowOutputsArchivalChange:
        """
        Unarchive one or more workflow outputs.

        See https://benchling.com/api/reference#/Workflow%20Outputs/unarchiveWorkflowOutputs
        """
        unarchive_request = WorkflowOutputsUnarchive(workflow_output_ids=list(workflow_output_ids))
        response = unarchive_workflow_outputs.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_create(self, workflow_outputs: Iterable[WorkflowOutputBulkCreate]) -> AsyncTaskLink:
        """
        Create one or more workflow outputs.

        See https://benchling.com/api/reference#/Workflow%20Outputs/bulkCreateWorkflowOutputs
        """
        body = WorkflowOutputsBulkCreateRequest(list(workflow_outputs))
        response = bulk_create_workflow_outputs.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def bulk_update(self, workflow_outputs: Iterable[WorkflowOutputBulkUpdate]) -> AsyncTaskLink:
        """
        Update one or more workflow outputs.

        See https://benchling.com/api/reference#/Workflow%20Outputs/bulkUpdateWorkflowOutputs
        """
        body = WorkflowOutputsBulkUpdateRequest(list(workflow_outputs))
        response = bulk_update_workflow_outputs.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
