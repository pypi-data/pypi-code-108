import abc
import os
from queue import Queue
from threading import Thread
from typing import Generator, List, Tuple

from click import secho
from docker.models.containers import Container  # type: ignore

from tktl.core.config import settings


def set_verbosity(verbose):
    set_logger_verbosity(verbose)
    set_grpc_verbosity(verbose)


def set_grpc_verbosity(verbose):
    if verbose > 1:
        os.environ["GRPC_TRACE"] = "channel,http"
        os.environ["GRPC_VERBOSITY"] = "debug"
    else:
        os.environ.pop("GRPC_TRACE", None)
        os.environ.pop("GRPC_VERBOSITY", None)


def set_logger_verbosity(verbose):
    if verbose == 0:
        if settings.VERBOSE:
            verbose += 1
        elif settings.DEBUG:
            verbose += 2
    if verbose >= 1 or settings.VERBOSE:
        LOG.VERBOSE = True
    if verbose > 1 or settings.DEBUG:
        LOG.DEBUG = True


class Logger(abc.ABC):
    VERBOSE = False
    DEBUG = False

    @abc.abstractmethod
    def log(self, msg, *args, **kwargs):
        pass

    @abc.abstractmethod
    def warning(self, msg, *args, **kwargs):
        pass

    @abc.abstractmethod
    def error(self, msg, *args, **kwargs):
        pass

    def debug(self, msg, *args, **kwargs):
        pass

    def trace(self, msg, *args, **kwargs):
        pass


class MuteLogger(Logger):
    def log(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def trace(self, msg, *args, **kwargs):
        pass


class CliLogger(Logger):
    @staticmethod
    def _log(message, color=None, err=False):
        message = str(message)
        color = color if settings.USE_CONSOLE_COLORS else None
        secho(message, fg=color, err=err)

    def trace(self, message, color=None, err=False):
        if self.VERBOSE:
            self._log(message, color=color, err=err)

    def log(self, message, color=None, err=False):
        self._log(message, color=color, err=err)

    def error(self, message, *args, **kwargs):
        color = "red" if settings.USE_CONSOLE_COLORS else None
        self._log(message, color=color, err=True)

    def warning(self, message, *args, **kwargs):
        color = "yellow" if settings.USE_CONSOLE_COLORS else None
        self._log(message, color=color)

    def debug(self, message, *args, **kwargs):
        if self.DEBUG:
            self._log("DEBUG: {}".format(message))


def stream_blocking_logs(
    arrow_container: Container, rest_container: Container, color_logs: bool
) -> None:
    arrow_stream = blocking_generator(
        arrow_container.logs(stream=True), kind="arrow", color_logs=color_logs
    )
    rest_stream = blocking_generator(
        rest_container.logs(stream=True), kind="rest", color_logs=color_logs
    )
    streams = [arrow_stream, rest_stream]

    try:
        for msg, color in merge_blocking_iterators(streams):
            LOG.log(message=msg, color=color)
    except (KeyboardInterrupt, StopIteration, RuntimeError):
        LOG.log("Exiting...", color="red")
        rest_container.kill()
        arrow_container.kill()


def blocking_generator(
    container_logs: Generator[bytes, None, None],
    kind: str = "arrow",
    color_logs: bool = True,
) -> Generator[Tuple, None, None]:
    while True:
        try:
            line = container_logs.__next__()
        except StopIteration:
            return
        if kind == "arrow":
            yield f"> {line.decode()}".strip(), "bright_magenta" if color_logs else None
        else:
            yield f"> {line.decode()}".strip(), "bright_green" if color_logs else None
        if not line:
            return


def merge_blocking_iterators(
    generators: List[Generator[Tuple, None, None]]
) -> Generator[Tuple[str, str], None, None]:

    queue: Queue = Queue()

    def consume(_queue: Queue, stream: Generator) -> None:
        for i in stream:
            _queue.put(i)

    for generator in generators:
        thread = Thread(target=consume, args=(queue, generator))
        thread.start()

    while True:
        out = queue.get()
        if not out:
            return
        else:
            yield out


LOG = CliLogger()
MUTE_LOG = MuteLogger()
