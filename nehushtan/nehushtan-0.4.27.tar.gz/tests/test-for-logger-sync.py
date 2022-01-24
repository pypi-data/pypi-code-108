import logging
import threading
import time
from random import random

from nehushtan.logger.NehushtanLogger import NehushtanLogger
from tests.config import test_log_store

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
        )
    ),
    universal_log_level=logging.INFO,
    with_process_info=True,
    with_thread_info=True
)


def work(shovel_logger: NehushtanLogger, x):
    shovel_logger.info(f'I will sleep for {x} seconds...')
    time.sleep(x)
    shovel_logger.info('I woke up and die!')


thread_list = {}
for i in range(5):
    x = int(random() * 50)
    t = threading.Thread(target=work, args=(shovel_logger, x,))
    t.start()
    thread_list[i] = t

for i, t in thread_list.items():
    t.join()
    shovel_logger.info(f'joined {i}', threading.current_thread())

shovel_logger.info('awsl')
