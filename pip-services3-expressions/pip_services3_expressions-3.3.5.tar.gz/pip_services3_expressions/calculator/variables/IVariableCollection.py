# -*- coding: utf-8 -*-

from abc import ABC
from typing import List

from pip_services3_expressions.calculator.variables.IVariable import IVariable


class IVariableCollection(ABC):
    """
    Defines a variables list.
    """

    def add(self, variable: IVariable):
        """
        Adds a new variable to the collection.

        :param variable: a variable to be added.
        """

    def length(self) -> int:
        """
        Gets a number of variables stored in the collection.

        :return: return a number of stored variables.
        """

    def get(self, index: int) -> IVariable:
        """
        Get a variable by its index.

        :param index: a variable index.
        :return: a retrieved variable.
        """

    def get_all(self) -> List[IVariable]:
        """
        Get all variables stores in the collection

        :return: a list with variables.
        """

    def find_index_by_name(self, name: str) -> int:
        """
        Finds variable index in the list by it's name.

        :param name: The variable name to be found.
        :return: Variable index in the list or **-1** if variable was not found.
        """

    def find_by_name(self, name: str) -> IVariable:
        """
        Finds variable in the list by it's name.

        :param name: The variable name to be found.
        :return: A variable or **None** if function was not found.
        """

    def locate(self, name: str) -> IVariable:
        """
        Finds variable in the list or create a new one if variable was not found.

        :param name: The variable name to be found.
        :return: Found or created variable.
        """

    def remove(self, index: int):
        """
        Removes a variable by its index.

        :param index: a index of the variable to be removed.
        """

    def remove_by_name(self, name: str):
        """
        Removes variable by it's name.
        
        :param name: The variable name to be removed.
        """

    def clear(self):
        """
        Clears the collection.
        """

    def clear_values(self):
        """
        Clears all stored variables (assigns null values).
        """
