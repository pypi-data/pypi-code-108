from tim.core.credentials import Credentials
from tim.core.api import execute_request
from .types import WorkspaceListPayload, Workspace
from typing import List, Union


def get_workspaces(
    credentials: Credentials,
    offset: int,
    limit: int,
    user_group_id: Union[str, None] = None,
    sort: Union[str, None] = None
) -> List[Workspace]:
  payload = WorkspaceListPayload(offset=offset, limit=limit)
  if user_group_id: payload['userGroupId'] = user_group_id
  if sort: payload['sort'] = sort

  return execute_request(credentials=credentials, method='get', path=f'/workspaces', params=payload)
