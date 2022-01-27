#!/usr/bin/env python
# coding: utf-8
"""
Help Module
-----------
"""


# Module level
##############################################################
__all__ = [
    "help",
]




# Library
##############################################################
from absfuyu import sort as s
from absfuyu.version import __version__ as v






# Function
##############################################################

current_func = ["help","srcMe","version"]

def printAlphabet(lst: list):
    """
    Print item in list in alphabet order with line break
    """
    
    data = s.alphabetAppear(lst)
    incre = data[1]
    for i in range(len(lst)):
        if i in incre:
            print("")
        if i == len(lst)-1:
            print(lst[i], end = " ")
        else:
            print(lst[i], end = "; ")
    
    return None

def help(page: int = 1):
    """
    absfuyu builtin help page
    """
    
    if page == 1:
        print(f"""
            absfuyu version: {v}
            
            import absfuyu
            absfuyu.help()

            use code below to use all the functions
            from absfuyu import calculation
            from absfuyu import fibonacci
            from absfuyu import generator
            from absfuyu import obfuscator
            from absfuyu import sort
            from absfuyu import strings
            from absfuyu import util

            page 1 of 2
            """)
    
    elif page == 2:
        print("List of function that can use in main module:")
        printAlphabet(current_func)
        print("\n")
        print("page 2 of 2")
        
    else:
        return None




if __name__ == "__main__":
    pass






################################
    # to documenting
    """
    Summary
    -------
    
    Summary line.

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
    arg2 : str
        Description of arg2

    Returns
    -------
    int
        Description of return value

    """
################################