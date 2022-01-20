import pandas as pd
import math

def class_methods(cls):

    @property
    def attributes(self):
        for attr, value in self.__dict__.items():
            if isinstance(value, (str, int, float, list, tuple)):
                print(f'{attr}: {value}')
            else:
                print(f'{attr}: {type(value)}')

    @property
    def help(self):
        print(self.__doc__)

    setattr(cls, 'attributes', attributes)
    setattr(cls, 'help', help)
    
    return cls

def add_docstring(value):
    if not isinstance(value, str):
        value = value.__doc__
    def _doc(func):
        func.__doc__ = value
        return func
    return _doc

# resampling
resolution_functions = {
    'sum': sum,
    'min': min,
    'max': max,
    }

def resolution_function(func):
    resolution_functions[func.__name__] = func
    return func
