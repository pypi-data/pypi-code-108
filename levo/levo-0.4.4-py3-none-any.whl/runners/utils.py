import json
from typing import Dict, List

import attr
from levo_commons.models import Request, Response, SerializedTestResult
from levo_commons.status import Status

from ..utils import SENSITIVE_HEADERS, mask_sensitive_headers


def _format_header_values(values: List[str]) -> str:
    return "\n".join(f"      - {json.dumps(v)}" for v in values)


def _format_headers(headers: Dict[str, List[str]]) -> str:
    return "\n".join(
        f"      {name}:\n{_format_header_values(values)}"
        for name, values in headers.items()
    )


def _format_request_body(request: Request) -> str:
    if request.body is not None:
        return f"""    body:
      encoding: 'utf-8'
      base64_string: '{request.body}'"""
    return ""


def _format_response_body(response: Response) -> str:
    if response.body is not None:
        return f"""    body:
      encoding: '{response.encoding}'
      base64_string: '{response.body}'"""
    return ""


def get_formatted_request_response(status, created_time, duration, request, response):
    # Construct a blob with all requests and responses from the interactions and
    # send them to SaaS.
    return f"""
- status: '{status}'
  duration: '{duration}'
  recorded_at: '{created_time}'

  request:
    uri: '{request.uri}'
    method: '{request.method}'
    headers:
{_format_headers(request.headers)}
{_format_request_body(request)}
  response:
    status:
      code: '{response.status_code}'
      message: {json.dumps(response.message)}
    headers:
{_format_headers(response.headers)}
{_format_response_body(response)}
    http_version: '{response.http_version}'
"""


def get_formatted_test_result(result: SerializedTestResult) -> str:
    for assertion in result.assertions.values():
        for interaction in assertion.interactions:
            interaction.request.headers = mask_sensitive_headers(
                interaction.request.headers, SENSITIVE_HEADERS
            )
            interaction.response.headers = mask_sensitive_headers(
                interaction.response.headers, SENSITIVE_HEADERS
            )
            interaction.curl_code = interaction.request.as_curl_command()
    for interaction in result.interactions.values():
        interaction.request.headers = mask_sensitive_headers(
            interaction.request.headers, SENSITIVE_HEADERS
        )
        interaction.response.headers = mask_sensitive_headers(
            interaction.response.headers, SENSITIVE_HEADERS
        )
        interaction.curl_code = interaction.request.as_curl_command()
    result = json.dumps(attr.asdict(result))
    return result


def get_color_for_status(status: Status) -> str:
    return (
        "green"
        if status == Status.success
        else "red"
        if status == Status.failure
        else "yellow"
    )
