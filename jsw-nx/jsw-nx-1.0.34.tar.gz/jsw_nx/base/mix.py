def mix(*args):
    arg0 = args[0] or dict()
    arr = args[1:]
    for arg in arr:
        arg0.update(arg)
    return arg0
