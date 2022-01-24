# algorithms

from .util import colored
from dataclasses import dataclass


def _color_common(a, common, fore="RED"):
    idx = 0
    ret = []
    for ch in a:
        if(idx < len(common) and common[idx].lower() == ch.lower()):
            ret.append(str(colored(ch, fore=fore)))
            idx += 1
        else:
            ret.append(ch)
    return ''.join(ret)

@dataclass
class lcs:
    A: str
    B: str
    common: str
    common_ratio_a: float
    common_ratio_b: float
    common_ratio: float
    def __init__(self, A, B):
        n = len(A)
        m = len(B)
        dp = ndarray((n, m))
        dp_from = ndarray((n, m), (-1, -1))
        for i in range(n):
            for j in range(m):
                '''if(A[i] in 'Aa' and B[j] in 'Aa' and A[i]!=B[j]):
                    print(A[i],B[j],A[i].lower() == B[j].lower())'''
                if(A[i].lower() == B[j].lower()):
                    if(i and j):
                        dp[i][j] = dp[i-1][j-1]+1
                    else:
                        dp[i][j] = 1
                    dp_from[i][j] = (i-1, j-1)
                else:
                    _dp_from = None
                    mx = 0
                    if(i):
                        if(dp[i-1][j] >= mx):
                            _dp_from = (i-1, j)
                            mx = dp[i-1][j]
                    if(j):
                        if(dp[i][j-1] >= mx):
                            _dp_from = (i, j-1)
                            mx = dp[i][j-1]
                    if(_dp_from is None):
                        dp[i][j] = 0
                    else:
                        dp[i][j] = mx
                        dp_from[i][j] = _dp_from
        u, v = n-1, m-1
        common = []
        while(u >= 0 and v >= 0):
            if(A[u].lower() == B[v].lower()):
                common.append(A[u])
            u, v = dp_from[u][v]
        common = common[::-1]
        self.A=A
        self.B=B
        self.common=common  # list
        self.common_ratio_a=len(common)/len(A)
        self.common_ratio_b=len(common)/len(B)
        self.common_ratio=self.common_ratio_a*self.common_ratio_b
    def color_common(self,foreA="RED",foreB="GREEN"):
        return _color_common(self.A,self.common,foreA),_color_common(self.B,self.common,foreB)
    

def ndarray(dims, fill=0):
    if(len(dims) == 1):
        n = dims[0]
        return [fill for i in range(n)]
    else:
        return [ndarray(dims[1:], fill=fill) for i in range(dims[0])]



if(__name__=='__main__'):
    tmp=lcs("fuck",'ucl')
    print(tmp)
    print(lcs([1,1,4,5,1,4],[1,9,1,9,8,1,0]))
    print(*tmp.color_common())