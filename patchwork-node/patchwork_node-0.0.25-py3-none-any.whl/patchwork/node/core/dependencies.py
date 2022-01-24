# -*- coding: utf-8 -*-
from typing import Any, Mapping

from patchwork import core
from patchwork.core.utils import cached_property


class Context:
    def __init__(self, worker: 'PatchworkWorker', task: core.Task, receiver: core.AsyncSubscriber):
        self.worker = worker
        self.task = task
        self.receiver = receiver

    @cached_property
    def publishers(self) -> Mapping[str, core.AsyncPublisher]:
        return self.worker.publishers

    @property
    def payload(self):
        return self.task.payload


class Dependency:

    def resolve(self, ctx):
        raise NotImplementedError()


class Depends(Dependency):

    def __init__(self, call):
        self.call = call

    def resolve(self, ctx):
        return self.call()


class GetPublisher(Dependency):

    def resolve(self, ctx: Context):
        return ctx.worker.get_publisher()


class GetPayload(Dependency):
    def __init__(self, schema: Any, betterproto=False):
        self.schema = schema
        self.betterproto = betterproto

    def resolve(self, ctx):
        obj = self.schema()
        if self.betterproto:
            obj.parse(ctx.payload.value)
        else:
            ctx.payload.Unpack(obj)
        return obj


class GetTask(Dependency):

    def resolve(self, ctx: Context):
        return ctx.task
