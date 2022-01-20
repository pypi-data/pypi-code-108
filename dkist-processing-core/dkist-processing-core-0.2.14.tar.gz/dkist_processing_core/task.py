"""
This module provides the base class that is used to wrap the various DAG task methods. It
provides support for user-defined setup and cleanup, task monitoring using Elastic APM,
standardized logging and exception handling.
"""
import json
import logging
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from contextlib import contextmanager
from os import environ
from typing import Optional

import elasticapm


__all__ = ["TaskBase"]

logger = logging.getLogger(__name__)


class ApmTransaction:
    """
    Elastic APM transaction manager for a DAG Task.
        Without configuration it self disables
    """

    @property
    def _apm_server_url(self) -> Optional[str]:
        # Environment variable indicating how to connect to dependencies on the service mesh
        raw_mesh_config = environ.get("MESH_CONFIG", default="null")
        mesh_config = json.loads(raw_mesh_config)
        if not mesh_config:  # no mesh config at all
            return None
        if not mesh_config.get("system-monitoring-log-apm"):  # no mesh config for apm
            return None
        return f"http://{mesh_config['system-monitoring-log-apm']['mesh_address']}:{mesh_config['system-monitoring-log-apm']['mesh_port']}"

    @property
    def _apm_other_options(self) -> dict:
        raw_options = environ.get("ELASTIC_APM_OTHER_OPTIONS", "{}")
        return json.loads(raw_options)

    @property
    def _apm_service_name(self) -> str:
        name = f"{self._workflow_name}-{self._workflow_version}"
        name = name.replace("_", "-")
        name = name.replace(".", "-")
        return name

    @property
    def _apm_is_active(self) -> bool:
        if not self._apm_server_url:
            return False
        value = environ.get("ELASTIC_APM_ENABLED", "false")
        return json.loads(value)

    @property
    def _apm_config(self) -> Optional[dict]:
        if not self._apm_is_active:
            return None
        apm_client_config = {
            "SERVICE_NAME": self._apm_service_name,
            "SERVER_URL": self._apm_server_url,
            "ENVIRONMENT": "Workflows",
            **self._apm_other_options,
        }
        return apm_client_config

    def __init__(self, transaction_name: str, workflow_name: str, workflow_version: str) -> None:
        self._workflow_name = workflow_name
        self._workflow_version = workflow_version
        self.configured = bool(self._apm_config)
        if self.configured:
            self.transaction_name = transaction_name
            self.client = elasticapm.Client(self._apm_config)
            self.instrument()
            self.client.begin_transaction(transaction_type="Task")
            logger.info(f"APM Configured: config={self._apm_config}")
        else:
            logger.warning(f"APM Not Configured")

    @contextmanager
    def capture_span(self, name: str, *args, **kwargs):
        if not self.configured:
            try:
                yield
            finally:
                pass
        else:
            try:
                with elasticapm.capture_span(name, *args, **kwargs):
                    yield
            finally:
                pass

    def close(self, exc_type=None):
        if not self.configured:
            return
        result = "Success"
        if exc_type is not None:
            result = "Error"
            self.client.capture_exception(handled=False)
        self.client.end_transaction(name=self.transaction_name, result=result)
        self.client.close()

    @staticmethod
    def instrument():
        """
        Vendored implementation of elasticapm.instrumentation.control.instrument changed to
          omit certain frameworks
        """
        omit_frameworks = {
            "elasticapm.instrumentation.packages.redis.RedisInstrumentation",
            "elasticapm.instrumentation.packages.redis.RedisPipelineInstrumentation",
            "elasticapm.instrumentation.packages.redis.RedisConnectionInstrumentation",
            "elasticapm.instrumentation.packages.asyncio.aioredis.RedisConnectionPoolInstrumentation",
            "elasticapm.instrumentation.packages.asyncio.aioredis.RedisPipelineInstrumentation",
            "elasticapm.instrumentation.packages.asyncio.aioredis.RedisConnectionInstrumentation",
        }

        from elasticapm.instrumentation.control import _lock
        from elasticapm.instrumentation.register import _cls_register
        from elasticapm.instrumentation.register import _instrumentation_singletons
        from elasticapm.instrumentation.register import import_string

        # from elasticapm.instrumentation.control.instrument
        with _lock:
            # update to vendored code
            filtered_cls_register = _cls_register.difference(omit_frameworks)
            # from elasticapm.instrumentation.register.get_instrumentation_objects
            for cls_str in filtered_cls_register:
                if cls_str not in _instrumentation_singletons:
                    cls = import_string(cls_str)
                    _instrumentation_singletons[cls_str] = cls()
                obj = _instrumentation_singletons[cls_str]
                # from elasticapm.instrumentation.control.instrument
                obj.instrument()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_type)
        # note: exception not captured through apm due to potential size of local variables


class TaskBase(ABC):
    """
    Generic wrapper for the DAG tasks providing a standard interface and execution flow.
    Each DAG task must implement its own subclass of this abstract wrapper class.

    Intended instantiation is as a context manager

    >>> class RealTask(TaskBase):
    >>>     def run(self):
    >>>         pass
    >>>
    >>> with RealTask(1, "a", "b") as task:
    >>>     task()

    Task names in airflow are the same as the class name
    Additional methods can be added but will only be called if they are referenced via run,
    pre_run, post_run, or __exit__

    overriding methods other than run, pre_run, post_run, and in special cases __exit__ is
    discouraged as they are used internally to support the abstraction.
    e.g. __init__ is called by the core api without user involvement so adding parameters will not
    result in them being passed in as there is no client interface to __init__.

    To use the apm infrastructure in subclass code one would do the following:

    >>> def foo(self):
    >>>     with self.apm_step("do detailed work"):
    >>>         pass # do work

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    retries = 0
    retry_delay_seconds = 60

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        self.recipe_run_id = int(recipe_run_id)
        self.workflow_name = workflow_name
        self.workflow_version = workflow_version
        self.task_name = self.__class__.__name__
        logger.info(f"Task {self.task_name} initialized")
        self.apm = ApmTransaction(
            transaction_name=self.task_name,
            workflow_name=self.workflow_name,
            workflow_version=self.workflow_version,
        )
        self.apm_step = self.apm.capture_span  # abbreviated syntax for capture span context mgr

    def pre_run(self) -> None:
        """
        Method intended to be overridden that will execute prior to run() with Elastic APM span
        capturing
        """

    @abstractmethod
    def run(self) -> None:
        """
        Abstract method that must be overridden to execute the desired DAG task.
        """

    def post_run(self) -> None:
        """
        Method intended to be overridden that will execute after run() with Elastic APM span
        capturing
        """

    def __call__(self) -> None:
        """
        The main executable function for the DAG task wrapper. Execution is instrumented with
        Application Performance Monitoring if configured. The standard execution sequence is:

        1 run

        2 record provenance

        Returns
        -------
        None
        """

        logger.info(f"Task {self.task_name} started")
        with self.apm_step("Pre Run"):
            self.pre_run()
        with self.apm_step("Run"):
            self.run()
        with self.apm_step("Post Run"):
            self.post_run()
        logger.info(f"Task {self.task_name} complete")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Method that can be overridden to execute teardown tasks after task execution regardless
        of task execution success.  Only override this method with tasks that need to happen
        regardless of tasks having an exception, ensure that no additional exception
        will be raised, and always call super().__exit__
        """
        self.apm.close(exc_type=exc_type)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"recipe_run_id={self.recipe_run_id}, "
            f"workflow_name={self.workflow_name}, "
            f"workflow_version={self.workflow_version}, "
            f")"
        )

    def __str__(self):
        return repr(self)
