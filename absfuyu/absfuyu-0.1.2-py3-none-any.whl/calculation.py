#!/usr/bin/env python
# coding: utf-8


import math

__all__ = [
    "isPrime", "isPerfect", "lsum",
    # "matsum",
    # "isPerfectLegacy",
]




# Check if the integer is a prime number
def isPrime(n):
    if int(n) <= 1:
        return False
    for i in range(2,int(math.sqrt(n))+1):# divisor range
        if (n % i == 0):
            return False
    return True


# Check if integer is perfect number
def isPerfect(number):
    # list of known perfect number
    """
    perfect_number_index = [2,3,5,7,13,17,19,31]
    perfect_number = []
    for x in perfect_number_index:
        # a perfect number have a form of (2**(n-1))*((2**n)-1)
        perfect_number.append((2**(x-1))*((2**x)-1))
    """
    perfect_number = [6,28,496,8128,
                        33550336,8589869056,
                        137438691328,
                        2305843008139952128]
    
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
def isPerfectLegacy(number):
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
def lsum(lst):
    sum = 0
    for x in lst:
        sum += x
    return sum



# Sum element of matrix
def matsum(matrix,sum_opt=0):
    sum_option = {
        0:"all",
        1:"row",
        2:"col"
    }

    if sum_opt not in sum_option:
        return -1

    row = len(matrix)
    col = len(matrix[0])

    if (sum_opt == 0):
        mat_sum = 0
        for i in range(row):
            for j in range(col):
                mat_sum += matrix[i][j]
        return mat_sum

    elif (sum_opt == 1):
        mat_sum_row = []
        for i in range(row):
            srow = 0
            for j in range(col):
                srow += matrix[i][j]
            mat_sum_row.append(srow)
        return mat_sum_row

    else:
        mat_sum_col = []
        for i in range(col):
            scol = 0
            for j in range(row):
                scol += matrix[j][i]
            mat_sum_col.append(scol)
        return mat_sum_col


