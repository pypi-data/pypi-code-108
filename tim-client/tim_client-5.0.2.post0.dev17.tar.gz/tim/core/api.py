import json
import requests
from typing import Any, TypeVar, Union
from .credentials import Credentials
from .authentication import verify_credentials

T = TypeVar('T')


def execute_request(
    credentials: Credentials,
    method: str,
    path: str,
    body: Union[Any, None] = None,
    params: Union[Any, None] = None,
    file: Union[str, None] = None,
) -> Any:
  verified_credentials = verify_credentials(credentials)
  headers = {
      "Authorization": f"Bearer {verified_credentials.token}",
      "X-Tim-Client": verified_credentials.clientName,
  }

  upload_file = lambda: requests.request(
      method=method,
      url=f"{verified_credentials.endpoint}{path}",
      headers=headers,
      files={
          "configuration": json.dumps(body),
          "file": file,
      },
  )

  handle_request = lambda: requests.request(
      method=method,
      url=f"{verified_credentials.endpoint}{path}",
      json=body,
      params=params,
      headers=headers,
  )

  response = upload_file() if file else handle_request()

  if not response.ok:
    if response.status_code == 500:
      raise ValueError("Internal error. Please contact support.")

    raise ValueError(json.loads(response.text)["message"])

  if response.headers.get('content-type') == 'application/json':
    return response.json()

  return response.text
