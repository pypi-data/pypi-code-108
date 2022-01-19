from __future__ import annotations

import asyncio
import contextlib
import itertools
import logging
from argparse import ArgumentParser
from asyncio.events import AbstractEventLoop
from dataclasses import dataclass, replace
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)

from aiorun import run

from ..common import (
    ASYNC_NOOP,
    ASYNC_VOID,
    IS_DICT,
    IS_ITERABLE,
    ProxyDictionary,
    findvalue,
    format_help,
)
from ..execution import SimpleExecutor
from ..services import DependencyInjection, Scoped, Scoping
from .parser import Parser

if TYPE_CHECKING:
    from concurrent.futures import Executor


ScopedNext = Callable[[], Awaitable[Optional[Scoped]]]


@dataclass
class Context:
    """
    Context for applying middleware.

    Attributes
    ------

    executor: An instance of [Executor](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor).
    Tasks can be submitted to this executor for async and parallel execution.
    next: Current execution chain. This is usually the `apply` of next middleware.
    scoped: The execution scope for this middleware. Should be returned
    as middleware's application result.
    """

    executor: Executor
    scoped: Scoped
    next: ScopedNext = ASYNC_NOOP

    @classmethod
    def new(cls, executor: Executor) -> Tuple[Context, Scoping]:
        """
        Create a new middleware context from a executor.

        Scoped is created from a newly created Scoping.
        """
        scoping = Scoping()
        return (
            cls(
                executor=executor, scoped=scoping.create_scoped(parent_scope=scoping.global_scope)
            ),
            scoping,
        )

    def prepare(self, _callable: Callable[..., Any]) -> Callable[..., Any]:
        provider = ProxyDictionary(self.scoped, _scoped_=self.scoped)
        return DependencyInjection.prepare(_callable, provider)

    async def submit(self, _callable: Callable[..., Any]) -> Any:
        prepared_action = self.prepare(_callable)
        result = await self.executor.submit(prepared_action)

        if isinstance(result, Scoping):
            self.scoped.update(result)
        return result

    def update_scoped(self, scoped: Optional[Scoped]) -> Scoped:
        """
        Update with another scoped. Updated scoped will be returned.
        """
        if scoped is not None:
            self.scoped.update(scoped)
        return self.scoped

    def replace_with_void_next(self) -> Context:
        """
        Use a no-op function to replace current context's next
        function and return the new context.

        Current context will not be modified.
        """
        return replace(self, next=ASYNC_VOID)


APPLY_INTO = "apply_into"
APPLY_ONTO = "apply_onto"
APPLY_METHOD = Union[APPLY_INTO, APPLY_ONTO]


class AbstractMiddleware:
    """
    A middleware should specify how it modifies the execution chain
    through the `apply` method.

    Events
    ------
    `before_apply`: emitted before applying the middleware to execution.
    Will receive this middleware and middleware context as argument
    `after_apply`: emitted after applying the middleware. Will receive the
    this middleware, middleware context, and `apply` invocation result,
    which should be the modified scope.
    """

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.lower()

    async def _do_apply(self, context: Context) -> Scoped:
        """
        Apply this middleware onto the execution chain.

        Should be overridden in subclasses to provide functionality.

        Returns
        ------
        Modified scope.

        * Return of modified scope is necessary in parallel execution scenario to
        * ensure the updates is captured.
        """
        return context.scoped

    async def apply_into(self, context: Context) -> Scoped:
        """
        Apply this middleware onto the execution chain.

        Can be overridden in subclasses to provide some common code around middleware application.

        Parameters
        ------
        executor:
        next: Current execution chain. This is usually the result of `apply` of next middleware.
        """
        scoped = await self._do_apply(context)
        return context.update_scoped(scoped)

    async def apply_onto(self, context: Context) -> Scoped:
        """
        Different from `apply` where middleware is committing the change to the scope,
        `apply_to` will add a scope to the existing scope in the context and make changes to it.

        Return
        ------
        The modified scope will be returned.
        """
        new_context = replace(context, scoped=context.scoped.create_scoped())
        return await self.apply_into(new_context)

    async def apply(self, context: Context, apply_method: APPLY_METHOD = APPLY_INTO) -> Scoped:
        """
        Use `apply_method` to select a way to apply this middleware
        in context.
        """
        apply = getattr(self, apply_method)
        return await apply(context)

    async def run(self, executor: Optional[Executor] = None, **kwargs: Any) -> Scoped:
        """
        Run current middleware in an executor.

        Parameters
        ------
        executor
        If executor is not specified, then a  `SimpledExecutor` will be used.
        kwargs
        Provided arguments will be used to initialize global scope.

        Return
        ------
        The execution scoping tree.
        """
        if executor is None:
            executor = SimpleExecutor()

        context, scoping = Context.new(executor)
        for name, value in kwargs.items():
            scoping.global_scope[name] = value

        scoped = await self.apply_onto(context)

        scoping.update(scoped)
        return scoped

    async def __run_and_stop(self, executor: Optional[Executor] = None, **kwargs: Any) -> None:
        await self.run(executor, **kwargs)
        asyncio.get_running_loop().stop()

    def run_as_main(self, executor: Optional[Executor] = None, **kwargs: Any) -> None:
        """
        Await completion of middleware in provided executor. This method can be
        used as main method.

        Differences from `self.run`
        ------
        + `run_as_main` will block main thread until the middleware has finished.
        + the execution scope will not be returned.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.__run_and_stop(executor, **kwargs))

        def handler(loop: AbstractEventLoop, context: Mapping[str, Any]) -> None:
            try:
                raise Exception("Premature termination") from context["exception"]
            except Exception:
                logging.exception(context["message"])
                loop.stop()

        loop.set_exception_handler(handler)

        return run(loop=loop)


class Middleware(Parser, AbstractMiddleware):
    @classmethod
    def of(cls, value: Any, name: Optional[str] = None) -> AbstractMiddleware:
        if name is None:
            name = cls.get_name()

        if IS_DICT(value) and len(value) == 1 and name in value:
            config = value
        else:
            config = {name: value}
        return cls(config)

    def format_help(
        self, argument_parser: Optional[Union[ArgumentParser, Dict[str, Any]]] = None
    ) -> str:
        from .action import Argparse

        if argument_parser is None:
            argument_parser = dict()

        arguments = map(
            Argparse.to_argument_definition,
            findvalue(self.declaration, Argparse.is_variant),
        )

        return format_help(argument_parser, arguments)


@dataclass
class _BoundMiddleware:
    middleware: Middleware
    context: Context

    async def apply_into(self) -> Scoped:
        return await self.middleware.apply_into(self.context)

    async def apply_onto(self) -> Scoped:
        return await self.middleware.apply_onto(self.context)


class Middlewares:
    """
    A queue of middleware.
    """

    middlewares: List[Middleware]

    @classmethod
    def apply_middlewares_into(
        cls, context: Context, middlewares: Iterable[Middleware]
    ) -> ScopedNext:
        """
        Create a coroutine function where each middleware will be applied in order.
        """
        return cls.apply_middlewares(context, middlewares, apply_methods=APPLY_INTO)

    @classmethod
    def apply_middlewares_onto(
        cls, context: Context, middlewares: Iterable[Middleware]
    ) -> ScopedNext:
        """
        Create a coroutine function where each middleware will be applied in order.

        Different from `apply`, the middlewares will be applied in new scope
        instead of existing scope.
        """
        return cls.apply_middlewares(context, middlewares, apply_methods=APPLY_ONTO)

    @classmethod
    def apply_middlewares(
        cls,
        context: Context,
        middlewares: Iterable[Middleware],
        apply_methods: Union[APPLY_METHOD, Iterable[APPLY_METHOD]],
    ) -> ScopedNext:
        if IS_ITERABLE(middlewares):
            middlewares = iter(middlewares)

        if isinstance(apply_methods, str):
            apply_methods = itertools.repeat(apply_methods)

        return cls._apply_middlewares(context, middlewares, apply_methods)

    @classmethod
    def _apply_middlewares(
        cls,
        context: Context,
        middlewares: Iterator[Middleware],
        apply_methods: Iterator[APPLY_METHOD],
    ) -> ScopedNext:
        try:
            middleware = next(middlewares)
            apply_method = next(apply_methods)

            context_next = cls._apply_middlewares(context, middlewares, apply_methods)

            middleware_context = replace(context, next=context_next)
            bound_middleware = _BoundMiddleware(middleware, middleware_context)

            return getattr(bound_middleware, apply_method)
        except StopIteration:
            return context.next

    def __init__(self) -> None:
        super().__init__()
        self.middlewares = []

    def get_middleware_by_type(self, middleware_type: Type[Middleware]) -> Middleware:
        """
        Get middleware by its type.
        """
        for middleware in self.middlewares:
            if isinstance(middleware, middleware_type):
                return middleware
        raise TypeError(f"No midleware has the specified type {middleware_type}")

    def get_middlewares_by_type(
        self, middleware_types: Iterable[Type[Middleware]]
    ) -> Iterable[Middleware]:
        """
        Get middlewares specified by their types.

        Existing middlewares will be yielded.
        """
        for middleware_type in middleware_types:
            with contextlib.suppress(TypeError):
                yield self.get_middleware_by_type(middleware_type)

    def apply_into(self, context: Context) -> ScopedNext:
        """
        Transform the registered middlewares to a coroutine function.
        """
        return self.apply_middlewares_into(context, self.middlewares)

    def apply_onto(self, context: Context) -> ScopedNext:
        """
        Transform the registered middlewares to a coroutine function.

        Different from `apply`, the middlewares will be applied in separate scope.
        """
        return self.apply_middlewares_onto(context, self.middlewares)

    def apply(
        self, context: Context, apply_methods: Union[APPLY_METHOD, Iterable[APPLY_METHOD]]
    ) -> ScopedNext:
        """
        Transform the registered middlewares to a coroutine function.

        Each middleware will be applied in the method specified in
        `apply_methods`.
        """
        return self.apply_middlewares(context, self.middlewares, apply_methods)


class WithMiddlewares(Middlewares):
    """
    A derived class of Middlewares that supports initialization of middlewares
    through their types.

    To use `WithMiddlewares`, derived class should implement `_init_middleware_types`
    with desired middleware types. Then call `create_middlewares_from` at appropriate place
    to initialize `self.middlewares`.
    """

    middleware_types: List[Type[Middleware]]
    middleware_apply_methods: List[APPLY_METHOD]

    @property
    def apply_methods(self) -> Iterable[APPLY_METHOD]:
        """
        Get apply methods for registered middlewares.
        """
        try:
            middleware_apply_methods = self.middleware_apply_methods
        except AttributeError:
            middleware_apply_methods = APPLY_INTO

        if isinstance(middleware_apply_methods, str):
            yield from itertools.repeat(middleware_apply_methods)
        else:
            try:
                middleware_iter = iter(self.middlewares)
                middleware = next(middleware_iter)
                for middleware_type, middleware_apply_method in zip(
                    self.middleware_types, middleware_apply_methods
                ):
                    if isinstance(middleware, middleware_type):
                        yield middleware_apply_method
                        middleware = next(middleware_iter)
            except StopIteration:
                return

    def __init__(self) -> None:
        super().__init__()
        self._init_middleware_types()
        self._init_middleware_apply_methods()

    def _init_middleware_types(self) -> None:
        self.middleware_types = []

    def _init_middleware_apply_methods(self) -> None:
        self.middleware_apply_methods = []

    def get_middleware_names(self) -> Iterable[str]:
        for middleware_type in self.middleware_types:
            yield middleware_type.get_name()

    def create_middlewares_from(self, value: Dict[str, Any]) -> Iterable[Middleware]:
        """
        Create middlewares using `value` if `value` is a dictionary and contains
        the middleware name.

        This assumes middleware config is keyed under middleware name.
        """
        for middleware_type, middleware_name in zip(
            self.middleware_types, self.get_middleware_names()
        ):
            if middleware_name in value:
                yield middleware_type(value)

    def apply(self, context: Context) -> ScopedNext:
        return super().apply(context, self.apply_methods)
