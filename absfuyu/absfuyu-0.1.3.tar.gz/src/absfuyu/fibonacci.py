#!/usr/bin/env python
# coding: utf-8
"""
Fibonacci Module
----------------
"""


# Module level
##############################################################
__all__ = [
    "fibonacci", "fibonacci_list",
]



# Function
##############################################################

def fibonacci(number: int) -> int:
    """
    Summary
    -------
    Return a fibonacii number at the k-th position

    Parameters
    ----------
    number : int
        k-th position

    Returns
    -------
    int
        fibonacci number at the k-th position
    None
        Invalid value (k <= 0)
    """

    a = 0
    b = 1
    
    # number < 0
    if number < 0:
        return None
    
    # number = 0
    elif number == 0:
        return 0
    
    # number = 1
    elif number == 1:
        return b
    
    else:
        for _ in range(1, number):
            c = a+b
            a,b = b,c
        return b



def fibonacci_list(number: int):
    """
    Summary
    -------
    Return a fibonacii list from 0 to the k-th position

    Parameters
    ----------
    number : int
        k-th position

    Returns
    -------
    list[int]
        fibonacci number at the k-th position
    None
        Invalid value (k <= 0)
    """

    if number <= 0:
        return None
    
    fibLst = [0, 1]
    if number > 2:
        for i in range (2, number+1):
            fibLst.append(fibLst[i-1] + fibLst[i-2])
    return fibLst




if __name__ == "__main__":
    pass