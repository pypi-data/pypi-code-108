import logging
import os

from nehushtan.logger.NehushtanLogger import NehushtanLogger
from tests.config import test_log_store


class FirstLoggerHolder:
    def __init__(self):
        self.logger = NehushtanLogger(
            'first',
            [
                NehushtanLogger.make_fixed_file_handler(os.path.join(test_log_store, 'first.log'))
            ]
        )


class SecondLoggerHolder:
    def __init__(self):
        self.logger = NehushtanLogger('first')


class ThirdLoggerHolder:
    def __init__(self):
        self.logger = NehushtanLogger(
            'first',
            [
                NehushtanLogger.make_stdout_handler(),
                NehushtanLogger.make_fixed_file_handler(os.path.join(test_log_store, 'third.log'))
            ]
        )


c1 = FirstLoggerHolder()
c1.logger.info('FIRST')

c2 = SecondLoggerHolder()
c2.logger.info('SECOND')

c1 = None
c2 = None

logging.getLogger('first').info('!', extra={"json_string": 'x'})
logging.getLogger('first').warning('!!', extra={"json_string": 'x'})
logging.getLogger('first').error('!!!', extra={"json_string": 'x'})

print(len(logging.getLogger('first').handlers))

c3 = ThirdLoggerHolder()
c3.logger.info('THIRD')

print(len(logging.getLogger('first').handlers))
