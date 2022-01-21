"""
TODO doc 
"""
import logging
import os
import sys
import threading
import time
import uuid

__all__=["HarvesterData"]

class HarvesterData(object):
    """TODO doc"""

    def __init__(self):
        self._data = {}
        self._key_lock = threading.Lock()
        
    def __getattr__(self, name):
        if name  == "_data":
            return self.__dict__[name]
        elif name  == "_key_lock":
            return self.__dict__[name]
        
        rst = None
        with self._key_lock:  
            rst = self._data[name] if name in self._data else None
        return rst
    
    def __setattr__(self, name, value):
        if name  == "_data":
             object.__setattr__(self, name, value)
        elif name  == "_key_lock":
            object.__setattr__(self, name, value)
        else:
            with self._key_lock: 
                self._data[name] = value