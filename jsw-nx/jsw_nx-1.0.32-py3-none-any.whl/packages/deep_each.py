def deep_each(obj, func):
    def inner_each(key, value, parent, fn):
        if isinstance(value, dict):
            for k, v in value.items():
                inner_each(k, v, value, fn)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                inner_each(i, v, value, fn)
        else:
            fn(key, value, parent)

    obj = [obj] if isinstance(obj, dict) else obj

    for i, v in enumerate(obj):
        inner_each(i, v, obj, func)
