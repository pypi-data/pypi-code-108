# -*- coding: utf-8 -*-
import copy
from typing import List

from pip_services3_expressions.calculator.variables.IVariable import IVariable
from pip_services3_expressions.calculator.variables.IVariableCollection import IVariableCollection
from pip_services3_expressions.calculator.variables.Variable import Variable
from pip_services3_expressions.variants.Variant import Variant


class VariableCollection(IVariableCollection):
    """
    Implements a variables list.
    """

    def __init__(self):
        super(VariableCollection, self).__init__()
        self.__variables: List[IVariable] = []

    def add(self, variable: IVariable):
        """
        Adds a new variable to the collection.

        :param variable: a variable to be added.
        """
        if variable is None:
            raise Exception("Variable cannot be null")
        self.__variables.append(variable)

    @property
    def length(self) -> int:
        """
        Gets a number of variables stored in the collection.

        :return: a number of stored variables.
        """
        return len(self.__variables)

    def get(self, index: int) -> IVariable:
        """
        Get a variable by its index.

        :param index: a variable index.
        :return: a retrieved variable.
        """
        return self.__variables[index]

    def get_all(self) -> List[IVariable]:
        """
        Get all variables stores in the collection
        
        :return: a list with variables.
        """
        result = copy.deepcopy(self.__variables)
        return result

    def find_index_by_name(self, name: str) -> int:
        """
        Finds variable index in the list by it's name.

        :param name: The variable name to be found.
        :return: Variable index in the list or **-1** if variable was not found.
        """
        name = name.upper()
        for i in range(len(self.__variables)):
            var_name = self.__variables[i].name.upper()
            if var_name == name:
                return i
        return -1

    def find_by_name(self, name: str) -> IVariable:
        """
        Finds variable in the list by it's name.

        :param name: The variable name to be found.
        :return: A variable or **None** if function was not found.
        """
        index = self.find_index_by_name(name)
        return None if index < 0 else self.__variables[index]

    def locate(self, name: str) -> IVariable:
        """
        Finds variable in the list or create a new one if variable was not found.
        
        :param name: The variable name to be found.
        :return: Found or created variable.
        """
        v = self.find_by_name(name)
        if v is None:
            v = Variable(name)
            self.add(v)

        return v

    def remove(self, index: int):
        """
        Removes a variable by its index.

        :param index: a index of the variable to be removed.
        """
        self.__variables.pop(index)

    def remove_by_name(self, name: str):
        """
        Removes variable by it's name.

        :param name: The variable name to be removed.
        """
        index = self.find_index_by_name(name)
        if index >= 0:
            self.remove(index)

    def clear(self):
        """
        Clears the collection.
        """
        self.__variables = []

    def clear_values(self):
        """
        Clears all stored variables (assigns null values).
        """
        for v in self.__variables:
            v.value = Variant()
