import sys
import time
import http
import dbt.main
import sentry_sdk
import typing as T
from . import dbt_version
from .types import Message
from .handlers import alert, monitor
from multiprocessing import cpu_count
from .parsers.formatter import Formatter
from dbt.contracts.results import RunExecutionResult
from .logger import GLOBAL_LOGGER as log, LogManager, AppendTags


# Hack to silence TCPServer logs
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


dbt.main.dbt.task.serve.SimpleHTTPRequestHandler = QuietHandler
# end hack to silence TCPServer logs


def run(command: T.List, tags: T.Dict):
    start = time.time()
    try:
        # Initialize stats and alerting
        alerting = alert.init()
        stats = monitor.init(common_tags=tags)

        @stats.timed("dbt.command.time", sample_rate=0.5)
        def run_command(cmd: T.List):
            return dbt.main.handle_and_check(cmd)

        res: RunExecutionResult
        res, success = run_command(command)
        for idx, result in enumerate(res.results):
            msg: Message = Formatter.format(result)
            stats.report(msg)
            alerting.alert(msg)
            with AppendTags({**msg.context, **tags}):
                log.log(
                    msg.level,
                    msg.message,
                    trace=msg.error,
                    context=msg.context,
                )

        return sys.exit(0 if success else 1)

    except Exception as err:
        log.error(err)
        sentry_sdk.capture_exception(err)
        return sys.exit(1)
    finally:
        stats.timing("dbt.command.time", time.time() - start)


def main(args: T.List):
    command = args[1:]
    tags = {
        "app": "dbt",
        "command": command[0],
        "version": dbt_version,
        "number_of_cores": cpu_count(),
    }

    log_manager = LogManager(tags=tags)
    log_manager.format_json()

    with log_manager.applicationbound():
        log.info("Starting dbt run")
        with AppendTags(tags).applicationbound():
            return run(command, tags)
