# -*- coding: utf-8 -*-

import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from functools import partial, lru_cache
from itertools import chain
from operator import itemgetter
from typing import MutableMapping, List, Union, Coroutine, Type, Sequence, Dict, Callable, Awaitable, Optional, \
    Iterator, NoReturn, Tuple

from patchwork.core import Task, AsyncSubscriber
from patchwork.core.config.base import ComponentConfig
from patchwork.core.typing import FuncPath
from patchwork.core.utils import cached_property, Flag
from patchwork.node.core import Module
from patchwork.node.core.exceptions import TaskControlException, TaskRetry, TaskFatal, TaskDrop, TaskNoHandler
from patchwork.node.core.router import TaskRouter
from patchwork.node.executor.unit import InlineUnit
from patchwork.node.executor.unit.base import ProcessingUnit

# task finalizer, run when task processing completes, if third argument is None
# means that task has been not processed as there was no processor to handle it
FinalizerType = Callable[[Task, AsyncSubscriber, asyncio.Future], Awaitable]
# middleware is to prepare task processing environment, optional finalizer is a method which
# will be called to finalize task processing. Middleware may return new finalizer which should
# invoke given finalizer internally for proper task finalization
# if middleware does not return new finalizer, passed finalizer will be used
# middlewares are run on the worker async loop, before passing task to processing unit!
# keep this in mind as middleware execution may slow down whole executor
MiddlewareType = Callable[[Task, AsyncSubscriber, FinalizerType], Awaitable[Optional[FinalizerType]]]

ExceptionHandler = Callable[[Task, Exception], Awaitable]


async def check_task_middleware(task: Task, receiver: AsyncSubscriber, finalizer: FinalizerType):
    now = datetime.utcnow().timestamp()
    if task.meta.HasField('expires') and now > task.meta.expires.ToSeconds():
        # task has expired
        raise TaskFatal(reason="Task has expired")
    elif task.meta.HasField('not_before') and now < task.meta.not_before.ToSeconds():
        # task is not ready yet
        raise TaskRetry(countdown=(now - task.meta.not_before))


async def default_task_exception_handler(task: Task, exception: Exception) -> NoReturn:
    if isinstance(exception, TaskControlException):
        raise exception

    # request task retry
    raise TaskRetry()


class Idempotent:

    idempotent = True

    def __init__(self, fn):
        self._fn = fn

    def __call__(self, task: Task, exc: Exception):
        try:
            return self._fn(task, exc)
        except TaskControlException:
            raise RuntimeError(f"Idempotent exception handlers can't raise TaskControlExceptions")

    def __repr__(self):
        return f"idempotent<{repr(self._fn)}>"


class BaseExecutor(Module):
    """
    Executor is responsible of taking tasks from supported queue, spawn and manage workers
    to run these tasks and implement ability to send new tasks to the queue though clients.
    """

    class Config(Module.Config):

        # executor termination timeout in seconds
        terminate_timeout: int = 10

        # retry limit for the worker, it will be forced even if task max retries is greater
        max_retries: int = 10

        unit: ComponentConfig[Type[ProcessingUnit]] = ComponentConfig(InlineUnit)
        middlewares: Sequence[FuncPath] = [
            FuncPath(check_task_middleware)
        ]

    EVENTS = Module.EVENTS + ('task', )

    _loop_task: asyncio.Future
    _routers: List[Tuple[str, TaskRouter]]
    _unit_monitor_task: asyncio.Future
    _busy: Flag

    def __init__(self, *, parent, **options):
        super().__init__(parent=parent, **options)

        self._terminate_request = asyncio.Event()
        self._current_tasks = set()
        self._routers = []
        self._middlewares: List[MiddlewareType] = []
        self._exc_handlers: Dict[type, List] = {}

        for middleware in self.settings.middlewares:
            self.add_middleware(middleware)

        self.add_exception_handler(Exception, default_task_exception_handler)
        self._busy = Flag()

    def __repr__(self):
        res = super().__repr__()
        return f"<{res[1:-1]} " \
               f"unit={self.unit.__class__.__name__}]>"

    def get_state(self) -> MutableMapping:
        return {
            'worker': self.unit.get_state(),
            'current_tasks': len(self._current_tasks),
            'busy': self._busy.value
        }

    @property
    def busy(self) -> Flag:
        return self._busy

    @cached_property
    def unit(self) -> ProcessingUnit:
        return self.settings.unit.instantiate(parent=self)

    def add_router(self, router: TaskRouter, prefix: str = ''):
        """
        Adds a router to the executor. Routers are responsible for routing tasks to proper handlers.
        :param prefix:
        :param router:
        :return:
        """
        router.bind(self.worker)
        for idx, rdata in enumerate(self._routers):
            if prefix == rdata[0]:
                raise ValueError(f"routers prefix conflict: prefix is already taken by another router")

            if prefix.startswith(rdata[0]):
                # if given prefix starts with one of already registered prefix, put
                # new router on higier priority then existing one
                self._routers.insert(idx, (prefix, router))
                break
        else:
            self._routers.append((prefix, router))

    def add_middleware(self, middleware: MiddlewareType):
        """
        Adds a middleware to be executed for each task before it starts processing
        :param middleware:
        :return:
        """
        self._middlewares.append(middleware)

    def add_exception_handler(self, exception: type, handler: ExceptionHandler, idempotent: bool = False):
        """
        Register a handler for given exception type (and subtypes). Exception handlers are called
        in LIFO manner - last registered handler is firstly called.

        If any handler raises one of TaskControlException it's handled by the executor and then no more exception
        handlers are executed (except idempotent ones)
        :param exception:
        :param handler:
        :param idempotent: if True, handler will be executed even if TaskControlException has been raised by one
        of previously executed handlers.
            :: warning
                Idempotent handlers CAN'T raise TaskControlExceptions.
        :return:
        """
        if exception not in self._exc_handlers:
            self._exc_handlers[exception] = []

        if idempotent:
            handler = Idempotent(handler)
        self._exc_handlers[exception].insert(0, handler)

    async def _start(self):
        """
        Setups executor
        :return:
        """

        # clear terminate request flag
        self._terminate_request.clear()

        # start processing unit
        await self.unit.run()

        self._unit_monitor_task = asyncio.create_task(self._unit_monitor())

        # put executor loop task on event loop
        self._loop_task = asyncio.ensure_future(self._loop(), loop=self.app_loop)
        self._loop_task.add_done_callback(self._loop_completed_callback)

    async def _unit_monitor(self):
        try:
            await self.unit.state.wait_for(False)
        except asyncio.CancelledError:
            return

        self.logger.error(f"Executor processing unit unexpectedly terminated. Executor can't continue")

        self.harakiri()

    def _loop_completed_callback(self, fut: asyncio.Future):

        if fut.cancelled():
            # loop should never be cancelled
            raise AssertionError("DO NOT CANCEL executor loop! Set termination_request event instead to make"
                                 "sure that loop is stopped cleanly and no message was lost")

        exc = fut.exception()
        if exc:
            self.logger.error(f"Executor loop completed with exception: {exc.__class__.__name__}({exc})")
            self.harakiri()

    async def _stop(self):
        """
        Stops executor and all running tasks, when method returns event loop can be stopped
        :return:
        """

        # set terminate request flag
        self._terminate_request.set()
        self.logger.debug(f"Executor termination requested, "
                          f"waiting {self.settings.terminate_timeout}s to complete...")

        # wait for termination
        done, pending = await asyncio.wait([self._loop_task], timeout=self.settings.terminate_timeout)

        if pending:
            self.logger.warning("Loop task termination timeout, cancelling")

            # this raises CancelledError in loop task, there is no way to predict where exactly in code
            # it happens
            self._loop_task.cancel()

            # timeout to be safe
            done, pending = await asyncio.wait([self._loop_task], timeout=self.settings.terminate_timeout)

            if pending:
                self.logger.error("Unable to terminate executor main loop")

        # stop processing unit, executor loop is stopped so no more task may come,
        # drop what unit has queued and what is currently processing
        # there should be no more job to do about tasks, commit() method has been not
        # called so tasks assigned to the processing unit should be not lost
        try:
            await asyncio.wait_for(self.unit.busy.wait_for(False), timeout=self.settings.terminate_timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"Processing unit is still busy, timeout elapsed")

        self._unit_monitor_task.cancel()
        await self.unit.terminate()

        # wait for tasks callbacks to complete (commit, retry..., the last job is removing task from the
        # _current_tasks set)
        if self._current_tasks:
            await asyncio.wait(self._current_tasks)

    async def _loop(self):
        """
        This is an executor main loop task. Waits on all listen_on subscribers simultaneously for
        incoming task.
        DO NOT CANCEL THIS CORO as it can break flow in a way which may leads to message lost.
        Set self._termination_request event to request the loop termination.
        :return:
        """
        # future of termination request
        term_future = asyncio.create_task(self._terminate_request.wait())
        subscriber = self.worker.get_subscriber()
        self._busy.set(False)

        while True:

            try:
                done, pending = await asyncio.wait((asyncio.create_task(subscriber.get()), term_future,),
                                                   return_when=asyncio.FIRST_COMPLETED)
            except Exception as e:
                self.logger.error(f"Client get() raises exception: {e.__class__.__name__}({e})",
                                  exc_info=True)
            else:
                for task in done:
                    if task == term_future:
                        # termination future done, even if there is more done futures skip them
                        # worker is going down
                        for fut in pending:
                            fut.cancel()
                        return

                    await self._handle_done_waiter(task, subscriber)

    async def _handle_done_waiter(self, future: asyncio.Future, receiver: AsyncSubscriber) -> bool:
        """
        Handles done waiter future of the client
        :param future:
        :param receiver:
        :return: True if loop should still listen on this client, False otherwise
        """

        if future.cancelled():
            # ygm? maybe something else disabled this client... do not put it back
            self.logger.info(f"Waiter of client {receiver} cancelled")
            await receiver.terminate()
            return False

        exc = future.exception()
        if exc:
            self.logger.error(f"Client {receiver} waiter completed with exception: "
                              f"{exc.__class__.__name__}({exc})")
            return True

        task: Task = future.result()
        self.logger.debug(f"Client {receiver} waiter returned a task message: {task.uuid}")

        self._busy.set(True)
        task_future = self.app_loop.create_future()
        self._current_tasks.add(task_future)
        task_future.add_done_callback(self._task_handling_completed)

        await self._dispatch_event('task', task=task)

        try:
            await self.handle(task, receiver, task_future)
        except Exception as e:
            # log error and do not commit task if something went wrong during internal scheduling
            self.logger.error(f"Unable to handle task '{task.uuid}', exception raised: {e.__class__.__name__}({e})")
            task_future.set_exception(e)

        return True

    async def retry(self, task: Task, *, countdown: float = None,
                    not_before: datetime = None, bump_attempts: bool = True) -> Union[Task, None]:
        """
        Retries given task by cloning it and sending through publisher.
        :param task:
        :param countdown:
        :param not_before:
        :param bump_attempts:
        :return:
        """
        new_task = Task()
        new_task.CopyFrom(task)
        new_task.uuid = ''

        if bump_attempts:
            new_task.meta.attempt += 1
            max_retries = min(task.meta.max_retries, self.settings.max_retries) \
                if task.meta.max_retries > 0 else self.settings.max_retries

            if new_task.meta.attempt > max_retries:
                await self.backoff_task(task, reason="Max number of retries exceeded")
                return

        if countdown is not None:
            assert not_before is None, "both `countdown` and `not_before` arguments cannot be set at the same time"

            not_before = datetime.utcnow().timestamp() + countdown

        if not_before is not None:
            new_task.meta.not_before.FromDatetime(not_before)

        publisher = self.worker.get_publisher()
        await publisher.send_task(new_task)
        return new_task

    async def backoff_task(self, task, reason: str = None):
        """
        Stores given task on backoff queue. If task cannot be executed for some reason (eg retries limit exceeded)
        can be logged and saved in special place for future investigation. This method allows to notify administrator
        that something has been not executed and should be manually verified.

        In base implementation this method just logs task using 'backoff' standard python logger and passes
        task in `extra` argument, which means that in basic configuration task contents might be lost.
        :param task:
        :param reason:
        :return:
        """
        backoff_log = logging.getLogger('backoff')
        backoff_log.log(logging.NOTSET,
                        f"Task '{task.uuid}' backoffed.{(' Reason: ' + reason) if reason is not None else ''}",
                        extra={'task': task})
        self.logger.debug(f"Task '{task.uuid}' backoffed.{(' Reason: ' + reason) if reason is not None else ''}")

    async def handle(self, task: Task, receiver: AsyncSubscriber, task_future: asyncio.Future):
        """
        Executes given task, handles all exceptions which may rise during task
        processing.

        :: warning:
            This method may raise exception if task scheduling fail.

        :: note:
            This method awaits only for task scheduling, not task execution itself. When returns task
            is internally scheduled on processing unit. If you need task execution result await on returned
            future.

        :param task: task to process
        :param receiver: a subscriber (receiver) which receives the task
        :param task_future: a future associated with the task which should resolved when task processing completes
        """
        finalizer = self._handle_task_result

        try:
            for middleware in self._middlewares:
                finalizer = (await middleware(task, receiver, finalizer)) or finalizer

            finalizer = partial(finalizer, task=task, receiver=receiver)

            exec_fut = await self._execute(task, receiver)
        except Exception as exc:
            exec_fut = self.app_loop.create_future()
            exec_fut.set_exception(exc)

        exec_fut.add_done_callback(
            partial(self._task_done_callback, finalizer=finalizer(processing_fut=exec_fut), task_future=task_future)
        )

    def _task_handling_completed(self, task_future):
        self._current_tasks.remove(task_future)
        if not self._current_tasks:
            self._busy.set(False)

    async def _execute(self, task: Task, receiver: AsyncSubscriber):
        """
        Executes a task on given processor
        :param task:
        :param receiver:
        :return:
        """
        for prefix, router in self._routers:
            if not task.task_type.startswith(prefix):
                continue

            processor = router.handle(task, receiver)
            if processor is not None:
                # await for submit which may hold if processing unit is full
                pu_fut = await self.unit.submit(processor)
                return pu_fut

        self.logger.error(f"No route to handle message type '{task.task_type}'")
        raise TaskNoHandler()

    def _task_done_callback(self,
                            processing_fut: asyncio.Future,
                            finalizer: Coroutine,
                            task_future: asyncio.Future
                            ):
        """
        Handles value returned by task processing future.
        :param finalizer:
        :param processing_fut:
        :param task_future:
        :return:
        """
        def _callback(f: asyncio.Future):
            if f.cancelled():
                # if finalizer has been cancelled to not pass result from task
                # processing future to task future, set it to None as there is no ready result as finalizers
                # were not completed
                task_future.set_result(None)
                return

            exc = f.exception()
            if exc is not None:
                # if finalizer ends with unhandled exception it's internal fatal error
                # kill the executor
                task_future.set_result(None)
                self.logger.fatal(f"Can't handle task result: {exc.__class__.__name__}({exc})")
                self.harakiri(exc)

            # otherwise pass processing future result to task result
            if processing_fut.cancelled():
                task_future.cancel()
            elif processing_fut.exception():
                task_future.set_exception(processing_fut.exception())
            else:
                task_future.set_result(processing_fut.result())

        handle_fut = self.app_loop.create_task(finalizer)
        handle_fut.add_done_callback(_callback)

    @lru_cache(maxsize=None)
    def _get_exception_handler(self, exception) -> Iterator[ExceptionHandler]:
        handlers = []

        for exc_type, callbacks in self._exc_handlers.items():
            if not isinstance(exception, exc_type):
                continue

            done = False
            for idx, item in enumerate(handlers):
                if exc_type == item[0]:
                    item[1].extend(callbacks)
                    done = True
                    break

                if issubclass(exc_type, item[0]):
                    handlers.insert(idx, (exc_type, list(callbacks)))
                    done = True
                    break

            if not done:
                handlers.append((exc_type, list(callbacks)))

        return chain.from_iterable(map(itemgetter(1), handlers))

    async def _handle_task_result(self, task: Task, receiver: AsyncSubscriber, processing_fut: asyncio.Future):
        """
        Handles task future result.
        :param task:
        :param receiver:
        :param processing_fut:
        :return:
        """
        exc = processing_fut.exception()
        if processing_fut.cancelled():
            self.logger.info(f"Task '{task.task_type} (uuid={task.uuid})' execution cancelled internally")
            return
        elif exc is not None:
            if not isinstance(exc, TaskControlException):
                self.logger.warning(f"Task '{task.task_type} (uuid={task.uuid})' "
                                    f"execution failed with exception {exc.__class__.__name__}({exc})")
            else:
                self.logger.info(f"Task '{task.task_type} (uuid={task.uuid})' "
                                 f"ended with TCE {exc.__class__.__name__}")

            handlers = self._get_exception_handler(exc)
            finalized = False

            for handler in handlers:
                if finalized and not getattr(handler, 'idempotent', False):
                    # if task is finalized (there was a TCE raised and handled), run only
                    # handlers declared as idempotent
                    continue

                try:
                    await handler(task, exc)
                except TaskControlException as control_exc:
                    self.logger.debug(f"Task '{task.task_type} (uuid={task.uuid})' "
                                      f"exception handler '{handler}' requested TCE {exc.__class__.__name__}")
                    await self._handle_task_control(task, control_exc)
                    finalized = True
                except Exception as exc:
                    self.logger.exception(f"exception handler failed: {exc.__class__.__name__}({exc})")
                    if self.worker.debug:
                        raise exc
        else:
            self.logger.info(f"Task '{task.task_type} (uuid={task.uuid})' processing completed")
        await self._commit_task(task, receiver)

    async def _handle_task_control(self, task: Task, exc: Exception):
        """
        Takes appropriate action for the task depending on given task control exception.
        This method commits task.
        :param task:
        :param exc:
        :return:
        """
        if isinstance(exc, TaskRetry):
            # schedule new task
            await self.retry(task, not_before=exc.not_before)
        elif isinstance(exc, TaskFatal):
            await self.backoff_task(task, reason=(exc.reason or "Task processing fatal error"))
            # backoff just logs task, commit it to truly remove from the queue
        elif isinstance(exc, TaskDrop):
            pass
        elif isinstance(exc, TaskControlException):
            self.logger.error(f"Unsupported task control exception '{exc.__class__.__name__}({exc})'")
            if self.worker.debug:
                raise ValueError("unknown task control exception")

    async def _commit_task(self, task: Task, receiver: AsyncSubscriber):
        """
        Commits the task on the underlying queue.
        :param task:
        :return:
        """
        await receiver.commit(task)

    def harakiri(self, cause: BaseException = None):
        """
        Stops executor immediately due to critical internal error.
        Call this method if something went so wrong that there is no better way than killing this executor
        which cause clients disconnection from message broker and leaving uncommitted all tasks which
        are in progress or pending. Broker should consider this worker as dead and stop delivering new messages.
        :return:
        """
        if self.worker.debug and cause:
            # in debug mode raise SystemExit to blow up
            raise SystemExit() from cause

        self.logger.error("Executor harakiri requested")
        self.app_loop.create_task(self.terminate())
