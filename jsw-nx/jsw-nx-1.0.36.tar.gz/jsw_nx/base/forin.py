def forin(arr, fn):
    for i in range(len(arr)):
        fn(arr[i], i)