from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable


class CustomQueryInterface(ABC):
    """Base class for basic operation create node"""

    @abstractmethod
    def custom_query(
            self,
            query: str,
            payload: Dict[str, Any],
            callback_func: Callable
    ) -> List[Dict[str, Any]]:
        """Execute string query based on parameters
        :param query: string query
        :param payload: dictionary binding to query
        :param callback_func: callback function to wrap result
        :return: List of dictionary
        """
        raise NotImplementedError
