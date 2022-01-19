import asyncio
import os
import threading

RUN_ASYNC_IN_THREAD_FLAG = "QM_SDK_RUN_ASYNC_IN_THREAD"


def run_async(coro):
    run_in_thread = os.environ.get(RUN_ASYNC_IN_THREAD_FLAG, None)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running() or run_in_thread is not None:
        thread = RunThread(coro)
        thread.start()
        thread.join()
        return thread.result
    else:
        return asyncio.run(coro)


class RunThread(threading.Thread):
    def __init__(self, func):
        self.func = func
        self.result = None
        super().__init__()

    def run(self):
        self.result = asyncio.run(self.func)
