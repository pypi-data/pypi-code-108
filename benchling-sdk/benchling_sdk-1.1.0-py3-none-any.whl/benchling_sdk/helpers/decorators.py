from functools import wraps
import inspect
import logging
from typing import Any, Callable, cast, TypeVar

from benchling_sdk.helpers.logging_helpers import sdk_logger
from benchling_sdk.helpers.retry_helpers import retry_method

F = TypeVar("F", bound=Callable[..., Any])


def api_method(f: F) -> F:
    """Mark the decorated method as making one or more API calls to Benchling."""

    @wraps(f)
    @retry_method
    def wrapper(*args, **kwargs):
        _log_function(f, args, kwargs)
        return f(*args, **kwargs)

    return cast(F, wrapper)


def _log_function(func, args, kwargs) -> None:
    func_module = inspect.getmodule(func)
    module_name = "" if func_module is None else func_module.__name__
    sdk_logger.info("Calling %s in %s", func.__name__, module_name)
    if sdk_logger.isEnabledFor(logging.DEBUG):
        formatted_args = list(args)
        # The first value is a pointer to the service and object hash like
        # <benchling_sdk.services.schema.location_schema_service.LocationSchemaService object at 0x109c9a8e0>
        formatted_args.pop(0)
        sdk_logger.debug(
            "Calling %s in %s with arguments: %s keyword arguments: %s",
            func.__name__,  # Example: location_schemas_page
            module_name,  # Example: benchling_sdk.services.schema.location_schema_service
            formatted_args,  # Example: ["arg1", "arg2"]
            kwargs,  # Example: {"next_token": "", "page_size": 50}
        )
