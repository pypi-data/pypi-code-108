from .QS import QS
def IS(A , x):
    low =  0
    mid = -1
    high = len(A) - 1

    while (low <=high):
        if low == high or A[low] == A[high]:
            return 'not found !'
        mid = low + ((high-low) // (A[high] - A[low] )) * (x - A[low])
        if A[mid] == x:
            return {'index':mid}
        elif A[mid] < x:
            low = mid + 1
        elif A[mid] > x:
            high = mid -1

