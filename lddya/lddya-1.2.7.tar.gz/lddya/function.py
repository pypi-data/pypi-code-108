import datetime
import os,sys



def matrix_add(A,B):
    for i in range(len(A)):
        for j in range(len(A)):
            A[i][j]+=B[i][j]
    return A

def matrix_del(A,B):
    for i in range(len(A)):
        for j in range(len(A)):
            A[i][j]-=B[i][j]
    return A

def map_reverse(fp = 'map.dll'):
    os.chdir(sys.path[0])
    with open(fp,'r') as f:
        d = f.readlines()
    d.reverse()
    with open(fp,'w') as f:
        f.writelines(d)