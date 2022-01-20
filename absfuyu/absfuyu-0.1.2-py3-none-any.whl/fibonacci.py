#!/usr/bin/env python
# coding: utf-8


__all__ = [
    "fibonacci","fibonacci_list",
]


# fib num at k-th position
def fibonacci(number):
    a = 0
    b = 1
    
    # number < 0
    if number < 0:
        return -1
    
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


# fib array from 0 to k-th position
def fibonacci_list(number):
    if number <= 0:
        return -1
    
    fibLst = [0, 1]
    if number > 2:
        for i in range (2, number+1):
            fibLst.append(fibLst[i-1] + fibLst[i-2])
    return fibLst
