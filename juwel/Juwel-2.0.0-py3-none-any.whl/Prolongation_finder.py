#!/usr/bin/env python3

def get_prolongation(my_string):
    string_list = my_string.split()

    my_int = 0
    for word in string_list:
        if word.isdigit():
            my_int = int(word)

    if my_int != 0:
        return my_int
    elif my_int == 0:
        return my_string
