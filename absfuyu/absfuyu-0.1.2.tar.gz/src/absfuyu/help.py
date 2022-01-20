#!/usr/bin/env python
# coding: utf-8


from absfuyu import sort as s
from absfuyu import version as v

__all__ = [
    "help", "version",
]

current_func = ["strDiv","strAna","isPrime", "isPerfect",
                "lsum", "randStrGen","help","srcMe","version"]

def printAlphabet(lst):
    data = s.alphabetAppear(lst)
    incre = data[1]
    for i in range(len(lst)):
        if i in incre:
            print("")
        if i == len(lst)-1:
            print(lst[i], end = " ")
        else:
            print(lst[i], end = "; ")

def help(page=1):
    if page == 1:
        print("""
            import absfuyu
            absfuyu.help()

            use code below to use all the functions
            from absfuyu import calculation
            from absfuyu import fibonacci
            from absfuyu import generator
            from absfuyu import sort
            from absfuyu import string
            from absfuyu import util

            page 1 of 2
            """)
    
    elif page == 2:
        print("List of function that can use in main module:")
        printAlphabet(current_func)
        print("\n")
        print("page 2 of 2")
        
    else:
        return -1

def version():
    return v.__version__