from .QS import QS
def binary_search(A,x,lower,upper):
    if(x == A[0]):
        return ({'index':0, 'element':A[0]})
    if(x == A[len(A)-1]):
        return ({'index':len(A)-1, 'element':A[len(A)-1]})   
    if upper >=lower:
   
        mid = lower + (upper - lower)//2
        if x == A[mid]:
            return ({'index':mid, 'element':A[mid]})
        elif x<A[mid]:
            return binary_search(A,x,lower,mid-1)
        elif x>A[mid]:
            return binary_search(A,x,mid+1, upper)
    return 'not found'
        

    

