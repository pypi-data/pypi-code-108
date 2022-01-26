# -*- coding: utf-8 -*-

import copy
from typing import List

from pip_services3_expressions.calculator.functions.IFunction import IFunction
from pip_services3_expressions.calculator.functions.IFunctionCollection import IFunctionCollection


class FunctionCollection(IFunctionCollection):
    """
    Implements a functions list.
    """

    def __init__(self):
        super(FunctionCollection, self).__init__()
        self.__functions: List[IFunction] = []

    def add(self, func: IFunction):
        """
        Adds a new function to the collection.
        
        :param func: a function to be added.
        """
        if func is None:
            raise Exception('Func cannot be None')
        self.__functions.append(func)

    @property
    def length(self) -> int:
        """
        Gets a number of functions stored in the collection.

        :return: a number of stored functions.
        """
        return len(self.__functions)

    def get(self, index: int) -> IFunction:
        """
        Get a function by its index.

        :param index: a function index.
        :return: a retrieved function.
        """
        return self.__functions[index]

    def get_all(self) -> List[IFunction]:
        """
        Get all functions stores in the collection

        :return: a list with functions.
        """
        result = copy.deepcopy(self.__functions)
        return result

    def find_index_by_name(self, name: str) -> int:
        """
        Finds function index in the list by it's name.

        :param name: The function name to be found.
        :return: Function index in the list or **-1** if function was not found.
        """
        name = name.upper()
        for i in range(len(self.__functions)):
            var_name = self.__functions[i].name.upper()
            if var_name == name:
                return i
        return -1

    def find_by_name(self, name: str) -> IFunction:
        """
        Finds function in the list by it's name.

        :param name: The function name to be found.
        :return: A function or **None** if function was not found.
        """
        index = self.find_index_by_name(name)
        return self.__functions[index] if index >= 0 else None

    def remove(self, index: int):
        """
        Removes a function by its index.

        :param index: a index of the function to be removed.
        """
        self.__functions.pop(index)

    def remove_by_name(self, name: str):
        """
        Removes function by it's name.

        :param name: The function name to be removed.
        """
        index = self.find_index_by_name(name)
        if index >= 0:
            self.remove(index)

    def clear(self):
        """
        Clears the collection.
        """
        self.__functions = []
