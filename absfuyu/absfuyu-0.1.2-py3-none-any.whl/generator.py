#!/usr/bin/env python
# coding: utf-8

# Import library
import string
import random



__all__ = [
    "randStrGen",
    # "strGen", "checkDigitGen",
]


# Random string generator
def randStrGen(size=8,times=1,char="default"):
    character_option = {
        "default": string.ascii_letters + string.digits,
        "full": string.ascii_letters + string.digits + string.punctuation,
        "uppercase": string.ascii_uppercase,
        "lowercase": string.ascii_lowercase,
        "digit": string.digits,
        "special": string.punctuation
    }

    if char not in character_option:
        return -1

    unique_string = []
    count = 0
    char_lst = character_option[char]

    while (count < times):
        s = ''.join(random.choice(char_lst) for _ in range(size))
        if s not in unique_string:
            unique_string.append(s)
            count += 1

    return unique_string



# generate random string from a string
def strGen(from_string="",size=8,times=1):
    if from_string == "":
        return -1

    unique_string = []
    count = 0

    while (count < times):
        s = ''.join(random.choice(from_string) for _ in range(size))
        if s not in unique_string:
            unique_string.append(s)
            count += 1

    if times == 1:
        return unique_string[0]
    else:
        return unique_string




# Check digit generator
def checkDigitGen(number):
    # turn into array then reverse the order
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