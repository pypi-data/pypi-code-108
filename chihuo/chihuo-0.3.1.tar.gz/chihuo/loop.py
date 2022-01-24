from typing import Union, Dict, Tuple, Optional, Any, cast
import traceback
import logging
import asyncio
import json as stdjson
import types

from .server import Server
from .common import SERVER_DEFAULT_CONFIG_PATH, TaskType, TaskId, Direction
from .config import parse_server_config
from .util import serialize_json

logger = logging.getLogger(__name__)


class ChihuoLoop:
    """Chihuo async loop abstract class

    The class handles all asynchronous tasks which are created
    by the `make_task` method of its subclass.

    The class connects to a Chihuo server to persist all tasks.
    All running tasks are received from the backend server.
    So, for adding a task to the loop, subclass must use the
    `add_task` method to add the task to the backend server,
    then the loop can automaticly get a task from the backend
    server. The received task is passed to `make_task` to make
    an asynchronous generator which is added to the asynchronous
    loop.

    The backend server can be regarded as a bidirectional queue.

    Params:

    NAME: The unique project name (MUST BE ascii characters)
        It is the key to define the task queue of the project in
        backend server.

    CONCURRENCY: The number of all concurrent tasks

    SERVER_CONFIG: The configuration of the backend server
        It is a dict or a path to the configuration file.
        Default is the path 'chdb.config'
    """

    NAME: Optional[str] = None
    CONCURRENCY: int = 1
    SERVER_CONFIG: Union[str, Any] = SERVER_DEFAULT_CONFIG_PATH

    def __init__(self, run_forever: bool = True):
        if not self.NAME:
            logger.warning("NAME is missing")

        assert self.NAME, "NAME is missing"
        assert self.CONCURRENCY > 0, "CONCURRENCY must be > 0"

        logger.info(
            """
Initiate %s loop:
    NAME: %s
    CONCURRENCY: %s
    SERVER_CONFIG: %s""",
            self._cls_name,
            self.NAME,
            self.CONCURRENCY,
            self.SERVER_CONFIG,
        )

        self._concurrency = self.CONCURRENCY
        self._loop = asyncio.get_event_loop()

        self._server_config = parse_server_config(self.SERVER_CONFIG)
        self._server = Server(self.NAME, self._server_config, loop=self._loop)
        self._semaphore = asyncio.locks.Semaphore(self.CONCURRENCY, loop=self._loop)

        # Running tasks cache
        self._running_tasks: Dict[TaskId, Any] = {}

        # Count the running tasks
        self._lock = asyncio.Lock()
        self._running_tasks_count = 0

        self._stop = False
        self._run_forever = run_forever

    @property
    def _cls_name(self) -> str:
        return self.__class__.__name__

    @property
    def stop(self) -> bool:
        return self._stop

    @stop.setter
    def stop(self, val):
        self._stop = val

    @property
    def concurrency(self) -> int:
        return self._concurrency

    @concurrency.setter
    def concurrency(self, concurrency: int):
        self._concurrency = concurrency
        self._semaphore = asyncio.locks.Semaphore(self.CONCURRENCY, loop=self._loop)

    def _create_task(self, task, task_type: TaskType = None) -> asyncio.Task:
        """Wrap `loop.create_task`
        We add an id to task if `task_id` is not None
        """

        task_name: Optional[str] = None
        if task_type:
            task_name = task_type.value

        return self._loop.create_task(task, name=task_name)

    def _cache_task(self, task_id: TaskId, task: Any) -> None:
        """Cache running task"""

        self._running_tasks[task_id] = task

    def _uncache_task(self, task_id: TaskId) -> None:
        """Remove running task from cache"""

        self._running_tasks.pop(task_id, None)

    async def make_task(self, task_id: TaskId, task: Any) -> None:
        """This function is the procedure of a task.

        The function must be implemented for handling every tasks
        """

        logger.error("%s: make_task is not implemented", self._cls_name)
        raise NotImplementedError("ChihuoLoop.make_task must be implemented")

    async def next_task(self) -> Optional[Tuple[TaskId, Any]]:
        """Get next task from backend"""

        async with self._lock:
            value = await self._server.pop_left()
            if not value:
                return None
            value = cast(Tuple[TaskId, Union[str, bytes]], value)

            self._running_tasks_count += 1

        task_id, raw_task = value
        task = stdjson.loads(raw_task)
        return task_id, task

    async def _task_loop(self) -> None:
        """Main Task loop

        The loop pops tasks from backend to execute asynchronously.
        """

        while True:
            await self._semaphore.acquire()

            # Stop the loop
            if self._stop:
                logger.info("%s: task_loop stop", self._cls_name)
                self._release()
                return

            item = await self.next_task()
            if item:
                task_id, task = item
                future = self._create_task(
                    self._wrap_task(task_id, task), task_type=TaskType.Task
                )
                self._cache_task(task_id, task)
                future.add_done_callback(lambda _: self._uncache_task(task_id))
            else:
                await self.sleep(1)
                # Release the task
                self._release()

    async def _wrap_task(self, task_id: TaskId, task: Any) -> None:
        """Wrap task
        Handle `asyncio.CancelledError`

        If the task fails, adding task back to backend
        """

        try:
            await self.make_task(task_id, task)
        except Exception as err:
            await self.add_task(
                (task_id, task), ignore_running=False, direction=Direction.Reverse
            )
            logger.error(
                "task fail: %s, task_id: %s, task: %s, error: %s, traceback: %s",
                self._cls_name,
                task_id,
                task,
                err,
                traceback.format_exc(),
            )
        finally:
            # Release the semaphore for a completed task
            self._release()

        async with self._lock:
            self._running_tasks_count -= 1

            # The end event: running tasks is empty and the task queue is empty
            if not self._run_forever and self._running_tasks_count == 0:
                size = await self._server.size()
                if size == 0:
                    logger.info(
                        "`run_forever = %s`: It is the end. "
                        "There is no running tasks and the queue is empty.",
                        self._run_forever,
                    )
                    self._loop.stop()

    async def add_task(
        self,
        *pairs: Tuple[TaskId, Any],
        finished: bool = True,
        ignore_running: bool = False,
        direction: Direction = Direction.Forward
    ) -> None:
        """Add a task to backend server

        `pairs`: [(task_id1, task1), (task_id2, task2), ...]
            `pairs` are the information of tasks.

        `task_id`: str or bytes
            `task_id` is the unique identification for a task.
        `task`: object
            `task` is the information that can be dumped as json about the task.

        `finished`: bool
            if finished is true, we add the task only if the task is not finished.
            Else, we add the task whether or not the task is finished.
        `ignore_running`: bool
            if ignore_running is true, the task will be added to the task queue
            only if there is not a task which is running with same task_id
        `direction`: chihuo.Direction
            if direction is `Direction.Forward`, the task will be appended to the
            tail of queue, received at last. if direction is `Direction.Reverse`, the
            task will be appended to the head of queue, received at first.
        """

        if ignore_running:
            # Remove these tasks which is running
            pairs = tuple(pair for pair in pairs if pair[0] not in self._running_tasks)

        if finished:
            unfinished_pairs = []
            for task_id, task in pairs:
                v = await self._server.finished(task_id)
                if not v:
                    unfinished_pairs.append((task_id, task))
            pairs = tuple(unfinished_pairs)

        if not pairs:
            return

        # Serialize tasks
        pairs = tuple((task_id, serialize_json(task)) for task_id, task in pairs)

        if direction == Direction.Forward:
            await self._server.pushnx(*pairs)
        else:
            await self._server.pushnx_left(*pairs)

    async def task_finish(self, task_id: TaskId) -> None:
        """Set the task as finished

        If a task is set as finished, it CAN NOT be added to the backend at next time.
        """

        logger.info("%s: task_finish: %s", self._cls_name, task_id)

        await self._server.finish(task_id)

    async def task_unfinish(self, task_id: TaskId) -> None:
        """Set the task as unfinished

        If a task is set as unfinished, it CAN be added to the backend at next time.
        """

        logger.info("%s: task_unfinish: %s", self._cls_name, task_id)

        await self._server.unfinish(task_id)

    async def task_finished(self, task_id: TaskId) -> bool:
        """Check if the task is finished"""

        return await self._server.finished(task_id)

    async def task_exists(self, task_id: TaskId) -> bool:
        """Check if the task exists"""

        return await self._server.exists(task_id)

    def _release(self) -> None:
        """Release the semaphore"""

        self._semaphore.release()

    def length(self):
        """How many tasks are there"""

        return self._concurrency - self._semaphore._value

    async def sleep(self, second) -> None:
        await asyncio.sleep(second, loop=self._loop)

    def _run_(self):
        """The main function to run the factory"""

        logger.info("%s runs", self._cls_name)

        start = getattr(self, "start", None)
        if start and isinstance(start, types.MethodType):
            self._create_task(start(), task_type=TaskType.Start)

        self._create_task(self._task_loop(), task_type=TaskType.TaskLoop)
