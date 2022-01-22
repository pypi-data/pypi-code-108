import inspect


def get_function_defined_directly_in_annotation(annotation):
    res = dict()
    for func_name, func_obj in annotation.items():
        if inspect.isroutine(func_obj):
            origin_obj_name, origin_func_name = None, None

            for checked_obj_name, checked_obj in annotation.items():
                if inspect.isclass(checked_obj):
                    checked_obj_dict = dict(inspect.getmembers(checked_obj, inspect.isroutine))
                    for checked_obj_func_name, checked_obj_func in checked_obj_dict.items():
                        if func_obj == checked_obj_func:
                            origin_obj_name = checked_obj_name
                            origin_func_name = checked_obj_func_name

            if origin_obj_name:
                res[func_name] = (origin_obj_name, func_obj, origin_func_name)
    return res


def get_function_from_object_defined_in_annotation(annotation):
    res = dict()
    for origin_obj_name, origin_obj in annotation.items():
        if inspect.isclass(origin_obj):
            origin_obj_dict = origin_obj.__dict__
        else:
            origin_obj_dict = origin_obj.__class__.__dict__

        for origin_func_name, origin_func in origin_obj_dict.items():
            res[origin_func_name] = (origin_obj_name, origin_func, origin_func_name)    
    return res
