import numpy as np

def mapper(string=''):
    string = str(string)
    value = 0
    for char in string:
        value += np.cos(1/ord(char))
    return value
