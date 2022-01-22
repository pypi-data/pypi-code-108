import inspect
import types


def inject_method(cls_dict, func_list):
        for func_name, (origin_obj_name, origin_func, origin_func_name) in func_list.items():
            if func_name not in cls_dict:
                _inject_function_to_class(cls_dict, func_name, origin_obj_name, origin_func, origin_func_name)


def _inject_function_to_class(cls_dict, func_name, origin_obj_name, origin_func, origin_func_name):
    func_decorator = cls_dict.get('_method_decorator', None)
    func = _injected_function_factory(cls_dict, origin_obj_name, origin_func_name, func_decorator)
        
    if inspect.isfunction(origin_func):
        cls_dict[func_name] = func
    if isinstance(origin_func, classmethod):
        cls_dict[func_name] = classmethod(func)
    if isinstance(origin_func, staticmethod):
        cls_dict[func_name] = staticmethod(func)


def _injected_function_factory(cls_dict, origin_obj_name, func_name, method_decorator):
    def wrapper(self, 
                *args, 
                _origin_obj_name=origin_obj_name, 
                _func_name=func_name, 
                _method_decorator=method_decorator,
                **kwargs):

        injected_obj = getattr(self, _origin_obj_name)

        if injected_obj:
            injected_func = injected_obj.__getattribute__(_func_name)
        else:
            for _, checked_obj in cls_dict['__annotations__'].items():
                if inspect.isclass(checked_obj):
                    checked_obj_dict = dict(inspect.getmembers(checked_obj, inspect.isroutine))
                    injected_func = checked_obj_dict.get(_func_name, None)
                    injected_func = types.MethodType(injected_func, self)
                    
        if _method_decorator:
            injected_func = _method_decorator(self, injected_func)
        return injected_func(*args, **kwargs)
    return wrapper