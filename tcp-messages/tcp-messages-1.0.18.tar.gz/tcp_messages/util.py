def check_type(v, t, m):
    if not isinstance(v, t):
        raise TypeError(m)
