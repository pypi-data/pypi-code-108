# -*- coding: utf-8 -*-
"""
@author: Uwe Ziegenhagen, ziegenhagen@gmail.com
"""

class Classification:
    """
        Classification Item
    """

    def __init__(self):
        self.clear()

    def clear(self):
        """
            resets the classification
        """
        self.__label = None
        self.__description = None

    @property
    def label(self):
        """
            returns the label
        """
        return self.__label

    @label.setter
    def label(self, label):
        """
            sets the label
        """
        self.__label = label

    @property
    def description(self):
        """
           returns the classification
        """
        return self.__description

    @description.setter
    def description(self, description):
        """
            sets the classification
        """
        self.__description = description
