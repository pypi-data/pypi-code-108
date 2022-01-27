# Copyright (c) Qotto, 2021

"""
Celery integration utilities

Utility functions to integrate the eventy protocol in celery apps

You need to install celery optional dependencies ("pip install eventy[celery]")
"""

import logging
from contextvars import copy_context
from functools import wraps
from logging import LogRecord
from typing import Callable, List, Dict, Any, Optional

import celery as vendor_celery
import celery.app.base as vendor_celery_app_base
from celery import shared_task as celery_shared_task
from celery.execute import send_task as celery_send_task
from celery.result import AsyncResult

import eventy.config.celery
from eventy.trace_id import correlation_id_var, request_id_var
from eventy.trace_id.generator import gen_trace_id

logger = logging.getLogger(__name__)

__all__ = [
    'send_task',
    'shared_task',
    'Celery',
]


def _shorten_celery_task_id(celery_task_id: Optional[str]) -> Optional[str]:
    task_id_len = 10
    if celery_task_id and len(celery_task_id) > task_id_len:
        return celery_task_id[-task_id_len:-1]
    else:
        return None


def _provide_request_id(record: LogRecord) -> bool:
    """
    Add a field request_id in the log record using celery task_id.
    """
    try:
        celery_task_id: str = record.data['id']  # type:ignore
        record.request_id = _shorten_celery_task_id(celery_task_id)  # type:ignore
    except Exception:
        pass
    return True


class Celery(vendor_celery_app_base.Celery):
    """
    Modified implementation of Celery class to provide logs with trace ids.
    """

    def __init__(self, *args, **kwargs):
        logging.getLogger('celery.worker.strategy').addFilter(_provide_request_id)
        logging.getLogger('celery.app.trace').addFilter(_provide_request_id)
        super().__init__(*args, **kwargs)
        self.conf.update(worker_hijack_root_logger=False)

    def config_from_envvar(self, *args, **kwargs):
        result = super().config_from_envvar(*args, **kwargs)
        self.conf.update(worker_hijack_root_logger=False)
        return result

    def config_from_cmdline(self, *args, **kwargs):
        result = super().config_from_cmdline(*args, **kwargs)
        self.conf.update(worker_hijack_root_logger=False)
        return result

    def config_from_object(self, *args, **kwargs):
        result = super().config_from_object(*args, **kwargs)
        self.conf.update(worker_hijack_root_logger=False)
        return result


class AsyncResultWithAutoForgetOnGet(AsyncResult):
    """
    Modified implementation of AsyncResult class to auto-forget celery tasks.
    """

    def get(self, *args, **kwargs):
        result = super().get(*args, **kwargs)
        self.forget()
        return result


def send_task(name: str, args: List = None, kwargs: Dict = None, **options) -> AsyncResult:
    """
    Modified version of celery.execute.send_task adding context in task kwargs

    options ar propagated as celery send_task named arguments and keyword arguments

    if CELERY_AUTO_FORGET_ON_GET is True, and no custom `result_cls` is provided the task is forgotten after get()

    Usage::

        from eventy.integration.celery import send_task

        send_task(
            'service.task.name', [],
            {
                'param': 'value',
            }
        )

    If a correlation_id is defined in the current context, it is equivalent to::

        from celery.execute import send_task
        from eventy.trace_id import correlation_id_var

        send_task(
            'service.task.name', [],
            {
                'correlation_id': correlation_id_var.get(),
                'param': 'value',
            }
        )
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    if eventy.config.celery.CELERY_AUTO_FORGET_ON_GET and 'result_cls' not in options:
        logger.debug(f"Will auto-forget celery task {name}.")
        options['result_cls'] = AsyncResultWithAutoForgetOnGet

    if correlation_id_var.get():
        kwargs.update(correlation_id=correlation_id_var.get())

    return celery_send_task(name, args, kwargs, **options)


def shared_task(_func: Callable = None, **kwargs) -> Callable:
    """
    Modified version of celery.shared_task adding traces in the task keyword arguments

    ``correlation_id`` is fetched from context, or generated. ``request_id`` is always generated

    Usage::

        from eventy.integration.celery import shared_task

    Instead of::

        from celery import shared_task

    And then::

        @shared_task(options...)
        def my_task(param):
            ...


    :param _func: if used as a decorator with no args, decorated function will be first arg
    :param kwargs: options are propagated to celery's shared_task
    :return: new version of shared_task
    """

    def _shared_task_decorator(func: Callable) -> Callable:
        def _run_and_extract_trace_id(*func_args, **func_kwargs) -> Any:
            if 'correlation_id' in func_kwargs:
                correlation_id_var.set(func_kwargs.pop('correlation_id'))
            else:
                correlation_id_var.set(gen_trace_id(func))
            try:
                request_id = _shorten_celery_task_id(vendor_celery.current_task.request.id)
            except Exception:
                request_id = None
            request_id_var.set(request_id or gen_trace_id(func))
            return func(*func_args, **func_kwargs)

        @wraps(func)
        def _run_inside_context(*func_args, **func_kwargs) -> Any:
            context = copy_context()
            return context.run(_run_and_extract_trace_id, *func_args, **func_kwargs)

        return celery_shared_task(**kwargs)(_run_inside_context)  # type: ignore

    if _func:
        return _shared_task_decorator(_func)
    else:
        return _shared_task_decorator
