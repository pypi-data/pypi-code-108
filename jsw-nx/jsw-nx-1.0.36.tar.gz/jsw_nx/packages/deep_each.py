def deep_each(obj, func):
    def inner_each(key, value, parent, fn):
        fn(key, value, parent)
        if isinstance(value, dict):
            for k, v in value.items():
                inner_each(k, v, value, fn)
        if isinstance(value, list):
            for i, v in enumerate(value):
                inner_each(i, v, value, fn)

    inner_each(None, obj, None, func)
