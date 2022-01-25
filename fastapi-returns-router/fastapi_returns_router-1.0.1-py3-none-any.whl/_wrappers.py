# fastapi_returns/_async_wrapper.py
# Ian Kollipara
# 2022.01.19
#
# Async Wrapper to handle Return transformations

# Imports
from fastapi import HTTPException, status
from inspect import signature, _empty
from typing import Any, Callable, List
from returns import future, io, result, maybe
from functools import wraps


def future_wrapper(endpoint_func: Callable[..., future.Future[Any]]):
    @wraps(endpoint_func)
    async def wrapper(*args, **kwargs):
        return (await endpoint_func(*args, **kwargs).awaitable())._inner_value
    return wrapper

def future_result_wrapper(endpoint_func: Callable[..., future.FutureResult[Any, Any]]):
    @wraps(endpoint_func)
    async def wrapper(*args, **kwargs):
        res = await endpoint_func(*args, **kwargs).awaitable()
        match res:
            case io.IOSuccess(result.Success(val)):
                return val
            case io.IOFailure(result.Failure(val)):
                if isinstance(val, Exception):
                    raise val
                return val
    return wrapper

def result_wrapper(endpoint_func: Callable[..., result.Result[Any, Any]]):
    @wraps(endpoint_func)
    def wrapper(*args, **kwargs):
        res = endpoint_func(*args, **kwargs)
        match res:
            case result.Success(val):
                return val
            case result.Failure(val):
                if isinstance(val, Exception):
                    raise val
                return val
    return wrapper

def io_result_wrapper(endpoint_func: Callable[..., io.IOResult[Any, Any]]):
    @wraps(endpoint_func)
    def wrapper(*args, **kwargs):
        res = endpoint_func(*args, **kwargs)
        match res:
            case io.IOSuccess(result.Success(val)):
                return val
            case io.IOFailure(result.Failure(val)):
                if isinstance(val, Exception):
                    raise val
                return val
    return wrapper

def io_wrapper(endpoint_func: Callable[..., io.IO[Any]]):
    @wraps(endpoint_func)
    def wrapper(*args, **kwargs):
        return endpoint_func(*args, **kwargs)._inner_value
    return wrapper

def maybe_wrapper(endpoint_func: Callable[..., maybe.Maybe[Any]]):
    @wraps(endpoint_func)
    def wrapper(*args, **kwargs):
        res = endpoint_func(*args, **kwargs)
        match res:
            case maybe.Some(val):
                return val
            case maybe.Nothing:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper

def make_container_jsonable(endpoint_func: Callable):
    """Turn a function that returns a container to a normal function.
    
    This wrapper function provides a return return's container types
    in a fastapi route handler, and have the data return successfully.
    Currently the function does not handle custom containers or
    RequiresContext. 
    """

    return_type_list: List[type] = signature(endpoint_func).return_annotation.mro()
    if return_type_list == future.Future.mro():
        return future_wrapper(endpoint_func)
    elif return_type_list == future.FutureResult.mro():
        return future_result_wrapper(endpoint_func)
    elif return_type_list == io.IO.mro():
        return io_wrapper(endpoint_func)
    elif return_type_list == io.IOResult.mro():
        return io_result_wrapper(endpoint_func)
    elif return_type_list == result.Result.mro():
        return result_wrapper(endpoint_func)
    elif return_type_list == maybe.Maybe.mro():
        return maybe_wrapper(endpoint_func)
    elif _empty in return_type_list:
        raise ValueError(f"No return argument provided for {endpoint_func.__name__}")
    else:
        return endpoint_func