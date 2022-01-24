# -*- coding: utf-8 -*-
#Copyright (c) 2020, KarjaKAK
#All rights reserved.

import json
import os
from collections.abc import Iterator
from types import GeneratorType
from typing import Union, Any
from functools import wraps

def primer(gfn):
    """Wrapper for generator for priming first next"""
    
    @wraps(gfn)
    def nexting(*args, **kwargs):
        wr = gfn(*args, **kwargs)
        next(wr)
        return wr
    return nexting

class Datab:
    """
    Database created in json file.
    """
    __slots__ = '__path',
    
    def __init__(self, pname: str):
        if isinstance(pname, str):
            self.__path = f'{pname}.json' if '.json' not in pname else pname
        else:
            raise TypeError('{pname} must be string!')
    
    def __getattribute__(self, name):
        return super().__getattribute__(name)
    
    def __getattr__(self, name):
        if name == 'pname':
            return self.__path
        raise AttributeError(f'"{name}" is not exist!')
    
    def __repr__(self):
        return f'Datab(pname = {self.__path})'
    
    def validate(self):
        """Validate Path"""
        
        if os.path.exists(self.__path):
            return True
        raise FileNotFoundError('File is not exist yet!')
        
    def gdt(self):
        """Get database"""
        
        with open(self.__path) as rdb:
            jit = iter(json.load(rdb).items())
        return jit
    
    def wdt(self, data: Union[Iterator, GeneratorType]) -> None:
        """Writing database"""
        
        try:
            jit = None
            if self.validate():
                jit = self.gdt()
                with open(self.__path, 'w') as dbj:
                    json.dump(dict(jit)|dict(data), dbj)
        except:
            with open(self.__path, 'w') as dbj:
                json.dump(dict(data), dbj)
        finally:
            del jit, data
    
    @primer
    def comit(self):
        """Generator writer for database"""
        
        try:
            dt = {}
            caperr = None
            try:
                while True:
                    rcv = yield
                    dt.update([rcv])
            except Exception as e:
                caperr = str(e)
                raise e
        finally:
            if caperr is None:
                with open(self.__path, 'w') as dbj:
                    json.dump(dt, dbj)
            else:
                del caperr
            del dt
                
    def createdb(self, data: Union[Iterator, GeneratorType]) -> None:
        """Create first time database."""
        
        try:
            if isinstance(data, (Iterator, GeneratorType)):
                try:
                    if not os.path.exists(self.__path):
                        self.wdt(data)
                    else:
                        raise FileExistsError('File already exist!')
                except Exception as e:
                    raise e
            else:
                raise TypeError('Must be Generator or iterator')
        except Exception as e:
            raise e
        finally:
            del data
    
    def indata(self, data: Union[Iterator, GeneratorType]) -> None:
        """Insert data to existing database."""
        
        try:
            if isinstance(data, (Iterator, GeneratorType)):
                if self.validate():
                    self.wdt(data)
            else:
                raise TypeError('Must be Generator or iterator')
        except Exception as e:
            raise e
        finally:
            del data        
    
    def deldata(self, named: str) -> None:
        """Delete a data in existing database."""
        
        try:
            if isinstance(named, str):
                if self.validate():
                    writer = self.comit()
                    for d in self.gdt():
                        if d[0] != named:
                            writer.send(d)
                    writer.close()
            else:
                raise TypeError('Must be str')
        except Exception as e:
            raise e
        finally:
            del named
    
    def takedat(self, named: str) -> Any:
        """
        Taking a data from database.
        If value is a string,
        it will return both key and value.
        """
        
        try:
            if isinstance(named, str):
                for d in self.gdt():
                    if d[0] == named:
                        if isinstance(d[1], str):
                            return iter(d)
                        return iter(d[1])
            else:
                raise TypeError('Must be str')
        except Exception as e:
            raise e
        finally:
            del named
            
    def totalrecs(self) -> int:
        """Return the total of records in database."""
        
        try:
            if self.validate():
                return len(tuple(self.gdt()))
        except Exception as e:
            raise e
        
    def deldb(self) -> None:
        """Delete database."""
        
        if self.validate():
            os.remove(self.__path)
    
    def loadall(self) -> Any:
        """Load all database to dictionary's items."""
        
        try:
            if self.validate():
                return iter(dict(self.gdt()).items())
        except Exception as e:
            raise e
            
    def loadkeys(self) -> Any:
        """Load all database keys only."""
        
        try:
            if self.validate():
                return iter(dict(self.gdt()).keys())
        except Exception as e:
            raise e
    
    def loadvalues(self) -> Any:
        """Load all database values only."""
        
        try:
            if self.validate():
                return iter(dict(self.gdt()).values())
        except Exception as e:
            raise e