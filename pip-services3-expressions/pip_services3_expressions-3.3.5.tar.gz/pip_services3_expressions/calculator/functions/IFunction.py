# -*- coding: utf-8 -*-

from abc import ABC
from typing import List

from pip_services3_expressions.variants.IVariantOperations import IVariantOperations
from pip_services3_expressions.variants.Variant import Variant


class IFunction(ABC):
    """
    Defines an interface for expression function.
    """

    # The function name.
    name: str

    def calculate(self, params: List[Variant], variant_operations: IVariantOperations) -> Variant:
        """
        The function calculation method.

        :param params: The stack to get function parameters and place
        :param variant_operations: Variants operations manager.
        :return: the function result.
        """
