# algorithms

from tkinter import E
from .util import colored
from dataclasses import dataclass
import re
debug = False


def split_paragraph(s):
    pattern = r"[\n \t\r]"
    spliter = re.findall(pattern, s)
    splited = re.split(pattern, s)
    ret = []
    # print(spliter)
    # print(splited)
    for idx, i in enumerate(splited):
        if(idx):
            ret.append(spliter[idx-1])
        ret.append(i)
    return ret


def ndarray(dims, fill=0):
    if(len(dims) == 1):
        n = dims[0]
        return [fill for i in range(n)]
    else:
        return [ndarray(dims[1:], fill=fill) for i in range(dims[0])]


def _eq(a, b):
    if(isinstance(a, str) and isinstance(b, str)):
        if(len(a) > 4 and len(b) > 4):
            rate = lcs(a, b).common_ratio
            return rate > 0.7
        else:
            return a.lower() == b.lower()
    else:
        return a == b


def _element_similarity(a, b):
    if(isinstance(a, str) and isinstance(b, str)):
        if(len(a) > 4 and len(b) > 4):
            return lcs(a, b).common_ratio
        else:
            return 1 if a.lower() == b.lower() else 0
    else:
        return 1 if a == b else 0
debug_dict={}
def element_similarity(a, b):
    global debug, debug_dict
    ret=_element_similarity(a, b)
    if(debug):
        if((a,b) not in debug_dict):
            print("similarity",a,b,"=",ret)
            debug_dict[(a,b)] = ret
    return ret
def _color_common(a, common, fore="RED"):
    idx = 0
    ret = []
    for ch in a:
        if(idx < len(common) and _eq(common[idx], ch.lower())):
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
    common_len: int
    a_matched: list
    b_matched: list

    def __init__(self, A, B):
        global debug
        n = len(A)
        m = len(B)
        dp = ndarray((n, m))
        self.a_matched = ndarray((n,), False)
        self.b_matched = ndarray((m,), False)
        dp_from = ndarray((n, m), (-1, -1))
        for i in range(n):
            for j in range(m):
                '''if(A[i] in 'Aa' and B[j] in 'Aa' and A[i]!=B[j]):
                    print(A[i],B[j],A[i].lower() == B[j].lower())'''
                mx = 0
                _dp_from = (-1, -1)

                # match A[i], B[j]
                score = dp[i-1][j-1] if (i and j) else 0
                score1 = element_similarity(A[i], B[j])
                
                if(score1):
                    
                    if(score+score1 >= mx):
                        mx = score+score1
                        _dp_from = (i-1, j-1)
                if(i):
                    if(dp[i-1][j] >= mx):
                        mx = dp[i-1][j]
                        _dp_from = (i-1, j)
                if(j):
                    if(dp[i][j-1] >= mx):
                        mx = dp[i][j-1]
                        _dp_from = (i, j-1)
                dp[i][j] = mx
                dp_from[i][j] = _dp_from
        u, v = n-1, m-1
        common = []
        while(u >= 0 and v >= 0):
            
            u1, v1 = dp_from[u][v]
            if(debug):
                print(u,v,'from',u1,v1)
            if(u1 == u-1 and v1 == v-1):
                if(element_similarity(A[u],B[v])>0.5):
                    common.append(A[u])
                    if(debug):
                        print("matching", A[u], B[v])
                    self.a_matched[u] = True
                    self.b_matched[v] = True
            u, v = u1, v1

        common = common[::-1]
        self.A = A
        self.B = B
        self.common = common  # list
        self.common_ratio_a = dp[n-1][m-1]/len(A)
        self.common_ratio_b = dp[n-1][m-1]/len(B)
        self.common_ratio = self.common_ratio_a*self.common_ratio_b
        self.common_len = dp[n-1][m-1]

    def color_common(self, foreA="RED", foreB="GREEN"):
        retA = []
        for idx, i in enumerate(self.A):
            if(self.a_matched[idx]):
                retA.append(str(colored(i, fore=foreA)))
            else:
                retA.append(i)
        retA = "".join(retA)

        retB = []
        for idx, i in enumerate(self.B):
            if(self.b_matched[idx]):
                retB.append(str(colored(i, fore=foreB)))
            else:
                retB.append(i)
        retB = "".join(retB)
        return retA, retB


if(__name__ == '__main__'):
    debug = True

    tmp = lcs("neural", "network")
    print(*tmp.color_common(), sep="\n")
    exit()
    A = "Approximate Nearest Neighbors in C++/Python optimized for memory usage"
    B = "nearest neighbbour"

    tmp = lcs(split_paragraph(A), split_paragraph(B))
    print(*tmp.color_common(), sep="\n")
