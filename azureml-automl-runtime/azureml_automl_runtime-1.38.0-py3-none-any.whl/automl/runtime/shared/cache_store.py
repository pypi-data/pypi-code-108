# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for automl cache store."""
from typing import Any, Callable, cast, Dict, Iterable, Iterator, Optional, Tuple

from abc import ABC, abstractmethod
import logging
import sys  # noqa F401 # dynamically evaluated to get caller
import time

from azureml.automl.core.shared import logging_utilities

logger = logging.getLogger(__name__)


class CacheStore(ABC):
    """ABC for cache store."""

    def __init__(self,
                 max_retries: int = 3) -> None:
        """
        Cache store constructor.

        :param max_retries: max retries to get/put from/to store
        """
        self.cache_items = {}  # type: Dict[Any, Any]
        self.max_retries = max_retries

    def __getstate__(self) -> Dict[str, Optional[Any]]:
        """
        Get this cache store's state, removing unserializable objects in the process.

        :return: a dict containing serializable state.
        """
        return {'cache_items': self.cache_items,
                'max_retries': self.max_retries}

    def __setstate__(self, state: Dict[str, Optional[Any]]) -> None:
        """
        Deserialize this cache store's state, using the default logger.

        :param state: dictionary containing object state
        :type state: dict
        """
        self.cache_items = cast(Dict[Any, Any], state['cache_items'])
        self.max_retries = cast(int, state['max_retries'])

    @abstractmethod
    def load(self):
        """Load - abstract method."""
        pass

    @abstractmethod
    def unload(self):
        """Unload - abstract method."""
        pass

    def add(self, keys: Iterable[str], values: Iterable[Any]) -> None:
        """Add to store.

        :param keys: store key
        :param values: store value
        """
        for k, v in zip(keys, values):
            self.cache_items[k] = v

    def get(self, keys: Iterable[str], default: Optional[Any] = None) -> Dict[Any, Optional[Any]]:
        """
        Get value from store.

        :param default: default value
        :param keys: store keys
        :return: values
        """
        return {k: self.cache_items.get(k, default) for k in keys}

    def set(self, key: str, value: Any) -> None:
        """
        Set value to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key: str) -> None:
        """
        Remove from store.

        :param key: store key
        """
        obj = self.cache_items.pop(key)
        del obj

    def remove_all(self) -> None:
        """Remove all entry from store."""
        for k, v in self.cache_items.items():
            del v

        self.cache_items.clear()

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """
        Store iterator.

        :return: cache items
        """
        return iter(self.cache_items.items())

    @staticmethod
    def _function_with_retry(fn: 'Callable[..., Optional[Any]]',
                             max_retries: int,
                             *args: Any,
                             **kwargs: Any) -> Optional[Any]:
        """
        Call function with retry capability.

        :param fn: function to be executed
        :param max_retries: number of retries
        :param args: args
        :param kwargs: kwargs
        :return: Exception if failure, otherwise returns value from function call
        """
        backoff = 2
        retry_count = 0
        ex = None
        while retry_count < max_retries:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.warning("CacheStore: Execution failed.")
                ex = e
                time.sleep(backoff)
                backoff *= 2
            finally:
                retry_count += 1

        error_raised = cast(BaseException, ex)
        raise error_raised.with_traceback(error_raised.__traceback__)

    # Need to disable type checking because ContextManager is not available in typing before Python 3.5.4
    def log_activity(self, custom_dimensions: Optional[Dict[str, Any]] = None) -> Any:
        """
        Log activity collects the execution latency.

        :param custom_dimensions: custom telemetry dimensions
        :return: log activity
        """
        get_frame_expr = 'sys._getframe({}).f_code.co_name'
        caller = eval(get_frame_expr.format(2))
        telemetry_values = dict()
        telemetry_values['caller'] = caller

        if custom_dimensions is not None:
            telemetry_values.update(custom_dimensions)

        return logging_utilities.log_activity(
            logger=logger, activity_name=caller, custom_dimensions=telemetry_values)
