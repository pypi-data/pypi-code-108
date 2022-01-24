"""
At least timeout implementation need to be reworked.
Encapsulation could be improved too.
"""
from __future__ import annotations

from inspect import _empty  # type: ignore[attr-defined]
from inspect import Parameter, signature
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    get_type_hints,
)

from loguru import logger

from .middlewares.broker import InjectBrokerMiddleware
from .middlewares.errors import ErrorHandlerMiddleware, catch_low_level_exceptions
from .middlewares.responses import ReplyMiddleware, ToResponseMiddleware, ensure_failure
from .middlewares.time.subscribe import x_process_time
from .middlewares.timeout import ensure_process_timeout
from .requests import Header, Headers, Reply, Request, Subject
from .validation import _check_optional, validate

if TYPE_CHECKING:  # pragma: no cover
    from .broker import Broker  # pragma: no cover


T = TypeVar("T")

Dispatch = Callable[..., Any]


def _get_dependency(
    param: Parameter,
    param_type: Type[T],
) -> Callable[[Request], Any]:
    """Retrieve a callable that can be used to get an argument value based on a given request."""
    default = param.default

    # Get single header from request
    if isinstance(default, Header):

        def get_header(request: Request) -> Any:
            value = default.get(request, param_type)
            return value

        return get_header

    # Get raw data from request
    if param_type is bytes:

        def get_raw_data(request: Request) -> bytes:
            data: bytes = request.data
            return data

        return get_raw_data

    # Get request from request
    elif param_type is Request:

        def get_request(request: Request) -> Request:
            return request

        return get_request

    # Get subject from request
    elif param_type is Subject:

        def get_subject(request: Request) -> Subject:
            return request.subject

        return get_subject

    # Get reply from request
    elif param_type is Reply:

        def get_reply(request: Request) -> Reply:
            return request.reply

        return get_reply

    # Get headers from request
    elif param_type is Headers:

        def get_headers(request: Request) -> Headers:
            return request.headers

        return get_headers

    # Get anything from request payload
    elif param_type != _empty:

        # Take a raw message and return parsed message data
        def get_data(request: Request) -> Any:
            return validate(param_type, request.data, default=param.default)

        return get_data

    # No annotation specified, we return the request
    def default_get_request(request: Request) -> Request:
        return request

    return default_get_request


def get_request_dependencies(
    handler: Callable[..., Any],
) -> Tuple[List[Callable[..., Any]], Dict[str, Callable[..., Any]]]:
    """Identify handlers arguments and return a dictionnary of keys
    and functions that can be used to fetch arguments from message"""
    # Create empty list of args
    args: List[Callable[..., Any]] = []
    # Create empty dict of kwargs
    kwargs: Dict[str, Callable[..., Any]] = {}
    # Gather type hints and parameters
    parameters = signature(handler).parameters.items()
    parameters_types = get_type_hints(handler)
    parameters_types.pop("return", None)
    # Iterate over the parameters
    for param_name, param in parameters:
        # Gather type and kind (I.E, positional only, positional or keyword, keyword only)
        positional_only = param.kind == param.POSITIONAL_ONLY
        param_type = parameters_types.get(param_name, param.annotation)
        # Check if type is an optional type and fetch real type in this case
        _, _param_type = _check_optional(param_type)
        # Get validator for this parameter
        func = _get_dependency(param, _param_type)
        # Append positional arguments
        if positional_only:
            args.append(func)
        # Append keyword arguments
        else:
            kwargs[param_name] = func
    # Return a list of functions and a dict of parameter names and functions
    return args, kwargs


def inject_request_dependencies(
    handler: Callable[..., Awaitable[T]],
    ignore: List[str] = [],
) -> Callable[[Request], Awaitable[T]]:
    """Create a new function based on given function signature"""
    args_v, kwargs_v = get_request_dependencies(handler)

    async def wrapped_handler(request: Request, *_args: Any, **_kwargs: Any) -> T:
        """Wrapped handler that will perform arguments injection (optionally with validation)"""
        nonlocal args_v
        nonlocal kwargs_v
        kwargs = {
            name: value(request)
            for name, value in kwargs_v.items()
            if name not in ignore
        }
        args = [value(request) for value in args_v]
        return await handler(*[*args, *_args], **{**kwargs, **_kwargs})

    return wrapped_handler


def chain_middleware(
    dispatch: Callable[..., Any],
    middleware: Callable[..., Any],
) -> Callable[..., Any]:
    async def cb(*args: Any, **kwargs: Any) -> Any:
        """Chain a coroutine middleware with given async function"""
        cancelled = True
        try:
            name = (
                getattr(middleware, "__name__", None) or middleware.__class__.__name__
            )
            logger.trace(f"Entering middleware {name}")
            result = await middleware(*args, **kwargs, dispatch=dispatch)
            cancelled = False
        finally:
            logger.trace(f"Exiting middleware {name} (cancelled={cancelled})")
        return result

    return cb


def chain_middlewares(
    function: Callable[..., Any], middlewares: List[Callable[..., Any]]
) -> Callable[..., Any]:
    """Take a function and a list of middlewares as arguments and return a single asynchronous coroutine"""

    # Take first middleware
    # Initializing dispatch function
    dispatch = function

    # Iterate over middlewares in reverse order
    for middleware in reversed(middlewares):
        dispatch = chain_middleware(dispatch, middleware)

    return dispatch


def get_subscribe_cb(
    cb: Callable[..., Awaitable[Any]],
    middlewares: Optional[List[Callable[..., Awaitable[Any]]]] = None,
    error_handlers: Dict[
        Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
    ] = {},
    broker: Optional[Broker] = None,
) -> Callable[..., Awaitable[Any]]:
    """Get a subscription callback"""
    # Make sure middlewares is of type list
    middlewares = middlewares or []
    # Inject dependencies into user callback
    wrapped_cb = inject_request_dependencies(cb)

    # Also perform dependency injection on the middlewares, but ignore "dispatch" argument
    if middlewares:
        # WARNING: Injecting dependencies following this pattern means that the argument MUST be called "dispatch"
        middlewares = [
            inject_request_dependencies(middleware, ignore=["dispatch"])
            for middleware in middlewares
        ]

    # Create the middleware stack
    middleware_stack: List[Callable[..., Awaitable[Any]]] = [
        # This is the first (and last) middleware to be executed
        # It's used to catch all exceptions that are not handled
        catch_low_level_exceptions,
        # Make sure a process timeout is enforced
        ensure_process_timeout,
        # User middlewares
        *middlewares,
        # Used to ensure that user error handlers are executed in case of exception
        # raise during message processing
        ErrorHandlerMiddleware(error_handlers),
    ]

    if broker:
        # Inject the broker into the request
        # This will be the first middleware to run
        middleware_stack.insert(0, InjectBrokerMiddleware(broker))

    # Chain the wrapped callback with the middleware stack
    return chain_middlewares(wrapped_cb, middleware_stack)


def get_subscribe_and_reply_cb(
    send: Callable[..., Awaitable[None]],
    cb: Callable[..., Awaitable[Any]],
    middlewares: Optional[List[Callable[..., Any]]] = None,
    status_code: Optional[int] = 200,
    details: Optional[str] = None,
    drop_headers: Iterable[str] = [],
    error_handlers: Dict[
        Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
    ] = {},
    broker: Optional[Broker] = None,
) -> Callable[..., Awaitable[Any]]:
    """Get a subscription callback which can reply."""
    # Make sure middlewares is a list
    middlewares = middlewares or []
    # First inject the request dependencies
    wrapped_cb = inject_request_dependencies(cb, ignore=[])

    if middlewares:
        # Also perform dependency injection on the middlewares, but ignore "dispatch" argument
        # WARNING: Injecting dependencies following this pattern means that the argument MUST be called "dispatch"
        middlewares = [
            inject_request_dependencies(middleware, ignore=["dispatch"])
            for middleware in middlewares
        ]
        middlewares.insert(
            0, ToResponseMiddleware(status_code=status_code, details=details)
        )

    # At this point we can define our middleware stack
    # NOTE: I don't know if using at least 7 coroutines to process a single message
    # might have a performance impact.
    # If that's the case, we will simply need to allow sync middlewares as well, so that
    # we do not waste time switching context.
    # I don't think it's critical at the moment
    middleware_stack: List[Callable[..., Awaitable[Any]]] = [
        # This is the first (and last) middleware to be executed
        # It's used to catch all exceptions that are not handled
        catch_low_level_exceptions,
        # Used to send a reply to the requester
        ReplyMiddleware(send=send, drop_headers=drop_headers),
        # Used to measure process time
        x_process_time,
        # Used to enforce a timeout on message processing
        ensure_process_timeout,
        # Used to transform any exception into a response
        ensure_failure,
        # User middlewares
        *middlewares,
        # Used to ensure that user middleware are called using a Response
        ToResponseMiddleware(status_code=status_code, details=details),
        # Used to ensure that user error handlers are executed in case of exception
        # raise during message processing
        ErrorHandlerMiddleware(error_handlers=error_handlers),
    ]

    if broker:
        # Inject the broker into the request
        # This will be the first middleware to run
        middleware_stack.insert(0, InjectBrokerMiddleware(broker))

    # Chain the wrapped callback and the middleware stack
    return chain_middlewares(wrapped_cb, middleware_stack)


__all__ = [
    "get_request_dependencies",
    "inject_request_dependencies",
    "chain_middleware",
    "chain_middlewares",
    "get_subscribe_cb",
    "get_subscribe_and_reply_cb",
]
