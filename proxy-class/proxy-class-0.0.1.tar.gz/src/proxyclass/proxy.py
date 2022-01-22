from abc import ABCMeta

from .annotation_utility import (
    get_function_defined_directly_in_annotation,
    get_function_from_object_defined_in_annotation
)
from .injection_utility import inject_method
from .method_to_inject import init_method


class ProxyMeta(ABCMeta):
    ''' Metaclass used to inject object of another class to class
    '''
    def __new__(cls, name, bases, cls_dict):      
        
        if '__init__' not in cls_dict:
            cls_dict['__init__'] = init_method

        if '__annotations__' in cls_dict:
            func_list = get_function_defined_directly_in_annotation(cls_dict['__annotations__'])
            if not func_list:
                func_list = get_function_from_object_defined_in_annotation(cls_dict['__annotations__'])
            inject_method(cls_dict, func_list)
        else:
            cls_dict['__annotations__'] = dict()

        for parent in bases:
            if parent != object and '__annotations__' in parent.__dict__:
                cls_dict['__annotations__'].update(parent.__dict__['__annotations__'])

        __cls = super().__new__(cls, name, bases, cls_dict)
        return __cls


def proxyclass(__cls):
    '''
    Class decorator implementing bridge design pattern. Returns the same class as was passed in.
    Concrete adaptee classes can be addded based on the fields defined in the class annotation.
    '''
    cls_dict = dict(__cls.__dict__)
    cls_dict.pop('__dict__', None)
    return ProxyMeta(__cls.__name__, __cls.__bases__, cls_dict)


