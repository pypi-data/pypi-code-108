#!/usr/bin/env python
# coding: utf-8
"""
Utilities Module
----------------
"""




# Module level
##############################################################
__all__ = [
    "toCelcius", "toFahrenheit", "unique_list",
]





# Library
##############################################################
from typing import Any, List, Union






# Define type
##############################################################
Number = Union[int, float]





# Function
##############################################################

def toCelcius(
        number: Number,
        roundup: bool = True
    ) -> Number:
    """
    Summary
    -------
    Convert Fahrenheit to Celcius

    Parameters
    ----------
    number : Number
        F degree
    
    roundup : bool
        round the figure to .2f if True
        (default: True)

    Returns
    -------
    Number
        C degree
    """

    c_degree = (number-32)/1.8
    if roundup:
        return round(c_degree,2)
    else:
        return c_degree



def toFahrenheit(
        number: Number,
        roundup: bool = True
    ) -> Number:
    """
    Summary
    -------
    Convert Celcius to Fahrenheit

    Parameters
    ----------
    number : Number
        C degree
    
    roundup : bool
        round the figure to .2f if True
        (default: True)

    Returns
    -------
    Number
        F degree
    """

    f_degree = (number*1.8)+32
    if roundup:
        return round(f_degree,2)
    else:
        return f_degree



def unique_list(lst: list) -> List[Any]:
    """
    Summary
    -------
    Remove duplicate items in list

    Parameters
    ----------
    lst : list
        List that needs "cleaning"

    Returns
    -------
    list
        list that has no duplicates
    """
    return list(set(lst))





if __name__ == "__main__":
    pass