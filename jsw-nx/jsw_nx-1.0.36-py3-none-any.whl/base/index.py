def index(arr, value):
    for i, v in enumerate(arr):
        if v == value:
            return i
    return -1
