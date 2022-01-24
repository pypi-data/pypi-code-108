def filter(arr, fn):
    return [v for i, v in enumerate(arr) if fn(v, i)]
