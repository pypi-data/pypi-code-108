# -*- coding: utf-8 -*-
"""
@author: Uwe Ziegenhagen, ziegenhagen@gmail.com
"""

class Account:
    """
        Account Item
    """

    def __init__(self):
        """
            creates an empty account
        """
        self.clear()

    def clear(self):
        """
            resets the account
        """
        self.__label = None
        self.__description = None
        self.__type = None
        self.__currency = None        

    @property
    def type(self):
        """
            returns the type of the account
        """
        return self.__type

    @type.setter
    def type(self, text):
        self.__type = text
        
    @property
    def label(self):
        """
            returns the label for the specific account
        """
        return self.__label

    @label.setter
    def label(self, label):
        self.__label = label

    @property
    def description(self):
        """
            returns the description for this specific account
        """
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description


    @property
    def currency(self):
        """
            returns the type of the account
        """
        return self.__currency

    @currency.setter
    def currency(self, text):
        self.__currency = text        
        