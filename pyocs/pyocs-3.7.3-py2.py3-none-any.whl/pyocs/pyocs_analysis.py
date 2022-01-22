import time
import logging


class PyocsAnalysis:
    logging.basicConfig(level=logging.WARNING)  # 控制打印级别

    # 计算时间函数
    @staticmethod
    def print_run_time(func):
        def wrapper(*args, **kw):
            local_time = time.time()
            ret = func(*args, **kw)
            logging.info('current Function [%s] run time is %.2f' % (func.__name__, time.time() - local_time))
            return ret
        return wrapper
