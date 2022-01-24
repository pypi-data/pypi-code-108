def type(target):
    if isinstance(target, str):
        return 'string'
    elif isinstance(target, int):
        return 'int'
    elif isinstance(target, float):
        return 'float'
    elif isinstance(target, bool):
        return 'bool'
    elif isinstance(target, list):
        return 'list'
    elif isinstance(target, dict):
        return 'dict'
    elif isinstance(target, tuple):
        return 'tuple'
    elif isinstance(target, set):
        return 'set'
    elif isinstance(target, frozenset):
        return 'frozenset'
    elif isinstance(target, object):
        return 'object'
    else:
        return 'unknown'