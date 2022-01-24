def hoh(base, *keys):
    x = base
    for k in keys:
        if k not in x:
            x[k] = {}
        x = x[k]
    return base
