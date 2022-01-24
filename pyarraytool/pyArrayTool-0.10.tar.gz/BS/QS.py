def partition(A,p,r):
    x = A[r]
    i = p-1
    for j in range(p,r):
        if A[j] <= x:
            i = i+1
            A[i],A[j] = A[j],A[i]
    A[i+1],A[r] =A[r],A[i+1] 
    return i+1
    
def QS(A,p,r):
    if p<r:
        q = partition(A,p,r)
        QS(A,p,q-1)
        QS(A,q+1,r)
    return A


