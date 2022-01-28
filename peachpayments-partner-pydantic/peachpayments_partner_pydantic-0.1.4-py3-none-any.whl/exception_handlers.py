"""Translate pydantic error to Peach Payments error response."""

from datetime import datetime, timezone
from typing import Any

from peachpayments_partner.result_codes import result_codes

from peachpayments_partner_pydantic.outbound_schemas import ParameterError
from peachpayments_partner_pydantic.schemas import Error400Response


def _find_validated_data(loc: tuple, data: dict) -> tuple:
    """Find the validated data for the given location in the data.

    Args:
        loc: The location to find the validated data for. ie. ("body", "card", "cvv")
        data: The data to find the validated data for.

    Returns:
        A tuple containing the path to receive the data and the value of the field if present.
    """
    location = []

    # remove "__root__" from path
    for item in loc:
        if item != "__root__":
            location.append(item)

    # Remove "body" from path
    if location and location[0] == "body":
        location.pop(0)

    # Concatenate location values seperated by "/" to create a path string
    path: str = "/".join([str(i) for i in location])
    result: Any = data.copy()
    values: Any
    try:
        # Iterate through location tuple to find value of validated data field
        for index in location:
            values = result if isinstance(result, dict) or isinstance(result, list) else {}
            # Replace result with a nested dictionary or final value if it exists
            result = values[index]
    except (KeyError, IndexError):
        # Return only the path in case the field was not found or the index was out of range.
        return (path,)

    return (path, result)


def _get_message(error: dict[str, Any]) -> str:
    """Override the message to match Peach format.

    Args:
        error: The error dictionary containing the type and context("ctx").

    Returns:
        The message to be used in the response.
    """
    if "type" in error and error["type"] == "value_error.str.regex":
        return f"Must match {error['ctx']['pattern']}."

    return error["msg"].capitalize()


def exception_to_response(exc: Any) -> dict[str, Any]:
    """Create Error400Response from exception data.

    Args:
        exc: The exception object.

    Returns:
        A dict create from Error400Response containing the Error400Result.
    """
    data = exc.body
    errors = exc.errors()
    result_code = result_codes.INVALID_OR_MISSING_PARAMETER

    parameter_errors: list[ParameterError] = []
    for error in errors:
        validated_data: tuple = _find_validated_data(error["loc"], data)
        value = None
        # Set the parameter_error.value if value (validated_data[1]) is present.
        if len(validated_data) == 2:
            value = validated_data[1]

        parameter_errors.append(ParameterError(name=validated_data[0], message=_get_message(error), value=value))

    response = Error400Response(
        result={
            "code": result_code.code,
            "parameterErrors": parameter_errors,
        },
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    )

    response_dict = response.dict(exclude_unset=True)
    response_dict["timestamp"] = response_dict["timestamp"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return response_dict
