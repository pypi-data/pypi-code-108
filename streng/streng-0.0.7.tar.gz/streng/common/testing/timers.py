import time
from functools import wraps


def execution_timer(func):
    # from STONE.RIVER.ELEARNING.PYTHON.TOOLS.MODULES.AND.JSON-iLLiTERATE
    # video 00033 Decorators_and_Monkey_Patching_-_Part_2B.mp4
    @wraps(func)
    def time_wrapper(*args, **kwargs):
        begin_time = time.time()
        result = func(*args, **kwargs)
        complete_time = time.time()
        total_time = complete_time - begin_time
        print("The", func.__name__, "method completed in:", total_time)
        return result
    return time_wrapper

