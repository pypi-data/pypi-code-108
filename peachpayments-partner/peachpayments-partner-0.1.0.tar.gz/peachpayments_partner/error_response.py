"""Format error response."""

from datetime import datetime, timezone
from typing import Optional, Union

from peachpayments_partner.result_codes import ResultCode

ParameterErrorType = dict[str, Optional[str]]
ParameterErrorsType = list[ParameterErrorType]
ErrorResultType = dict[str, Union[ParameterErrorsType, Optional[str]]]
ErrorResponseType = dict[str, Union[str, ErrorResultType]]
ValidateRequestReturnType = dict[
    str,
    Union[
        bool,
        list[str],
        ErrorResponseType,
    ],
]
ValidateResponseReturnType = dict[str, Union[bool, list[str], dict]]


def format_parameter_errors(errors: dict[str, list[str]] = None, data: dict = None) -> ParameterErrorsType:
    """Format parameter errors.

    Args:
        errors (dict): field as a key providing a list of messages
        data (dict): request data

    Returns:
        (list): parameter errors
    """
    errors = errors or {}
    data = data or {}
    parameter_errors: ParameterErrorsType = []
    for field in errors:
        for message in errors[field]:
            error: ParameterErrorType = dict(name=field, message=message)
            if field in data:
                error["value"] = data[field]
            parameter_errors.append(error)
    return parameter_errors


def format_error_response(
    code: ResultCode,
    errors: dict[str, list[str]] = None,
    data: dict = None,
) -> ErrorResponseType:
    r"""Format error response.

    Args:
        code (ResultCode): error code
        errors (dict): field as a key providing a list of messages
        data (dict): request data

    Returns:
        (dict): error response

    Example:
    ```
    {
      "result": {
          "code": "200.300.404",
          "parameterErrors": [
              {
                  "value": "10.0",
                  "name": "amount",
                  "message": "Must match ^[0-9]{1,8}(\\.[0-9]{2})?$"
              },
              {
                  "value": "ZA",
                  "name": "currency",
                  "message": "Must be a valid ISO-4217, 3-character currency."
              }
          ]
      },
      "timestamp": "2021-08-03T16:16:30.992618Z"
    }
    ```
    """
    errors = errors or {}
    data = data or {}

    result: ErrorResultType = dict(
        code=code.code,
    )
    parameter_errors: ParameterErrorsType = format_parameter_errors(errors, data)
    if parameter_errors:
        result["parameterErrors"] = parameter_errors

    response: ErrorResponseType = dict(
        result=result,
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )
    return response
