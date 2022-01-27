#!/usr/bin/env python
# coding: utf-8
"""
Calculation Module
------------------
"""


# Module level
##############################################################
__all__ = [
    "isPrime", "isPerfect", "lsum", "lavg", "matsum",
    # "isPerfectLegacy",
]


# Library
##############################################################
import math
from typing import List, Union
# from typing import Literal for Python 3.8




# Define type
##############################################################
Number = Union[int, float]



# Function
##############################################################

def isPrime(number: int) -> bool:
    """
    Summary
    -------
    Check if the integer is a prime number or not

        A prime number is a natural number greater than 1
        that is not a product of two smaller natural numbers.
        A natural number greater than 1 that is not prime
        is called a composite number.

    Parameters
    ----------
    number : int
        an interger number

    Returns
    -------
    bool
        True if a prime number
    """
    
    if int(number) <= 1:
        return False
    for i in range(2,int(math.sqrt(number))+1):# divisor range
        if (number % i == 0):
            return False
    return True



def isPerfect(number: int) -> bool:
    """
    Summary
    -------
    Check if integer is perfect number

        Perfect number: a positive integer that is
        equal to the sum of its proper divisors.
        The smallest perfect number is 6, which is
        the sum of 1, 2, and 3.
        Other perfect numbers are 28, 496, and 8,128.

    Parameters
    ----------
    number : int
        an interger number

    Returns
    -------
    bool
        True if a perfect number
    """
    
    # list of known perfect number
    """
    perfect_number_index = [2,3,5,7,13,17,19,31]
    perfect_number = []
    for x in perfect_number_index:
        # a perfect number have a form of (2**(n-1))*((2**n)-1)
        perfect_number.append((2**(x-1))*((2**x)-1))
    """
    perfect_number = [
        6, 28, 496, 8_128,
        33_550_336, 8_589_869_056,
        137_438_691_328,
        2_305_843_008_139_952_128
    ]
    
    if int(number) in perfect_number:
        return True
    
    elif int(number) < perfect_number[-1]:
        return False
    
    else:
        # sum
        s = 1
        # add all divisors
        i = 2
        while i * i <= number:
            if number % i == 0:
                s += + i + number/i
            i += 1
        # s == number -> perfect
        return (True if s == number and number!=1 else False)


# Check if integer is perfect number - old
def isPerfectLegacy(number: int) -> bool:
    """
    A legacy function since the other runs faster
    """
    perfect_number = [6,28,496,8128,
                        33550336,8589869056,
                        137438691328,
                        2305843008139952128]
    if int(number) in perfect_number: return True
    elif int(number) < perfect_number[-1]: return False
    else:
        divisor = 1
        for i in range(2,int(number/2)+1):
            if (number%i == 0): divisor += i
        if number == divisor: return True
        else: return False
    



# Sum element of list
def lsum(lst: List[Number]) -> Number:
    """
    Summary
    -------
    Sum all the elements in a list

    Parameters
    ----------
    lst : list
        a list of number

    Returns
    -------
    Number
    """

    total = 0
    for x in lst:
        total += x
    return total


def lavg(lst: List[Number]) -> Number:
    """
    Summary
    -------
    Calculate the average value of
    all the elements in a list

    Parameters
    ----------
    lst : list
        a list of number

    Returns
    -------
    Number
    """
    return lsum(lst)/len(lst)





# Sum element of matrix
#MATRIXOPTION = Literal["all","row","col"] # Python 3.8
def matsum(
    matrix: List[Number],
    sum_opt: str = "all",
    #sum_opt: MATRIXOPTION = "all"
    ) -> Union[Number, list, None]:
    """
    Summary
    -------
    Sum the elements in a matrix

    Parameters
    ----------
    matrix : list
        2 dimension list
    
    sum_opt : str
        "all": sum all the elements (default)
        "row": sum all the elements in each row
        "col": sum all the elements in each column

    Returns
    -------
    int or float
        "all" option
    list
        other options
    None
        when invalid option
    """

    sum_option = ["all", "row", "col"]

    if sum_opt not in sum_option:
        return None

    row = len(matrix)
    col = len(matrix[0])

    if (sum_opt == "all"):
        mat_sum = 0
        for i in range(row):
            for j in range(col):
                mat_sum += matrix[i][j]
        return mat_sum

    elif (sum_opt == "row"):
        mat_sum_row = []
        for i in range(row):
            srow = 0
            for j in range(col):
                srow += matrix[i][j]
            mat_sum_row.append(srow)
        return mat_sum_row

    elif (sum_opt == "col"):
        mat_sum_col = []
        for i in range(col):
            scol = 0
            for j in range(row):
                scol += matrix[j][i]
            mat_sum_col.append(scol)
        return mat_sum_col
    else:
        return None





if __name__ == "__main__":
    pass