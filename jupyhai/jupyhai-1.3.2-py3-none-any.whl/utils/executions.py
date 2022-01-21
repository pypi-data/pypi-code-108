from typing import Union
from uuid import UUID

from valohai_cli.api import request

from jupyhai.api_urls import EXECUTIONS_URL


def get_execution_by_id(execution_id: Union[str, UUID]) -> dict:
    response = request('get', f'{EXECUTIONS_URL}{execution_id}/')
    if response.status_code == 404:
        raise ValueError(f"No such execution: {execution_id} - {response.text}")
    response.raise_for_status()
    return response.json()
