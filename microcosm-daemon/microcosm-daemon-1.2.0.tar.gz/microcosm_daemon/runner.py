"""
Execution abstraction.

"""
from multiprocessing import Pool
from signal import SIGINT, SIGTERM, signal


class SimpleRunner:
    """
    Run a daemon in the current process.

    """

    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.target.start(*self.args, **self.kwargs)


def _start(target, *args, **kwargs):
    target.start(*args, **kwargs)


class ProcessRunner:
    """
    Run a daemon in a different process.

    """

    def __init__(self, processes, target, *args, **kwargs):
        self.processes = processes
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.pool = None

        self.init_signal_handlers()

    def run(self):
        self.pool = self.process_pool()

        for _ in range(self.processes):
            self.pool.apply_async(_start, (self.target,) + self.args, self.kwargs)

        self.close()

    def init_signal_handlers(self):
        for signum in (SIGINT, SIGTERM):
            signal(signum, self.on_terminate)

    def process_pool(self):
        return Pool(processes=self.processes)

    def close(self, terminate=False):
        if self.pool is not None:
            if terminate:
                self.pool.terminate()
            else:
                self.pool.close()

            self.pool.join()

        exit(0)

    def on_terminate(self, signum, frame):
        self.close(terminate=True)
