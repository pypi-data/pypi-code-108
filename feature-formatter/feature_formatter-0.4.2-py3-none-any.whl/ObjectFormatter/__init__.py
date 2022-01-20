def customize_round(n, digit=3):
    if isinstance(n, float):
        r = round(n, digit)
        if r == 0 and n > 0:
            return 0.001
        if r == 1 and n < 1:
            return 0.999
        return r
    return n


def round_float(obj, digit=3, round_func=customize_round):
    if isinstance(obj, tuple):
        obj = list(obj)
    if isinstance(obj, (dict, list)):
        iter = obj.keys() if isinstance(obj, dict) else range(len(obj))
        for key in iter:
            if isinstance(obj[key], (dict, list, tuple)):
                obj[key] = round_float(obj[key])
            else:
                obj[key] = round_func(obj[key], digit)
    return obj
