import numpy as np

def mapper(string=''):
    string = str(string)
    value = 0
    for char in string:
        value += np.sin(1/ord(char))
    return value
