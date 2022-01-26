import datetime
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.schema_fields_query_param import SchemaFieldsQueryParam
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    workflow_task_group_ids: Union[Unset, str] = UNSET,
    workflow_task_ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    creation_origin_ids: Union[Unset, str] = UNSET,
    linked_item_idsany_of: Union[Unset, str] = UNSET,
    linked_item_idsall_of: Union[Unset, str] = UNSET,
    linked_item_idsnone_of: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/workflow-outputs".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_schema_fields: Union[Unset, Dict[str, Any]] = UNSET
    if not isinstance(schema_fields, Unset):
        json_schema_fields = schema_fields.to_dict()

    json_modified_at: Union[Unset, str] = UNSET
    if not isinstance(modified_at, Unset):
        json_modified_at = modified_at.isoformat()

    params: Dict[str, Any] = {}
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(workflow_task_group_ids, Unset) and workflow_task_group_ids is not None:
        params["workflowTaskGroupIds"] = workflow_task_group_ids
    if not isinstance(workflow_task_ids, Unset) and workflow_task_ids is not None:
        params["workflowTaskIds"] = workflow_task_ids
    if not isinstance(schema_id, Unset) and schema_id is not None:
        params["schemaId"] = schema_id
    if not isinstance(watcher_ids, Unset) and watcher_ids is not None:
        params["watcherIds"] = watcher_ids
    if not isinstance(responsible_team_ids, Unset) and responsible_team_ids is not None:
        params["responsibleTeamIds"] = responsible_team_ids
    if (
        not isinstance(flowchart_workflow_task_group_ids, Unset)
        and flowchart_workflow_task_group_ids is not None
    ):
        params["flowchartWorkflowTaskGroupIds"] = flowchart_workflow_task_group_ids
    if not isinstance(creation_origin_ids, Unset) and creation_origin_ids is not None:
        params["creationOriginIds"] = creation_origin_ids
    if not isinstance(linked_item_idsany_of, Unset) and linked_item_idsany_of is not None:
        params["linkedItemIds.anyOf"] = linked_item_idsany_of
    if not isinstance(linked_item_idsall_of, Unset) and linked_item_idsall_of is not None:
        params["linkedItemIds.allOf"] = linked_item_idsall_of
    if not isinstance(linked_item_idsnone_of, Unset) and linked_item_idsnone_of is not None:
        params["linkedItemIds.noneOf"] = linked_item_idsnone_of
    if not isinstance(json_schema_fields, Unset) and json_schema_fields is not None:
        params.update(json_schema_fields)
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name
    if not isinstance(name_includes, Unset) and name_includes is not None:
        params["nameIncludes"] = name_includes
    if not isinstance(creator_ids, Unset) and creator_ids is not None:
        params["creatorIds"] = creator_ids
    if not isinstance(json_modified_at, Unset) and json_modified_at is not None:
        params["modifiedAt"] = json_modified_at
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(display_ids, Unset) and display_ids is not None:
        params["displayIds"] = display_ids
    if not isinstance(archive_reason, Unset) and archive_reason is not None:
        params["archiveReason"] = archive_reason

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[BadRequestError]:
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[BadRequestError]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    workflow_task_group_ids: Union[Unset, str] = UNSET,
    workflow_task_ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    creation_origin_ids: Union[Unset, str] = UNSET,
    linked_item_idsany_of: Union[Unset, str] = UNSET,
    linked_item_idsall_of: Union[Unset, str] = UNSET,
    linked_item_idsnone_of: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Response[BadRequestError]:
    kwargs = _get_kwargs(
        client=client,
        ids=ids,
        workflow_task_group_ids=workflow_task_group_ids,
        workflow_task_ids=workflow_task_ids,
        schema_id=schema_id,
        watcher_ids=watcher_ids,
        responsible_team_ids=responsible_team_ids,
        flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
        creation_origin_ids=creation_origin_ids,
        linked_item_idsany_of=linked_item_idsany_of,
        linked_item_idsall_of=linked_item_idsall_of,
        linked_item_idsnone_of=linked_item_idsnone_of,
        schema_fields=schema_fields,
        name=name,
        name_includes=name_includes,
        creator_ids=creator_ids,
        modified_at=modified_at,
        next_token=next_token,
        page_size=page_size,
        display_ids=display_ids,
        archive_reason=archive_reason,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    workflow_task_group_ids: Union[Unset, str] = UNSET,
    workflow_task_ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    creation_origin_ids: Union[Unset, str] = UNSET,
    linked_item_idsany_of: Union[Unset, str] = UNSET,
    linked_item_idsall_of: Union[Unset, str] = UNSET,
    linked_item_idsnone_of: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Optional[BadRequestError]:
    """ List workflow outputs """

    return sync_detailed(
        client=client,
        ids=ids,
        workflow_task_group_ids=workflow_task_group_ids,
        workflow_task_ids=workflow_task_ids,
        schema_id=schema_id,
        watcher_ids=watcher_ids,
        responsible_team_ids=responsible_team_ids,
        flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
        creation_origin_ids=creation_origin_ids,
        linked_item_idsany_of=linked_item_idsany_of,
        linked_item_idsall_of=linked_item_idsall_of,
        linked_item_idsnone_of=linked_item_idsnone_of,
        schema_fields=schema_fields,
        name=name,
        name_includes=name_includes,
        creator_ids=creator_ids,
        modified_at=modified_at,
        next_token=next_token,
        page_size=page_size,
        display_ids=display_ids,
        archive_reason=archive_reason,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    workflow_task_group_ids: Union[Unset, str] = UNSET,
    workflow_task_ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    creation_origin_ids: Union[Unset, str] = UNSET,
    linked_item_idsany_of: Union[Unset, str] = UNSET,
    linked_item_idsall_of: Union[Unset, str] = UNSET,
    linked_item_idsnone_of: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Response[BadRequestError]:
    kwargs = _get_kwargs(
        client=client,
        ids=ids,
        workflow_task_group_ids=workflow_task_group_ids,
        workflow_task_ids=workflow_task_ids,
        schema_id=schema_id,
        watcher_ids=watcher_ids,
        responsible_team_ids=responsible_team_ids,
        flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
        creation_origin_ids=creation_origin_ids,
        linked_item_idsany_of=linked_item_idsany_of,
        linked_item_idsall_of=linked_item_idsall_of,
        linked_item_idsnone_of=linked_item_idsnone_of,
        schema_fields=schema_fields,
        name=name,
        name_includes=name_includes,
        creator_ids=creator_ids,
        modified_at=modified_at,
        next_token=next_token,
        page_size=page_size,
        display_ids=display_ids,
        archive_reason=archive_reason,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    workflow_task_group_ids: Union[Unset, str] = UNSET,
    workflow_task_ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    creation_origin_ids: Union[Unset, str] = UNSET,
    linked_item_idsany_of: Union[Unset, str] = UNSET,
    linked_item_idsall_of: Union[Unset, str] = UNSET,
    linked_item_idsnone_of: Union[Unset, str] = UNSET,
    schema_fields: Union[Unset, SchemaFieldsQueryParam] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Optional[BadRequestError]:
    """ List workflow outputs """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            workflow_task_group_ids=workflow_task_group_ids,
            workflow_task_ids=workflow_task_ids,
            schema_id=schema_id,
            watcher_ids=watcher_ids,
            responsible_team_ids=responsible_team_ids,
            flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
            creation_origin_ids=creation_origin_ids,
            linked_item_idsany_of=linked_item_idsany_of,
            linked_item_idsall_of=linked_item_idsall_of,
            linked_item_idsnone_of=linked_item_idsnone_of,
            schema_fields=schema_fields,
            name=name,
            name_includes=name_includes,
            creator_ids=creator_ids,
            modified_at=modified_at,
            next_token=next_token,
            page_size=page_size,
            display_ids=display_ids,
            archive_reason=archive_reason,
        )
    ).parsed
