from typing import Optional, Union, Dict, List

import requests
from racetrack_client.log.context_error import ContextError


def parse_response(response: requests.Response, error_context: str) -> Optional[Union[Dict, List]]:
    """
    Ensure response was successful. If not, try to extract error message from it.
    :return: response parsed as JSON object

    This function handles all of these following cases:
    - if request went fine, return parsed JSON object,
    - if request went fine, but response is empty (eg. 204 status after DELETing), return None
    - if request went fine, but there was eg. JSON parsing error,
     raise "LC-API deploying error: Json is invalid in character 5"
    - if request completely failed with empty response (eg. due to Kubernilla issues),
    raise "LC-API deploying error: 404 Client Error: Not found for url http://localhost/blahblah"
    - if request failed gracefully from other RT component returning {"error": "you have no power here"},
    raise "LC-API deploying error: 500 Internal Server Error: you have no power here"
    """
    try:
        if 'application/json' in response.headers['content-type']:
            result = response.json()
        else:
            result = None

        if response.ok:
            return result

        if result is not None and 'error' in result:
            raise RuntimeError(f'{response.status_code} {response.reason}: {result.get("error")}')
        response.raise_for_status()
        return result
    except Exception as e:
        raise ResponseError(error_context, response.status_code) from e


class ResponseError(ContextError):
    def __init__(self, error_context: str, status_code: int):
        super().__init__(error_context)
        self.status_code = status_code
