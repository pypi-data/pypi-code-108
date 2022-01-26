# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .StateValue import StateValue


class IStateStore(ABC):
    """
    Interface for state storages that are used to store and retrieve transaction states.
    """

    @abstractmethod
    def load(self, correlation_id: Optional[str], key: str) -> Any:
        """
        Loads state from the store using its key.
        If value is missing in the store it returns None.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param key: a unique state key.
        :return: the state value or `None` if value wasn't found.
        """

    @abstractmethod
    def load_bulk(self, correlation_id: Optional[str], keys: List[str]) -> List[StateValue]:
        """
        Loads an array of states from the store using their keys.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param keys: unique state keys.
        :return: an array with state values and their corresponding keys.
        """
        raise NotImplementedError('Method from interface definition')

    @abstractmethod
    def save(self, correlation_id: Optional[str], key: str, value: Any) -> Any:
        """
        Saves state into the store.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param key: a unique state key.
        :param value: a state value.
        :return: The state that was stored in the store.
        """
        raise NotImplementedError('Method from interface definition')

    @abstractmethod
    def delete(self, correlation_id: Optional[str], key: str) -> Any:
        """
        Deletes a state from the store by its key.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param key: a unique value key.
        :return: deleted item
        """
