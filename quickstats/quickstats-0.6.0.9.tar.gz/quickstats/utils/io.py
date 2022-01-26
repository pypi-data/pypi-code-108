from enum import Enum
from typing import Union
from functools import total_ordering

@total_ordering
class Verbosity(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        elif isinstance(other, int):
            return self.value < other
        elif isinstance(other, str):
            return self.value < getattr(self, other.upper()).value
        return NotImplemented

class VerbosePrint:
    @property
    def verbosity(self):
        return self._verbosity
    
    @verbosity.setter
    def verbosity(self, val):
        if isinstance(val, str):
            try:
                v = getattr(Verbosity, val.upper())
            except:
                raise ValueError("invalid verbosity level: {}".format(val))
            self._verbosity = v
        else:
            self._verbosity = val

    def __init__(self, verbosity:Union[int, Verbosity, str]=Verbosity.INFO):
        self.verbosity = verbosity
        
    def info(self, text:str):
        self.__call__(text, Verbosity.INFO)
        
    def warning(self, text:str):
        self.__call__(text, Verbosity.WARNING)
        
    def error(self, text:str):
        self.__call__(text, Verbosity.ERROR)
        
    def critical(self, text:str):
        self.__call__(text, Verbosity.CRITICAL)

    def debug(self, text:str):
        self.__call__(text, Verbosity.DEBUG)
        
    def __call__(self, text:str, verbosity:int=Verbosity.INFO):
        if verbosity >= self.verbosity:
            print(text)