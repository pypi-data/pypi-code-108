#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge sort algorithm, for a given order relation.

Adpated from https://www.geeksforgeeks.org/merge-sort/
"""

def sort(array, relation='__lt__'):
    
    if len(array) > 1:
         # Finding the mid of the array
        mid = len(array)//2
        # Dividing the array elements
        left_array = array[:mid]
        # into 2 halves
        right_array = array[mid:]
        # Sorting the first half
        sort(left_array, relation=relation)
        # Sorting the second half
        sort(right_array, relation=relation)
        i = j = k = 0
        # Copy data to temp arrays L[] and R[]
        while i < len(left_array) and j < len(right_array):
            if getattr(left_array[i], relation)(right_array[j]):
                array[k] = left_array[i]
                i += 1
            else:
                array[k] = right_array[j]
                j += 1
            k += 1
  
        # Checking if any element was left
        while i < len(left_array):
            array[k] = left_array[i]
            i += 1
            k += 1
  
        while j < len(right_array):
            array[k] = right_array[j]
            j += 1
            k += 1