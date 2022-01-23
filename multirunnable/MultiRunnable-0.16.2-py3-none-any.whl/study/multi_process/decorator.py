from task import SharedTask

from typing import Callable, Any
from functools import wraps



class SharedFunc:

    def try_decorator(function: Callable):

        @wraps(function)
        def try_catch_code(*args, **kwargs) -> Any:
            try:
                result = function(*args, **kwargs)
            except Exception as e:
                print(e)
                return e
            else:
                print("Done function.")
                return result

        return try_catch_code


    def try_task_decorator(function: Callable):

        @wraps(function)
        def try_catch_code(self, task: SharedTask) -> Any:
            try:
                result = task.function(*task.func_args, **task.func_kwargs)
            except Exception as e:
                result = task.error_handler(e=e)
                print("Catch the exception in task.")
                print(e)
                return result
            else:
                result = task.done_handler(result=result)
                print("Done function.")
                return result

        return try_catch_code


    @classmethod
    def try_catch_mechanism(cls, function: Callable, *args, **kwargs) -> Any:
        try:
            result = function(*args, **kwargs)
        except Exception as e:
            print(e)
            return e
        else:
            print("Done function.")
            return result

