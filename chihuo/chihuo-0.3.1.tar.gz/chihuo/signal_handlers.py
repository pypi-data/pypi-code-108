import logging
import asyncio
import functools
import signal
from typing import Iterable

from .common import TaskType, Direction
from .loop import ChihuoLoop

logger = logging.getLogger(__name__)

IS_ON_TERM = False
IS_ON_INT = False


async def cancel_all_running_tasks(loop, factories: Iterable[ChihuoLoop] = []) -> None:
    """Cancel all running tasks, then send these tasks back to backend"""

    while True:
        # Cancel all running async tasks in the loop
        tasks = [
            t for t in asyncio.all_tasks(loop) if t.get_name() != TaskType.Final.value
        ]

        logger.info("all tasks number: %s", len(tasks))

        task_loop = [t for t in tasks if t.get_name() == TaskType.TaskLoop.value]
        needed_cancel = [t for t in tasks if t.get_name() != TaskType.TaskLoop.value]

        for task in needed_cancel:
            task.cancel()

        if len(needed_cancel) == 0:
            # Finally, cancel the `ChihuoLoop._task_loop`
            if len(task_loop) == 0:
                break
            else:
                for task in task_loop:
                    task.cancel()

        await asyncio.sleep(1)

    await sendback_tasks(factories)

    loop.stop()


async def sendback_tasks(factories: Iterable[ChihuoLoop]) -> None:
    """Send all tasks in `ChihuoLoop._running_tasks` to backend"""

    for factory in factories:
        factory_name = factory.__class__.__name__
        pairs = list(factory._running_tasks.items())
        logger.info("%s: sendback tasks", factory_name)
        logger.info("%s: sendback_task: tasks: %s", factory_name, pairs)

        for pair in pairs:
            await factory.add_task(pair, direction=Direction.Reverse)

        logger.info("%s: sendback_task has done", factory_name)


def handle_stop_and_send(
    signum,
    frame,
    factories: Iterable[ChihuoLoop] = [],
    loop: asyncio.AbstractEventLoop = None,
) -> None:
    """The handler of INT and TERM signals

    First, we set all factories to be stoped at next event loop.
    Then, we cancel all running tasks and send them to backend.
    """

    assert loop, "The Event Loop can not be None"

    logger.info("handle signal %s: handle_stop_and_send", signum)

    global IS_ON_TERM
    global IS_ON_INT
    if IS_ON_TERM or IS_ON_INT:
        return

    # Stop the factory task loop
    for factory in factories:
        factory.stop = True

    # Spawn the final task
    final_task = cancel_all_running_tasks(loop, factories)
    loop.create_task(final_task, name=TaskType.Final.value)

    IS_ON_INT = True


def set_signal_handlers(
    factories: Iterable[ChihuoLoop], loop: asyncio.AbstractEventLoop
) -> None:
    """Set signal handlers for `factories`"""

    signal.signal(
        signal.SIGTERM,
        functools.partial(handle_stop_and_send, factories=factories, loop=loop),
        # functools.partial(wait_for_tasks, factories=factories, loop=loop),
    )
    signal.signal(
        signal.SIGINT,
        functools.partial(handle_stop_and_send, factories=factories, loop=loop),
    )
