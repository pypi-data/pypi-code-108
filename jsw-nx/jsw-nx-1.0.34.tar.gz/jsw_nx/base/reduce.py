def reduce(arr, fn, initial=None):
    if initial is None:
        initial = arr[0]
        arr = arr[1:]
    for i, v in enumerate(arr):
        initial = fn(initial, v, i)
    return initial
