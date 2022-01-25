"""
Utility functions used by the object clerk
"""
import logging

from botocore.exceptions import ClientError

from object_clerk.exceptions import ObjectClerkException
from object_clerk.exceptions import ObjectClerkServerAuthException
from object_clerk.exceptions import ObjectClerkServerInternalException
from object_clerk.exceptions import ObjectNotFoundException


logger = logging.getLogger(__name__)


def client_exception_handler(e: ClientError, function_name: str, args: tuple, kwargs: dict):
    """
    Handle boto3 call exceptions to convert them into object clerk exceptions
    """
    error_detail = f"function={function_name}, args={args}, kwargs={kwargs}, detail={e.response}"
    logger.error(f"Error executing client function: {error_detail}")
    error_code = None
    if isinstance(e.response.get("Error"), dict):
        error_code = e.response["Error"].get("Code")
    if error_code in ["404", "NoSuchBucket", "NoSuchKey"]:
        raise ObjectNotFoundException(f"Object not found: detail={e.response}")
    if error_code in [
        "500",
        "503",
        "InternalError",
        "Busy",
        "ServiceUnavailable",
        "SlowDown",
    ]:
        raise ObjectClerkServerInternalException(
            f"Internal Server Error executing client function: {error_detail}"
        )
    if error_code in [
        "401",
        "403",
        "UnauthorizedAccess",
        "AccessDenied",
        "AccountProblem",
        "AllAccessDisabled",
        "CrossLocationLoggingProhibited",
        "InvalidAccessKeyId",
        "InvalidObjectState",
        "InvalidPayer",
        "InvalidSecurity",
        "NotSignedUp",
        "RequestTimeTooSkewed",
        "SignatureDoesNotMatch",
    ]:
        raise ObjectClerkServerAuthException(
            f"Authorization Error executing client function: {error_detail}"
        )
    raise ObjectClerkException(f"Error executing client function: {error_detail}")


def mutate_client_exceptions(client_func):
    """
    Decorator to wrap boto3 call functions to capture Client Exceptions
    and translate to object clerk exceptions
    :param client_func: boto3 client function to wrap
    :return: Output of boto3 client function
    """

    def call_client_func(*args, **kwargs):
        """
        Wrapper function for  boto3 client translating ClientError codes to exceptions
        https://docs.aws.amazon.com/AmazonS3/latest/API/ErrorResponses.html
        """
        try:
            return client_func(*args, **kwargs)
        except ClientError as e:
            client_exception_handler(
                e, function_name=client_func.__name__, args=args, kwargs=kwargs
            )

    return call_client_func
