def map(arr, fn):
    return [fn(v, i) for i, v in enumerate(arr)]
