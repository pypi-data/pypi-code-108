# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List

from .LambdaAction import LambdaAction


class ILambdaService(ABC):
    """
    An interface that allows to integrate lambda services into lambda function containers
    and connect their actions to the function calls.
    """

    @abstractmethod
    def get_actions(self) -> List[LambdaAction]:
        """
        Get all actions supported by the service.

        :return: an array with supported actions.
        """
