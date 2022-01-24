# -*- coding: utf-8 -*-
# Copyright © kakkarja (K A K)

import re
import weakref
from types import GeneratorType
from functools import wraps

class DescriptClasses(type):
    
    def __new__(cls, name, bases, cls_d):
        CLS_NAMES = ['ChildsNum', 'Parent', 'FileName']
        
        clsob = super().__new__(cls, name, bases, cls_d)
        
        if name == CLS_NAMES[2]:
            setattr(clsob, 'store1', dict())        
        
        def _set(clsob, instance, value):
            return NotImplemented
        
        if name in CLS_NAMES[:2]:
            setattr(clsob, '__set__', _set)
        
        def getchild(clsob, instance, owner_class):
            if clsob.totr is None:
                clsob.totr = (clsob.childs * clsob.spc) + 1
            spc = clsob.spc
            return ((f'child{c//spc}', c) for c in range(clsob.totr) if c % spc == 0 and c != 0)
        
        if name == CLS_NAMES[0]:
            setattr(clsob, '__get__', getchild)
        
        def getpar(clsob, instance, owner_class):
            return enumerate(('parent',))
        
        if name == CLS_NAMES[1]:
            setattr(clsob, '__get__', getpar)
        
        def getfil(clsob, instance, owner):
            if instance is None:
                return clsob
            else:
                return clsob.store1[id(instance)][1]
        
        if name == CLS_NAMES[2]:
            setattr(clsob, '__get__', getfil)
    
        def setfil(clsob, instance, value):
            if id(instance) not in clsob.store1:
                clsob.store1[id(instance)] = \
                    (weakref.ref(instance, clsob.finalize), value)
        
        if name == CLS_NAMES[2]:
            setattr(clsob, '__set__', setfil)
        
        def finalize(clsob, weak_ref):
            look = [key for key, value in clsob.store1.items()
                    if value[0] is weak_ref]
            if look:
                del clsob.store1[look[0]]
        
        if name == CLS_NAMES[2]:
            setattr(clsob, 'finalize', finalize)

        def delch(clsob, instance):
            del instance, clsob
        
        if name in CLS_NAMES:
            setattr(clsob, '__delete__', delch)
                
        return clsob

class ChildsNum(metaclass=DescriptClasses):
    
    def __init__(self, childs, spc):
        if isinstance(childs, int) and isinstance(spc, int):
            self.childs = childs
            self.spc = spc
            self.totr = None
    
class Parent(metaclass=DescriptClasses):
    pass 
    
class FileName(metaclass=DescriptClasses):
    pass

def configtv(childs = None, space = None):
    """Decorator for childs in TreeView."""
    
    def childnum(cls):
        @wraps(cls)
        def inner(arg):
            if childs and space:
                cls.childs = ChildsNum(childs, space)
            return cls(arg)
        return inner
    return childnum