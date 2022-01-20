def find(arr, fn):
    for i in range(len(arr)):
        if fn(arr[i], i):
            return arr[i]
    return None
