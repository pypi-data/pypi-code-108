# -*- coding: utf-8 -*-
from typing import Any


class StateValue:

    def __init__(self, key: str = None, value: Any = None):
        """
        A data object that holds a retrieved state value with its key.
        :param key: A unique state key
        :param value: A stored state value;
        """
        self.key = key
        self.value = value
