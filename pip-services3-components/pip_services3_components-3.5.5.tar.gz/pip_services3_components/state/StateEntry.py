# -*- coding: utf-8 -*-
import datetime
from typing import Any


class StateEntry:
    """
    Data object to store state values with their keys used by :class:`MemoryStateStore <pip_services3_components.state.MemoryStateStore.MemoryStateStore>`
    """

    def __init__(self, key: str, value: Any):
        """
        Creates a new instance of the state entry and assigns its values.

        :param key: a unique key to locate the value.
        :param value: a value to be stored.
        """
        self._key = key
        self._value = value
        self._last_update_time = int(datetime.datetime.now().timestamp() * 1000)

    def get_key(self) -> str:
        """
        Gets the key to locate the state value.

        :return: the value key.
        """
        return self._key

    def get_value(self):
        """
        Gets the sstate value.

        :return: the value object.
        """
        return self._value

    def get_last_update_time(self) -> int:
        """
        Gets the last update time.

        :return: the timestamp when the value ware stored.
        """
        return self._last_update_time

    def set_value(self, value: Any):
        """
        Sets a new state value.

        :param value: a new cached value.
        """
        self._value = value
        self._last_update_time = int(datetime.datetime.now().timestamp() * 1000)
