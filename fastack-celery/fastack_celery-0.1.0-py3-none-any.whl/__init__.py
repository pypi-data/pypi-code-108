import asyncio
from typing import List, Type, Union

from asgi_lifespan import LifespanManager
from celery import Celery, Task
from celery.app.amqp import AMQP
from celery.app.control import Control
from celery.app.events import Events
from celery.app.log import Logging
from celery.app.registry import TaskRegistry
from celery.backends.base import Backend
from celery.loaders.base import BaseLoader
from fastack import Fastack
from fastack.context import _app_ctx_stack


def make_celery(
    app: Fastack,
    name: str = "main",
    *,
    loader: Union[str, BaseLoader] = None,
    backend: Union[str, Type[Backend]] = None,
    amqp: Union[str, Type[AMQP]] = None,
    events: Union[str, Type[Events]] = None,
    log: Union[str, Type[Logging]] = None,
    control: Union[str, Type[Control]] = None,
    set_as_current: bool = True,
    tasks: Union[str, Type[TaskRegistry]] = None,
    broker: str = None,
    include: List[str] = None,
    changes: dict = None,
    config_source: Union[str, object] = None,
    fixups: List[str] = None,
    autofinalize: bool = True,
    namespace: str = None,
    strict_typing: bool = True,
    **kwargs
) -> Celery:
    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            async def executor():
                token = None
                try:
                    async with LifespanManager(app):
                        token = _app_ctx_stack.set(app)
                        return self.run(*args, **kwargs)
                finally:
                    if token:
                        _app_ctx_stack.reset(token)

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()

            task = loop.create_task(executor())
            return loop.run_until_complete(task)

    celery = Celery(
        name,
        task_cls=ContextTask,
        loader=loader,
        backend=backend,
        amqp=amqp,
        events=events,
        log=log,
        control=control,
        set_as_current=set_as_current,
        tasks=tasks,
        broker=broker,
        include=include,
        changes=changes,
        config_source=config_source,
        fixups=fixups,
        autofinalize=autofinalize,
        namespace=namespace,
        strict_typing=strict_typing,
        **kwargs
    )
    celery.set_default()
    celery_conf = getattr(app.state.settings, "Celery", object())
    celery.config_from_object(celery_conf)
    celery.autodiscover_tasks(["app"], force=True)
    return celery
