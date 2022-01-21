import os
import sys
from typing import Any, Callable

import schedule


def job_name(job: schedule.Job) -> str:
    return qualified_func_name(job.job_func.func)


def qualified_func_name(func: Callable[..., Any]) -> str:
    if func.__module__ == "__main__":
        file_name = sys.modules[func.__module__].__file__
        assert file_name is not None
        module_name = os.path.basename(file_name).split(".")[0]
    else:
        module_name = func.__module__

    return f"{module_name}.{func.__name__}"
