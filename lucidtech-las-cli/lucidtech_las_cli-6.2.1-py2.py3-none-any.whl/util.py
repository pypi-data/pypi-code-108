class NotProvided:
    pass


def nullable(value):
    if isinstance(value, str) and value == 'null':
        return None
    return value
