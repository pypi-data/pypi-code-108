# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

from pip_services3_expressions.variants.Variant import Variant


class IVariable(ABC):
    """
    Defines a variable interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        :return: The variable name.
        """
        pass

    @property
    @abstractmethod
    def value(self) -> Variant:
        """
        :return: The variable value.
        """
        pass

    @value.setter
    @abstractmethod
    def value(self, value: Variant):
        """
        :param value: The variable value.
        """
        pass
