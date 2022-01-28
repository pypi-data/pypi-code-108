import datetime
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    execution_types: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    status_idsany_of: Union[Unset, str] = UNSET,
    status_idsnone_of: Union[Unset, str] = UNSET,
    status_idsonly: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/workflow-task-groups".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_modified_at: Union[Unset, str] = UNSET
    if not isinstance(modified_at, Unset):
        json_modified_at = modified_at.isoformat()

    params: Dict[str, Any] = {}
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(schema_id, Unset) and schema_id is not None:
        params["schemaId"] = schema_id
    if not isinstance(folder_id, Unset) and folder_id is not None:
        params["folderId"] = folder_id
    if not isinstance(project_id, Unset) and project_id is not None:
        params["projectId"] = project_id
    if not isinstance(mentioned_in, Unset) and mentioned_in is not None:
        params["mentionedIn"] = mentioned_in
    if not isinstance(watcher_ids, Unset) and watcher_ids is not None:
        params["watcherIds"] = watcher_ids
    if not isinstance(execution_types, Unset) and execution_types is not None:
        params["executionTypes"] = execution_types
    if not isinstance(responsible_team_ids, Unset) and responsible_team_ids is not None:
        params["responsibleTeamIds"] = responsible_team_ids
    if (
        not isinstance(flowchart_workflow_task_group_ids, Unset)
        and flowchart_workflow_task_group_ids is not None
    ):
        params["flowchartWorkflowTaskGroupIds"] = flowchart_workflow_task_group_ids
    if not isinstance(status_idsany_of, Unset) and status_idsany_of is not None:
        params["statusIds.anyOf"] = status_idsany_of
    if not isinstance(status_idsnone_of, Unset) and status_idsnone_of is not None:
        params["statusIds.noneOf"] = status_idsnone_of
    if not isinstance(status_idsonly, Unset) and status_idsonly is not None:
        params["statusIds.only"] = status_idsonly
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
    schema_id: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    execution_types: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    status_idsany_of: Union[Unset, str] = UNSET,
    status_idsnone_of: Union[Unset, str] = UNSET,
    status_idsonly: Union[Unset, str] = UNSET,
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
        schema_id=schema_id,
        folder_id=folder_id,
        project_id=project_id,
        mentioned_in=mentioned_in,
        watcher_ids=watcher_ids,
        execution_types=execution_types,
        responsible_team_ids=responsible_team_ids,
        flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
        status_idsany_of=status_idsany_of,
        status_idsnone_of=status_idsnone_of,
        status_idsonly=status_idsonly,
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
    schema_id: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    execution_types: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    status_idsany_of: Union[Unset, str] = UNSET,
    status_idsnone_of: Union[Unset, str] = UNSET,
    status_idsonly: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Optional[BadRequestError]:
    """ List workflow task groups """

    return sync_detailed(
        client=client,
        ids=ids,
        schema_id=schema_id,
        folder_id=folder_id,
        project_id=project_id,
        mentioned_in=mentioned_in,
        watcher_ids=watcher_ids,
        execution_types=execution_types,
        responsible_team_ids=responsible_team_ids,
        flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
        status_idsany_of=status_idsany_of,
        status_idsnone_of=status_idsnone_of,
        status_idsonly=status_idsonly,
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
    schema_id: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    execution_types: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    status_idsany_of: Union[Unset, str] = UNSET,
    status_idsnone_of: Union[Unset, str] = UNSET,
    status_idsonly: Union[Unset, str] = UNSET,
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
        schema_id=schema_id,
        folder_id=folder_id,
        project_id=project_id,
        mentioned_in=mentioned_in,
        watcher_ids=watcher_ids,
        execution_types=execution_types,
        responsible_team_ids=responsible_team_ids,
        flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
        status_idsany_of=status_idsany_of,
        status_idsnone_of=status_idsnone_of,
        status_idsonly=status_idsonly,
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
    schema_id: Union[Unset, str] = UNSET,
    folder_id: Union[Unset, str] = UNSET,
    project_id: Union[Unset, str] = UNSET,
    mentioned_in: Union[Unset, str] = UNSET,
    watcher_ids: Union[Unset, str] = UNSET,
    execution_types: Union[Unset, str] = UNSET,
    responsible_team_ids: Union[Unset, str] = UNSET,
    flowchart_workflow_task_group_ids: Union[Unset, str] = UNSET,
    status_idsany_of: Union[Unset, str] = UNSET,
    status_idsnone_of: Union[Unset, str] = UNSET,
    status_idsonly: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, datetime.date] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    display_ids: Union[Unset, str] = UNSET,
    archive_reason: Union[Unset, str] = UNSET,
) -> Optional[BadRequestError]:
    """ List workflow task groups """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            schema_id=schema_id,
            folder_id=folder_id,
            project_id=project_id,
            mentioned_in=mentioned_in,
            watcher_ids=watcher_ids,
            execution_types=execution_types,
            responsible_team_ids=responsible_team_ids,
            flowchart_workflow_task_group_ids=flowchart_workflow_task_group_ids,
            status_idsany_of=status_idsany_of,
            status_idsnone_of=status_idsnone_of,
            status_idsonly=status_idsonly,
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
