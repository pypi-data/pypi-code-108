"""Methods for invoking AWS Lambda functions."""

from typing import Union

from sym.sdk.errors import SymIntegrationErrorEnum


class AWSLambdaError(SymIntegrationErrorEnum):
    UNKNOWN_ERROR = "An unexpected error occurred with AWS Lambda."
    FUNCTION_ERROR = "A error occurred during function execution: {msg}"


def invoke(arn: str, payload: dict = {}) -> Union[dict, str]:
    """
    Synchronously invokes an AWS Lambda function.
    If the results can be parsed as a JSON object, a dict is returned. Otherwise, the result is returned as a string.

    Args:
        arn: The ARN of the Lambda function to invoke.
        payload: A dict of JSON-serializable data to pass to the function.
    """


def invoke_async(arn: str, payload: dict = {}) -> bool:
    """
    Asynchronously invokes an AWS Lambda function.
    Note that this method simply returns a boolean indicating success enqueuing the invocation.

    Args:
        arn: The ARN of the Lambda function to invoke.
        payload: A dict of JSON-serializable data to pass to the function.
    """
