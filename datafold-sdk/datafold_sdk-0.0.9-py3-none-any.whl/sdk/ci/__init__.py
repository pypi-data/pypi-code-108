import logging
from typing import Optional, List

import pydantic

from datafold_sdk.sdk.utils import prepare_api_url, prepare_headers, get_data

logger = logging.getLogger(__file__)


class CiRunListOptions(pydantic.BaseModel):
    limit: int = 100
    offset: int = 0
    pr_sha: Optional[str]
    pr_num: Optional[str]


class CiRun(pydantic.BaseModel):
    id: int
    base_branch: str
    base_sha: str
    pr_branch: str
    pr_sha: str
    pr_num: str
    status: str


def list_runs(
        host: str,
        api_key: str,
        ci_config_id: int,
        pr_sha: Optional[str] = None,
        pr_num: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None) -> List[CiRun]:
    """
    List runs for specified CI config.

    Args:
        host          (str): The location of the datafold app server.
        api_key       (str): The API_KEY to use for authentication
        ci_config_id  (int): The ID of the CI config for which you submit these artefacts
                             (See the CI config ID in the CI settings screen).
        pr_sha        (str): Optionally filter by PR sha.
        pr_num        (int): Optionally filter by PR number.
        limit         (int): Optionally limit number of results (1..1000).
        offset        (int): Optionally list results starting from this index.
    Returns:
        None
    """

    api_segment = f"api/v1/ci/{ci_config_id}/runs"
    url = prepare_api_url(host, api_segment)
    headers = prepare_headers(api_key)
    params = {
        'limit': limit,
        'offset': offset,
        'pr_sha': pr_sha,
        'pr_num': pr_num,
    }
    params = {k: str(v) for k, v in params.items() if v is not None}

    results = get_data(url, params=params, headers=headers).json()
    return [CiRun(**record) for record in results]
