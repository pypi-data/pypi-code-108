#!/usr/bin/env python
# coding: utf-8
"""
Generator Module
----------------
"""


# Module level
##############################################################
__all__ = [
    "randStrGen", "strGen", "checkDigitGen",
]




# Library
##############################################################
import string
import random
from typing import Union






# Function
##############################################################

def randStrGen(
        size: int = 8,
        times: int = 1,
        char: str = "default",
        string_type_if_1: bool = False
    ) -> Union[list, str, None]:
    """
    Summary
    -------
    Generate a list of random string (Random string generator)

    Parameters
    ----------
    size : int
        length of each string in list
    
    times : int
        how many random string generated

    char : str
        "default": character in [a-zA-Z0-9] (default)
        "alphabet": character in [a-zA-Z]
        "full": character in [a-zA-Z0-9] + special characters
        "uppercase": character in [A-Z]
        "lowercase": character in [a-z]
        "digit": character in [0-9]
        "special": character in [!@#$%^&*()_+=-]
        "all": character in every printable character
    
    string_type_if_1 : bool
        return a str type result if times == 1
        (default: False)

    Returns
    -------
    list
        list of random string generated
    str
        when string_type_if_1 is True
    None
        when invalid option
    """

    character_option = {
        "default": string.ascii_letters + string.digits,
        "alphabet": string.ascii_letters,
        "full": string.ascii_letters + string.digits + string.punctuation,
        "uppercase": string.ascii_uppercase,
        "lowercase": string.ascii_lowercase,
        "digit": string.digits,
        "special": string.punctuation,
        "all": string.printable
    }

    if char not in character_option:
        return None

    unique_string = []
    count = 0
    char_lst = character_option[char]

    while (count < times):
        s = ''.join(random.choice(char_lst) for _ in range(size))
        if s not in unique_string:
            unique_string.append(s)
            count += 1
    
    if string_type_if_1 and times == 1:
        return unique_string[0]
    else:
        return unique_string




def strGen(
        from_string: str = "",
        size: int = 8,
        times:int = 1,
        string_type_if_1: bool = False
    ) -> Union[list, str, None]:
    """
    Summary
    -------
    Generate a list of random string from a given string

    Parameters
    ----------
    from_string : str
        base string

    size : int
        length of each string in list
    
    times : int
        how many random string generated
    
    string_type_if_1 : bool
        return a str type result if times == 1
        (default: False)

    Returns
    -------
    list
        list of random string generated
    str
        when string_type_if_1 is True
    None
        when invalid option
    """

    if from_string == "":
        return None

    unique_string = []
    count = 0

    while (count < times):
        s = ''.join(random.choice(from_string) for _ in range(size))
        if s not in unique_string:
            unique_string.append(s)
            count += 1

    if string_type_if_1 and times == 1:
        return unique_string[0]
    else:
        return unique_string




def checkDigitGen(number: int) -> int:
    """
    Summary
    -------
    Check digit generator
    
        "A check digit is a form of redundancy check used for
        error detection on identification numbers, such as
        bank account numbers, which are used in an application
        where they will at least sometimes be input manually.
        It is analogous to a binary parity bit used to
        check for errors in computer-generated data.
        It consists of one or more digits (or letters) computed
        by an algorithm from the other digits (or letters) in the sequence input.

        With a check digit, one can detect simple errors in
        the input of a series of characters (usually digits)
        such as a single mistyped digit or some permutations
        of two successive digits." (Wikipedia)
        
        This function use Luhn's algorithm to calculate

    Parameters
    ----------
    number : int
        base number to calculate check digit

    Returns
    -------
    int
        check digit
    """

    # turn into list then reverse the order
    num = list(str(number))[::-1]
    sum = 0
    for i in range(len(num)):
        # convert back into integer
        num[i] = int(num[i])
        if i%2 == 0:
            # double value of the even-th digit
            num[i] *= 2
            # sum the character of digit if it's >= 10
            if num[i] >= 10:
                num[i] -= 9
        sum += num[i]
    return ((10-(sum%10))%10)




if __name__ == "__main__":
    pass