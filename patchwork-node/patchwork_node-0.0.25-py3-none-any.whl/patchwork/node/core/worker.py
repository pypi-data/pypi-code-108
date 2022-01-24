# -*- coding: utf-8 -*-

import weakref
from asyncio import AbstractEventLoop, Future
from multiprocessing.managers import BaseManager

import asyncio
import importlib_metadata
import logging
import logging.config
import multiprocessing
import os
import psutil
import signal
import sys
import threading
import warnings
from datetime import datetime
from functools import partial
from humanize import naturalsize, naturaldelta
from pydantic import BaseModel
from time import time
from typing import Mapping, MutableMapping, Iterable, Dict, Type, Optional, Literal

from patchwork.core import AsyncPublisher, AsyncSubscriber, Component
from patchwork.core.client.local import AsyncLocalPublisher, AsyncLocalSubscriber
from patchwork.core.config.base import ComponentConfig, PublisherConfig, SubscriberConfig
from patchwork.core.typing import LoggingConfig
from patchwork.core.utils import cached_property
from patchwork.node.core import Module
from patchwork.node.core.router import TaskRouter
from patchwork.node.executor import BaseExecutor
from patchwork.node.manager.base import Manager
from patchwork.node.manager.http import HttpManager

if sys.version_info < (3, 9):
    from functools import lru_cache
    cache = lru_cache(maxsize=None)
else:
    from functools import cache


LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "patchwork": {"handlers": ["default"], "level": "INFO"},
    },
}


class WorkerSettings(BaseModel):

    debug: bool = False
    enabled: bool = True

    logging: LoggingConfig = LOGGING_CONFIG

    # executor unit
    executor: ComponentConfig[Type[BaseExecutor]] = ComponentConfig(BaseExecutor)

    # manager unit
    manager: ComponentConfig[Type[BaseManager]] = ComponentConfig(HttpManager, {
        'listen_on': '127.0.0.1:4444'
    })

    # optional list of additional modules to load
    modules: Dict[str, ComponentConfig] = {}

    publisher: Optional[PublisherConfig] = PublisherConfig(AsyncLocalPublisher)

    # clients for queues
    subscriber: SubscriberConfig = SubscriberConfig(AsyncLocalSubscriber)


class PatchworkWorker(Module):

    # worker settings dataclass
    settings: WorkerSettings

    _event_loop: AbstractEventLoop
    monitor_task: Future

    def __init__(self, settings_class: type = WorkerSettings, settings: Mapping = None, **kwargs):
        super().__init__(**kwargs)
        self._settings_schema = settings_class
        self._load_settings(settings)

    @cached_property
    def logger(self) -> logging.Logger:
        return logging.getLogger('patchwork.node')

    @property
    def event_loop(self):
        return self._event_loop

    @property
    def process_name(self):
        return f'#{os.getpid()}: {multiprocessing.current_process().name}'

    @cached_property
    def manager(self) -> Manager:
        """
        Returns worker manager instance
        :return:
        """
        return self.settings.manager.instantiate(parent=self)

    @cached_property
    def executor(self) -> BaseExecutor:
        """
        Returns worker executor instance
        :return:
        """
        return self.settings.executor.instantiate(parent=self)

    @cached_property
    def modules(self):
        return {k: v.instantiate(parent=self) for k, v in self.settings.modules.items()}

    @property
    def debug(self):
        return self.settings.debug

    def middleware(self, flow: Literal['task'] = 'task'):

        if flow == 'task':
            def wrapper(fn):
                assert asyncio.iscoroutinefunction(fn)
                self.executor.add_middleware(fn)
                return fn
        else:
            raise NotImplementedError()

        return wrapper

    def exception_handler(self, exception_class: type):
        def wrapper(fn):
            assert asyncio.iscoroutinefunction(fn)
            self.executor.add_exception_handler(exception_class, fn)
            return fn

        return wrapper

    def _load_settings(self, settings: Mapping = None):
        """
        Load settings from worker settings JSON file and then updates values
        using environment variables if JSON file has no `locked_settings` flag enabled.
        :return:
        """
        try:
            self.settings = self._settings_schema(**(settings or {}))
        except Exception as e:
            self.logger.error(f"Unable to load settings: {e}")
            return False

        if self.settings.debug:
            warnings.warn("Debug mode enabled")
        return True

    def get_module(self, name: str) -> Module:
        """
        Returns module instance by given name
        :param name:
        :return:
        """
        return self.modules[name]

    @cache
    def get_publisher(self) -> AsyncPublisher:
        if self.settings.publisher is None:
            raise RuntimeError("can't use publisher as it's not configured")

        return self.settings.publisher.instantiate(self)

    @cache
    def get_subscriber(self) -> AsyncSubscriber:
        return self.settings.subscriber.instantiate(self)

    def main(self):
        """
        Runs the worker. This method is blocking until worker receive TERM signal.
        :return:
        """
        ev_loop = self._get_event_loop()

        # put executor start at event loop
        start_task = ev_loop.create_task(self.run())
        start_task.add_done_callback(self._on_started)

        # noinspection PyBroadException
        try:
            self.logger.debug("Starting worker event loop")
            ev_loop.run_forever()
            self.logger.debug("Worker event loop completed")
        except Exception:
            self.logger.fatal("Worker execution ends with unexpected exception", exc_info=True)

    def _on_started(self, fut: Future):
        exc = fut.exception()
        if exc:
            self.logger.error(f"Worker cannot be started due to exception: {type(exc).__name__}({exc})")

            # stop event loop if executor is not running
            # TODO: some cleanups are necessary?
            self._event_loop.stop()

            if getattr(self.settings, "debug", False):
                raise exc

            return

        if fut.result() is False:
            self.logger.error("Worker didn't start. See logs above for more details")
            self.terminate_worker()
            return

        self.logger.info("Node is up and running")

        # noinspection PyBroadException
        try:
            node_version = importlib_metadata.version('patchwork.node')
        except importlib_metadata.PackageNotFoundError:
            node_version = 'development'

        if self.settings.debug:
            print("\nPatchwork Node is up and running.")
            print(f"Version: {node_version}")
            print("Send TERM or INT signal to terminate")
            print("DEBUG MODE ENABLED, DO NOT RUN IN DEBUG ON PRODUCTION")

    async def _start(self):

        assert threading.current_thread() is threading.main_thread(), "Worker must start in MainThread"
        self._event_loop = asyncio.get_running_loop()

        self._setup_signals()

        self._setup_logger()
        self.logger.info("Worker initialized")

        # first starts manager
        self.logger.debug("Starting manager")
        await self.manager.run()
        self.logger.debug("Manager started")

        # then start additional modules, all at once, if modules depends on each other should await
        # internally. Use get_module() worker method to get module instance and await on state flag
        # Be careful of deadlocks

        start_jobs = [mod.run() for mod in self.modules.values()]
        if start_jobs:
            self.logger.debug("Starting additional modules")
            await asyncio.wait(start_jobs)
            self.logger.debug("All additional modules started")
        else:
            self.logger.debug("No additional modules to start")

        # start clients
        if self.settings.publisher is not None:
            await self.get_publisher().run()
            self.logger.debug("Publisher started")
        else:
            self.logger.debug("No publisher configured")

        await self.get_subscriber().run()
        self.logger.debug("Subscriber started")

        # end executor at the end when everything is ready
        self.logger.debug("Starting executor")
        await self.executor.run()
        self.logger.debug("Executor started")

        self.logger.info("Worker node is up and running")

        self.monitor_task = asyncio.create_task(self._monitor_submodules(
            (self.manager, self.executor) + tuple(self.modules.values())
        ))
        self.monitor_task.add_done_callback(self._on_monitor_stop)

    async def _monitor_submodules(self, submodules: Iterable[Component]):
        flags = {asyncio.ensure_future(s_mod.state.wait()): weakref.ref(s_mod) for s_mod in submodules}
        while True:
            try:
                done, pending = await asyncio.wait(flags.keys(), return_when=asyncio.FIRST_COMPLETED)

                if len(done) != 1:
                    self.logger.error(f"Monitor got invalid number of done flags, expected: 1, got: {len(flags)}")
                    continue

                done = done.pop()
                s_mod_ref = flags.pop(done)

                # dereference
                s_mod = s_mod_ref()

                if s_mod is None:
                    self.logger.warning(f"Stopped module disappeared")
                    continue

                self.logger.warning(f"{s_mod} terminated unexpectedly")
                recovered = await s_mod.recover()
            except asyncio.CancelledError:
                # cancel all active waiters
                for fut in flags.keys():
                    fut.cancel()

                raise
            else:
                if recovered:
                    # recovered!
                    flags[asyncio.ensure_future(s_mod.state.wait())] = weakref.ref(s_mod)
                    continue
                else:
                    self.logger.fatal(f"{s_mod} cannot be recovered after unexpected termination")
                    # if submodule cannot be recovered it means that application is in inconsistent
                    # and potentially invalid state, terminate it
                    self.terminate_worker()

    def _on_monitor_stop(self, fut: asyncio.Future):
        if fut.cancelled():
            # monitor should never completes, it's run forever until cancelled
            self.logger.debug("Submodules monitor stopped")
            return

        exc = fut.exception()
        if exc:
            self.logger.fatal(f"Submodules monitor terminate with exception: {exc.__class__.__name__}({exc})")
        else:
            self.logger.fatal(f"Submodules monitor terminates unexpectedly")

        self._event_loop.create_task(self.terminate())

    def _setup_logger(self):
        if self.settings.logging:
            logging.config.dictConfig(self.settings.logging)

        now = time()
        self.logger.debug(f"Logging configured. Current time is {now} ({datetime.fromtimestamp(now)})")

    def include_router(self, router: TaskRouter, prefix: str = ''):
        """
        Register and setup given processor. Awaits until processor setup is done
        :param prefix: task type prefix for matching tasks
        :param router: router to handle matching tasks
        :return:
        """
        self.executor.add_router(router, prefix=prefix)

    def _setup_signals(self):
        # setup signals using asyncio
        self._event_loop.add_signal_handler(signal.SIGUSR1, partial(self._handle_info_signal, signal.SIGUSR1, None))
        self._event_loop.add_signal_handler(signal.SIGTERM, partial(self._handle_term_signal, signal.SIGTERM, None))
        self._event_loop.add_signal_handler(signal.SIGINT, partial(self._handle_term_signal, signal.SIGTERM, None))

        self._terminate_request = asyncio.Event()

    def get_state(self) -> MutableMapping:
        process = psutil.Process(os.getpid())
        stats = process.as_dict(attrs=(
            'pid', 'status', 'nice', 'io_counters', 'memory_info', 'cpu_times', 'create_time', 'memory_percent',
            'cpu_percent'
        ))

        cpu_limit = process.rlimit(psutil.RLIMIT_CPU)
        mem_limit = process.rlimit(psutil.RLIMIT_RSS)
        threads = threading.enumerate()

        async_tasks = [t for t in asyncio.Task.all_tasks(loop=self._event_loop) if not t.done()]
        process_started = datetime.fromtimestamp(stats['create_time'])

        result = {
            'process': {
                'pid': stats['pid'],
                'status': stats['status'],
                'nice': stats['nice']
            },
            'resources': {
                'io counters': stats['io_counters'],
                'memory usage': naturalsize(stats['memory_info'].rss),
                'memory system [%]': f'{stats["memory_percent"]:.02f} %',
                'cpu times': stats['cpu_times'],
                'cpu usage [%]': f'{stats["cpu_percent"]:.02f} %',
                'started at': str(process_started),
                'uptime': naturaldelta(time() - stats['create_time']),
                'threads': [
                    {'name': t.name, 'daemon': t.daemon, 'alive': t.is_alive()} for t in threads
                ]
            },
            'limits': {},
            'futures': [f"{t._state} {t._coro.cr_code.co_name}() on {t._coro.cr_frame.f_locals['self']}"
                        for t in async_tasks],
            'worker': self.executor.get_state()
        }

        if mem_limit[1] != -1:
            result['limit']['memory'] = {
                'used': f'{(stats["memory_info"].rss/mem_limit[1]):.02f}',
                'limit': f'{naturalsize(mem_limit[0])} | {naturalsize(mem_limit[1])}'
            }

        if cpu_limit[0] != -1:
            result['limit']['cpu'] = {
                'used': f'{(stats["cpu_times"].user/cpu_limit[1])*100:.02f} %',
                'limit': cpu_limit,
            }

        return result

    def _handle_info_signal(self, signum, frame):
        stats = self.get_state()

        sys.stdout.write(f"Executor state information\n"
                         f"--------------------------\n")
        self._print_stats_dict(stats)
        sys.stdout.flush()

    def _print_stats_dict(self, data: Mapping, indentation=1):
        indent = "\t" * indentation
        for name, value in data.items():
            if not value:
                continue

            sys.stdout.write(f'{indent}{name} = ')

            if isinstance(value, dict):
                sys.stdout.write('\n')
                self._print_stats_dict(value, indentation+1)
            elif isinstance(value, (list, tuple)):
                sys.stdout.write('[\n{}]\n'.format(",\n".join(f"\t{v}" for v in value)))
            else:
                sys.stdout.write(f'{value}\n')

    def _handle_term_signal(self, signum, frame):
        self.terminate_worker()

    def terminate_worker(self):
        if self._terminate_request.is_set():
            self.logger.error("Termination signal received again, suicide")

            # restore python sigterm default handler
            signal.signal(signal.SIGTERM, signal.SIG_DFL)

            # send re-send sigterm to terminate process
            os.kill(os.getpid(), signal.SIGTERM)

        self._terminate_request.set()

        self.logger.info(f"Worker termination request received, terminating...")
        stop_job = self._event_loop.create_task(self.terminate())
        stop_job.add_done_callback(self._stop_job_done)

    async def _stop(self):
        # stop submodules monitor
        self.logger.debug("Stopping submodules monitor...")
        self.monitor_task.cancel()

        self.logger.debug("Waiting executor to complete...")
        # wait for executor, because working processors may depends on submodules, so terminate them
        # firstly
        await self.executor.terminate()
        self.logger.debug("Executor completed")

        # stop clients, there should be no messages pending on clients as executor is completed
        await self.get_subscriber().terminate()

        if self.settings.publisher is not None:
            await self.get_publisher().terminate()

        stop_jobs = [mod.terminate() for mod in self.modules.values()]
        if stop_jobs:
            self.logger.debug("Waiting for submodules stop jobs to complete...")
            # executor is down, stop all submodules simultaneously, stop jobs should not depends on each other
            await asyncio.wait(stop_jobs)
            self.logger.debug("Submodules completed")
        else:
            self.logger.debug("No stop jobs for submodules")

        self.logger.debug("Waiting for manager to stop...")
        await asyncio.wait([asyncio.create_task(self.manager.terminate())])
        self.logger.debug("Manager stopped")

        self_task = asyncio.current_task(loop=self._event_loop)
        tasks_left = [t for t in asyncio.all_tasks(self._event_loop) if not t.done() and t != self_task]

        if tasks_left:
            self.logger.error(f"{len(tasks_left)} tasks left in the event loop after stopping all modules")
        else:
            self.logger.debug("No tasks left after stop job, event loop can be stopped clearly")

        self.logger.info("Worker node completed")

    def _stop_job_done(self, fut: Future):
        fut.result()
        self._event_loop.stop()

    @classmethod
    def _get_event_loop(cls):
        return asyncio.get_event_loop()
