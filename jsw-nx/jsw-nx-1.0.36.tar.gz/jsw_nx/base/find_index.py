def find_index(arr, fn):
    for i in range(len(arr)):
        if fn(arr[i], i):
            return i
    return -1
