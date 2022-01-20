def set(d, key, value):
    dd = d
    keys = key.split('.')
    latest = keys.pop()
    for k in keys:
        dd = dd.setdefault(k, {})
    dd[latest] = value
