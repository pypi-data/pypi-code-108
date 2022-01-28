import inspect
import threading
from functools import wraps
from typing import Optional

import pendulum
import pyspark
from typeguard import typechecked

from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.analytics import AnalyticsLogger
from tecton._internals.tecton_errors import TectonAPIInaccessibleError
from tecton._internals.tecton_errors import TectonAPIValidationError
from tecton.tecton_errors import TectonInternalError
from tecton.tecton_errors import TectonValidationError
from tecton_spark import errors as tecton_spark_errors
from tecton_spark import logger
from tecton_spark.id_helper import IdHelper

VERBOSE = True

analytics = AnalyticsLogger()
thread_local_data = threading.local()
sdk_public_method_decorator_enabled = True


def disable_sdk_public_method_decorator():
    global sdk_public_method_decorator_enabled
    sdk_public_method_decorator_enabled = False


def documented_by(func):
    """Normally you should just use functools.wraps over this, but wraps() doesn't work nicely
    when you try to wrap a classmethod in a normal func.
    """

    def wrapper(target):
        target.__doc__ = func.__doc__
        return target

    return wrapper


def sdk_public_method(func):
    arg_names = _get_arg_names(func)

    @wraps(func)
    def _sdk_public_method_wrapper(*args, **kwargs):
        if not sdk_public_method_decorator_enabled:
            return func(*args, **kwargs)

        if not hasattr(thread_local_data, "in_tecton_sdk_public_method_wrapper"):
            thread_local_data.in_tecton_sdk_public_method_wrapper = False

        already_in_wrapper = thread_local_data.in_tecton_sdk_public_method_wrapper
        if already_in_wrapper:
            return func(*args, **kwargs)

        try:
            thread_local_data.in_tecton_sdk_public_method_wrapper = True
            return _invoke_and_transform_errors(
                func, args, kwargs, arg_names, analytics is not None, not already_in_wrapper, typecheck=True
            )
        finally:
            thread_local_data.in_tecton_sdk_public_method_wrapper = already_in_wrapper

    return _sdk_public_method_wrapper


def _is_method(func):
    params = inspect.signature(func).parameters
    return "self" in params or "cls" in params


def _get_arg_names(func):
    arg_names = []
    for i, param in enumerate(inspect.signature(func).parameters.values()):
        name = param.name
        if i == 0 and _is_method(func):
            continue
        arg_names.append(name)
    return arg_names


def _invoke_and_transform_errors(
    func, args, kwargs, arg_names, log_analytics: bool, is_top_level: bool, typecheck: bool = False
):
    original_exception: Optional[Exception] = None
    exception_to_throw: Optional[BaseException] = None
    return_value = None
    start_time = pendulum.now("UTC")

    if typecheck:
        func = typechecked(func)

    if _is_method(func):
        method_object = args[0]
        method_args = args[1:]
    else:
        method_object = None
        method_args = args

    trace_id = IdHelper.generate_string_id()

    if log_analytics:
        analytics.log_method_entry(trace_id, method_object, func, method_args, kwargs, arg_names)

    metadata_service.set_trace_id(trace_id)

    try:
        return_value = func(*args, **kwargs)
    except TectonValidationError as e:
        original_exception = e
        exception_to_throw = e
    except tecton_spark_errors.TectonValidationError as e:
        original_exception = e
        exception_to_throw = e
    except tecton_spark_errors.AccessError as e:
        original_exception = e
        exception_to_throw = e
    except TectonAPIValidationError as e:
        original_exception = e
        exception_to_throw = errors.VALIDATION_ERROR_FROM_MDS(str(e), trace_id)
    except TectonAPIInaccessibleError as e:
        original_exception = e
        exception_to_throw = errors.MDS_INACCESSIBLE(metadata_service._get_host_port())
    except TectonInternalError as e:
        original_exception = e
        exception_to_throw = e
    except Exception as e:
        original_exception = e
        # Skip wrapping some error types that are useful for debugging
        # Top level TypeError is thrown on missing required arguments to the public methods
        # pyspark.sql.utils.CapturedException wraps bunch of Spark errors parsing SQL and building plan:
        # https://github.com/apache/spark/blob/master/python/pyspark/sql/utils.py
        # and is useful for debugging SQL statements
        if (
            logger.get_logging_level() < logger.DEFAULT_LOGGING_LEVEL
            or (isinstance(e, TypeError) and is_top_level)
            or isinstance(e, pyspark.sql.utils.CapturedException)
            or isinstance(e, pendulum.parsing.exceptions.ParserError)
            or isinstance(e, PermissionError)
        ):
            exception_to_throw = e
        else:
            exception_to_throw = errors.INTERNAL_ERROR(str(e))
    finally:
        metadata_service.set_trace_id(None)

    end_time = pendulum.now("UTC")
    execution_time = end_time - start_time

    if log_analytics:
        analytics.log_method_return(trace_id, method_object, func, return_value, execution_time, original_exception)

    if exception_to_throw:
        if not VERBOSE and logger.get_logging_level() >= logger.DEFAULT_LOGGING_LEVEL:
            exception_to_throw = exception_to_throw.with_traceback(None)
            raise exception_to_throw
        else:
            raise exception_to_throw from original_exception

    return return_value
