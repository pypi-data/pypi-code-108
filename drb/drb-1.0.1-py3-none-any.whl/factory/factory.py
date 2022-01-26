from __future__ import annotations

import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Optional, Union

from ..node import DrbNode
from ..exceptions import DrbException
from ..utils.url_node import UrlNode


class DrbFactory(ABC):
    """
    The Factory class defines the abstract class to be implemented in order to
    build drb nodes according to their physical form.
    The factory shall be aware of the implementations available to build nodes
    and build a relation between the physical data and its virtual node
    representation.
    """

    @abstractmethod
    def _create(self, node: DrbNode) -> DrbNode:
        """ Build a DrbNode thanks to this factory implementation.
        :param : The DrbNode of the physical data.
        :type node: DrbNode
        :return: a drb node representing the passed node
        :rtype: DrbNode
        :raises:
            DrbFactoryException: if the factory cannot build the node
        """
        raise NotImplementedError("Call impl method")

    def create(self, source: Union[DrbNode, str]) -> DrbNode:
        """ Build a DrbNode thanks to this factory implementation.
        :param source: the URI or the DrbNode of the physical data.
        :type source: str, DrbNode
        :return: a drb node representing the passed source
        :rtype: DrbNode
        :raises:
            DrbFactoryException: if the given source is not valid
        """
        if isinstance(source, DrbNode):
            return self._create(source)
        else:
            return self._create(UrlNode(source))


class FactoryLoader:
    """
    Manages loading and retrieving of factories defined in the Python context.
    """
    __instance = None
    __factories = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(FactoryLoader, cls).__new__(cls)
            cls.__factories = {}
        return cls.__instance

    @classmethod
    def __is_class(cls, class_name: str):
        return lambda obj: inspect.isclass(obj) and class_name == obj.__name__

    def get_factory(self, name: str) -> Optional[DrbFactory]:
        """
        Retrieves a factory by its name identifier.
        Parameters:
            name: factory name identifier
        Returns:
             DrbFactory - the requested factory, otherwise ``None``
        """
        return self.__factories.get(name, None)

    def load_factory(self, name: str, classpath: str) -> DrbFactory:
        """
        Loads and stocks a new factory.
        Parameters:
            name (str): factory name identifier
            classpath (str): factory classpath (package.module:Class)
        Returns:
            DrbFactory - the loaded factory
        Raises:
            DrbException - if the factory cannot be load correctly
        """
        # m -> module_name, c -> class_name
        m, c = tuple(classpath.split(':'))
        try:
            module = importlib.import_module(m)
        except ModuleNotFoundError:
            raise DrbException('Failed to load factory: ', m)

        # n -> object name, obj -> object
        for n, obj in inspect.getmembers(module, self.__is_class(c)):
            if obj != DrbFactory and issubclass(obj, DrbFactory):
                self.__factories[name] = obj()
                return self.__factories[name]
        raise DrbException(f'Invalid DRB factory: {name} -- {classpath}')

    def check_factories(self) -> None:
        for name, factory in self.__factories.items():
            if factory is None:
                raise DrbException(f'factory {name} defined but not found')
