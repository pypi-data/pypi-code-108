import os

import backoff
import specd.sdk
from configparser import ConfigParser
from bravado.exception import HTTPInternalServerError
from urllib3.exceptions import TimeoutError
from aiohttp.client_exceptions import ClientConnectionError

from . import logger, models

# const

KMS_TOKEN = os.getenv("KMS_TOKEN")
KMS_HOST = os.getenv("KMS_HOST")
KMS_SCHEMES = os.getenv("KMS_SCHEMES")
KMS_SCHEMES = KMS_SCHEMES.split(",") if KMS_SCHEMES else None
DEFAULT_SPECD_PATH = os.path.join(os.path.dirname(__file__), "./specs/")
HTTP_EXCEPTIONS = (
    OSError,
    ConnectionError,
    TimeoutError,
    ClientConnectionError,
    # HTTPGatewayTimeout,
)
MAX_TIME = 600


# retrieve variables from environment (higher precedence) or .ini (lower)

CONFIG_SECTION = "gocli-options"
CONFIG_FILE_PATH = "~/.gocli.ini"

# ini

config = ConfigParser()
config.read(os.path.expanduser(CONFIG_FILE_PATH))


def construct_sdk(  # pragma: no mccabe
    targets=None,
    host=None,
    token=None,
    async_enabled=False,
    verify_ssl=False,
    loop=None,
    specd_path=None,
    schemes=None,
    enable_validation=False,
    config=None,
    max_time=MAX_TIME,
    max_tries=12,
    timeout=300,
    custom_header_option=None,
):

    token = token or KMS_TOKEN

    # add custom headers to the current headers var
    # creates a dict of key:val by iterating through
    # the tuple of custom_header_option and initializes
    # the dict by separating each element in the tuple
    # by ':'. ex. ('key1:val1','key2:val2') will be
    # {'key1':'val1','key2:'val2'}

    headers = dict(map(lambda x: x.split(':'), custom_header_option or []))
    if token:
        headers["Authorization"] = f"Token {token}"

    specd_path = specd_path or DEFAULT_SPECD_PATH

    config = config or {}

    # validating requests/responses causes problems for extra fields
    # when they cannot be supported by additionalProperties
    # (e.g. differing types in the same record: ao__int, sig__string)
    if not enable_validation:
        config.update(
            {
                "validate_responses": False,
                "validate_requests": False,
                "validate_swagger_spec": False,
            }
        )

    sdk = specd.sdk.create_sdk(
        specd_path,
        host=host or KMS_HOST,
        targets=targets,
        headers=headers,
        models=models,
        async_enabled=async_enabled,
        verify_ssl=verify_ssl,
        loop=loop,
        schemes=schemes or KMS_SCHEMES,
        config=config,
    )

    if async_enabled:

        @backoff.on_exception(
            backoff.expo,
            HTTP_EXCEPTIONS,
            max_time=max_time,
            max_tries=max_tries,
        )
        async def _async_with_retry(sdk_func, **kwargs):
            try:
                return handle_errors(
                    await sdk_func(**kwargs).result(timeout=timeout)
                )

            except HTTPInternalServerError as error:
                logger.get_logger().error(
                    "_async_with_retry",
                    sdk_func=sdk_func,
                    kwargs=kwargs,
                    error=error,
                )
                raise

        sdk.call_with_retry = _async_with_retry

    else:

        @backoff.on_exception(
            backoff.expo,
            HTTP_EXCEPTIONS,
            max_time=max_time,
            max_tries=max_tries,
        )
        def _sync_with_retry(sdk_func, **kwargs):
            try:
                return handle_errors(
                    sdk_func(**kwargs).result(timeout=timeout)
                )

            except HTTPInternalServerError as error:
                logger.get_logger().error(
                    "_sync_with_retry",
                    sdk_func=sdk_func,
                    kwargs=kwargs,
                    error=error,
                )
                raise

        sdk.call_with_retry = _sync_with_retry

    return sdk


def handle_errors(results):  # pragma: no mccabe
    try:
        errors = results.errors or []
    except Exception:
        errors = []

    for error in errors:
        if isinstance(error, list):
            error = error[0]
        if not error:
            continue
        err_msg = "no message provided."
        if "error_message" in error.keys():
            err_msg = error["error_message"]
        if "error_type" in error.keys():
            err_msg += " - " + error["error_type"]

        logger.get_logger().error("add_batch", error=err_msg)

    return results


def get_variable(variable_name: str):
    return os.getenv(
        f"KMS_{variable_name.upper()}",
        config.get(CONFIG_SECTION, variable_name, fallback=None),
    )
