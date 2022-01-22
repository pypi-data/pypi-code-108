import os
import sys
import time

# PATH = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)), "winhye_common")
PATH2 = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

# sys.path.append(PATH)
sys.path.append(PATH2)
print(PATH2)

from src.winhye_common.winhye_logger import logging as logging


def log_test():
    logger = logging.getLogger()
    for i in range(10000):
        logger.info("1111111111111111")
        logger.debug("222222222222222222")
        time.sleep(1)


def log_test2():
    logger = logging.getLogger()
    logger.report("123456")


def log_test3():
    logger = logging.getLogger()
    logger.error('123')
    import datetime
    print(datetime.datetime.now())


if __name__ == '__main__':
    log_test3()
