# -*- coding: utf-8 -*-
import fnmatch
import weakref

import asyncio

import inspect
from google.protobuf.reflection import GeneratedProtocolMessageType
from pydantic.typing import ForwardRef, evaluate_forwardref

from patchwork.node.core.exceptions import TaskDrop

try:
    import betterproto
except:
    betterproto = None

from typing import Callable, Any, Dict, List

from patchwork.core import Task, AsyncSubscriber
from patchwork.node.core import dependencies


def get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


def get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


class Handler:

    def __init__(self, call):
        self.call = call
        sig = get_typed_signature(call)
        self.kwargs = {}

        for param_name, param in sig.parameters.items():
            if isinstance(param.default, dependencies.Dependency):
                self.kwargs[param_name] = param.default
                continue
            if param.annotation is Task:
                self.kwargs[param_name] = dependencies.GetTask()
                continue
            if isinstance(param.annotation, GeneratedProtocolMessageType):
                self.kwargs[param_name] = dependencies.GetPayload(param.annotation)
                continue
            if betterproto is not None and issubclass(param.annotation, betterproto.Message):
                self.kwargs[param_name] = dependencies.GetPayload(param.annotation, betterproto=True)
                continue

            raise NotImplementedError(f"{param_name} is not supported")

    def __call__(self, ctx: dependencies.Context):
        kwargs = {k: v.resolve(ctx) for k, v in self.kwargs.items()}
        return self.call(**kwargs)


class Route:

    def __init__(self, handler: Handler, path: str):
        self.handler = handler
        self.path = path

    def match(self, path):
        return fnmatch.fnmatch(path, self.path)

    def __call__(self, ctx: dependencies.Context):
        return self.handler(ctx)


class TaskRouter:

    def __init__(self, skip_unsupported_tasks: bool = False):
        """
        :param skip_unsupported_tasks: if True skips unsupported tasks instead of
        """
        self.routes: List[Route] = []
        self._worker = None
        self._skip_unsupported = skip_unsupported_tasks

    def bind(self, worker):
        self._worker = weakref.ref(worker)

    def on(self, *task_type: str):
        def decorator(fn):
            assert asyncio.iscoroutinefunction(fn), "Handler must be an async function"

            handler = Handler(fn)

            for tt in task_type:
                self.routes.append(Route(handler, tt))

            return fn
        return decorator

    def handle(self, task: Task, receiver: AsyncSubscriber):
        for route in self.routes:
            if route.match(task.task_type):
                ctx = dependencies.Context(self._worker(), task, receiver)
                return route(ctx)

        if self._skip_unsupported:
            raise TaskDrop()
