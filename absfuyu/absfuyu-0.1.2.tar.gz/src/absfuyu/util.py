#!/usr/bin/env python
# coding: utf-8

# utilities.py
# util.py

__all__ = [
    "toCelcius", "toFahrenheit", "unique_list",
    "isPangram","isPalindrome",
]

# Convert Fahrenheit to Celcius
def toCelcius(number,roundup=True):
    c_degree = (number-32)/1.8
    if roundup:
        return round(c_degree,2)
    else:
        return c_degree

# Convert Celcius to Fahrenheit
def toFahrenheit(number,roundup=True):
    f_degree = (number*1.8)+32
    if roundup:
        return round(f_degree,2)
    else:
        return f_degree

# Remove duplicates in list
def unique_list(your_list):
    return list(set(your_list))


def isPangram(text):
    alphabet = set("abcdefghijklmnopqrstuvwxyz")
    return not set(alphabet) - set(text.lower())


def isPalindrome(text):
    # A palindrome is a word, verse, or sentence 
    # or a number that reads the same backward or forward

    # Use string slicing [start:end:step]
    return text == text[::-1]