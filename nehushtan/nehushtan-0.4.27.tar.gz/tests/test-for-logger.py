import logging

from nehushtan.logger.NehushtanLogger import NehushtanLogger
from tests.config import test_log_store


class TestFilter(logging.Filter):
    def filter(self, record):
        print('filtering', record)
        print(f"record.levelno={record.levelno}")
        print(f"record.name={record.name}")
        print(f"record.thread={record.thread}")
        print(f"record.threadName={record.threadName}")
        print(f"record.message={record.message}")
        print(f"record.args={record.args}")
        print(f"record.asctime={record.asctime}")
        print(f"record.created={record.created}")
        print(f"record.exc_info={record.exc_info}")
        print(f"record.exc_text={record.exc_text}")
        print(f"record.filename={record.filename}")
        print(f"record.funcName={record.funcName}")
        print(f"record.lineno={record.lineno}")
        print(f"record.msecs={record.msecs}")
        print(f"record.msg={record.msg}")
        print(f"record.pathname={record.pathname}")
        print(f"record.process={record.process}")
        print(f"record.processName={record.processName}")
        print(f"record.threadName={record.threadName}")
        print(f"record.relativeCreated={record.relativeCreated}")
        print(f"record.__dict__={record.__dict__}")
        return True


filtering_handler = NehushtanLogger.make_fixed_file_handler(
    file_name=test_log_store + "/filtering.log",
)
filtering_handler.addFilter(TestFilter())

shovel_logger = NehushtanLogger(
    logger_name="runner",
    handlers=(
        NehushtanLogger.make_stdout_handler(),
        NehushtanLogger.make_stderr_handler(),
        NehushtanLogger.make_fixed_file_handler(
            file_name=test_log_store + "/fixed.log"
        ),
        NehushtanLogger.make_timed_rotating_file_handler(
            file_name=test_log_store + "/rotating.log"
        ),
        filtering_handler
    ),
    universal_log_level=logging.INFO
)

shovel_logger.debug('世界非常和平')
shovel_logger.info('世界还算凑合', "Guhehe")
shovel_logger.warning('世界有点问题', {"log_path": test_log_store})
shovel_logger.error('世界打起来了', shovel_logger)
shovel_logger.critical('世界马上灭亡', [3, 2, 1, {0: [1, 2, 3, {4: "!"}]}])

try:
    x = 5 / 0
except Exception as e:
    shovel_logger.exception("咕", e)
