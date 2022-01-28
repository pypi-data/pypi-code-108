import os
import traceback
import logging
import datetime
from typing import Callable, Union, Any, Optional

from .utils import get_list_values, get_values, _check_lambda_args
from .client import ManageClient

__all__ = ('event', 'list_value_event')


logger = logging.getLogger('manage_app_client')
logger.setLevel(logging.DEBUG)


class __Executor(object):
    def __init__(
        self,
        function: Callable,
        keys: Optional[Union[list, str, None]] = None,
        list_value: Optional[str] = None,
        iter_key: Optional[str] = None,
        description: Optional[str] = None,
        *args,
        **kwargs
    ):
        self.function = function
        self.keys = keys
        self.list_value = list_value
        self.iter_key = iter_key
        self.args = args
        self.kwargs = kwargs
        self.description = description

    def execution(self, definition: dict, timestamp: str, *args, **kwargs) -> Any:
        init_kwargs = {
            "system_id": os.environ.get("MANAGE_SYSTEM_ID", ""),
            "system_url": os.environ.get("MANAGE_SYSTEM_URL", ""),
            "token": os.environ.get("MANAGE_SYSTEM_TOKEN", ""),
            "debug": os.environ.get("MANAGE_SYSTEM_DEBUG", '0'),
        }
        client = ManageClient(**init_kwargs)
        client.push_event(
            definition=definition,
            start_time=timestamp,
            status=False,
            description=self.description,
        )
        # print(pushed)
        try:
            args = _check_lambda_args(args)
            if args or kwargs:
                func_result = self.function(*args, **kwargs)
            else:
                func_result = self.function()
        except Exception as exc_description:
            t = traceback.format_exc()
            t = t.replace("func_result = function", self.function.__name__)
            logger.warning('exception - %s, traceback: %s', exc_description, t)
            return client.log_exception(
                definition=definition, description=str(exc_description), trb=t
            )
        client.push_event(
            definition=definition,
            start_time=timestamp,
            status=True,
            description=self.description,
        )
        return func_result

    def push(self, list_: bool = False, *args, **kwargs):
        definition = {}
        var_names = self.function.__code__.co_varnames
        try:
            if self.keys is not None and not list_:
                values = get_values(self.keys, var_names, *args, **kwargs)  # type: ignore
                definition = values["definition"]
                if not definition:
                    definition = {self.function.__name__: self.function.__name__}
            elif list_:
                list_values = get_list_values(
                    self.keys,  # type: ignore
                    self.list_value,  # type: ignore
                    self.iter_key,  # type: ignore
                    var_names,  # type: ignore
                    *args,
                    **kwargs
                )
                definition = list_values["definition"]
            else:
                definition = {self.function.__name__: self.function.__name__}

        except IndexError:
            pass
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.execution(definition, timestamp, *args, **kwargs)


def event(
    keys: Optional[Union[list, str, None]] = None, description: Optional[str] = None
):
    def decorator(function: Callable, *args, **kwargs):
        def push_function_results(*args, **kwargs):
            executor = __Executor(function=function, keys=keys, description=description)
            return executor.push(False, *args, **kwargs)

        return push_function_results

    return decorator


def list_value_event(
    keys: Union[str, list],
    list_value: str,
    iter_key: str,
    description: Optional[str] = None,
) -> Any:
    def decorator(function, *args, **kwargs):
        def push_function_results(*args, **kwargs):
            executor = __Executor(
                function=function,
                keys=keys,
                list_value=list_value,
                iter_key=iter_key,
                description=description,
            )
            return executor.push(True, *args, **kwargs)

        return push_function_results

    return decorator
