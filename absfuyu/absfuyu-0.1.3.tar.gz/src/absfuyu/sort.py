#!/usr/bin/env python
# coding: utf-8
"""
Sort Module
-----------
"""


# Module level
##############################################################
__all__ = [
    "selection_sort","insertion_sort",
    #"alphabetAppear",
]




# Library
##############################################################
from typing import Dict, List, Union






# Function
##############################################################

def selection_sort(lst: list, reverse: bool = False) -> list:
    """
    Summary
    -------
    Sort the list with selection sort (bubble sort) algorithm
 
    Parameters
    ----------
    lst : list
        list that want to be sorted
    
    reverse : bool
        if True: sort in descending order
        if False: sort in ascending order
        (default: False)

    Returns
    -------
    list
        sorted list
    """

    if reverse: # descending order
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                if lst[i] < lst[j]:
                    lst[i], lst[j] = lst[j], lst[i]
        return lst
        
    else: # ascending order
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                if lst[i] > lst[j]:
                    lst[i], lst[j] = lst[j], lst[i]
        return lst



def insertion_sort(lst: list) -> list:
    """
    Summary
    -------
    Sort the list with insertion sort algorithm
 
    Parameters
    ----------
    lst : list
        list that want to be sorted
    
    Returns
    -------
    list
        sorted list (ascending order)
    """

    for i in range (1,len(lst)):
        key = lst[i]
        j = i-1
        while j>=0 and key < lst[j]:
            lst[j+1] = lst[j]
            j -= 1
        lst[j+1] = key
    return lst




def alphabetAppear(lst: list,
    ) -> List[Union[Dict[str, int],List[int]]]:
    """
    Summary
    -------
    Make a dict that show the frequency of
    item name's first character in list
    in alphabet order
    
    For example:

    >>> ["apple","bee","book"]

    freq = {"a": 1, "b": 2}
 
    Parameters
    ----------
    lst : list
        list that want to be analyzed
    
    Returns
    -------
    list
        analyzed list (list[0])
        apperance incremental value index (list[1])
    """

    al_char = [x[0] for x in selection_sort(lst)]
    times_appear = dict()
    for x in al_char:
        if x in times_appear:
            times_appear[x] += 1
        else:
            times_appear[x] = 1
    
    times_appear_increment = []
    total = 0
    for x in times_appear.values():
        total += x
        times_appear_increment.append(total)

    # first item is character frequency
    # second item is incremental index list
    return [times_appear,times_appear_increment]





if __name__ == "__main__":
    pass