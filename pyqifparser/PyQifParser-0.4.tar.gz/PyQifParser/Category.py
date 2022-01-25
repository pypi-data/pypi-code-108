# -*- coding: utf-8 -*-
"""
@author: Uwe Ziegenhagen, ziegenhagen@gmail.com
"""

class Category:
    """
        Category Item
    """

    def __init__(self):
        self.clear()

    def clear(self):
        """
            Resets the category
        """
        self.__label = None
        self.__parent = None
        self.__type = None
        self.__description = None

    @property
    def label(self):
        """
            returns the category label
        """
        return self.__label

    @label.setter
    def label(self, label):
        """
            sets the category label
        """
        self.__label = label

    @property
    def parent(self):
        """
            returns the parent of this category
        """
        return self.__parent

    @parent.setter
    def parent(self, parent):
        """
            sets the parent category for this category
        """
        self.__parent = parent

    @property
    def description(self):
        """
            returns the description for this category
        """
        return self.__description

    @description.setter
    def description(self, description):
        """
            sets the description for this category
        """
        self.__description = description

    @property
    def type(self):
        """
            Returns the Type for this category
        """
        return self.__type

    @type.setter
    def type(self, type):
        """
            sets the type of this category
        """
        self.__type = type



if __name__ == "__main__":
    """
        Some test code
    """
    c = Category()
    c.label = 'General Expense'
    c.type = "E"
    c.parent = "Expense"
    print(c.label, c.type, c.parent)
    