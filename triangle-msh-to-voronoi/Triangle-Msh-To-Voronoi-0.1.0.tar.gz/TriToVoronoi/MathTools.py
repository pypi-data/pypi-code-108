#coding:utf-8
import numpy as np

def dis(a,b):
    '''两点距离'''
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5

def GetCent(a,b):
    '''两点中点'''
    return [(a[0] + b[0])*0.5, (a[1] + b[1])*0.5]   

def GetCentFromNodes(lnods,coords):
    cent = np.array([0,0])
    for inode in lnods:
        cent = cent + np.array(coords[inode])
    return cent / len(lnods)


def GetCosAngle(a,b,c):
    x = np.array(a) - np.array(c)
    y = np.array(b) - np.array(c)
    return x.dot(y)/(np.linalg.norm(x) * np.linalg.norm(y))


def GetIncenter(a,b,c):
    '''获取三角形内心坐标'''
    A=dis(b,c)
    B=dis(a,c)
    C=dis(a,b)
    S=A+B+C; 
    x=(A*a[0]+B*b[0]+C*c[0])/S
    y=(A*a[1]+B*b[1]+C*c[1])/S
    return [x,y]

def reOrderLine(lnods, coords, cent):
    '''逆时针排序lnods'''
    n = len(lnods)
    newList = [0]*n
    ds = {}
    lcoords = []
    for i in range(n):
        inode = lnods[i]
        lcoords.append(coords[inode])
        dir = np.array(coords[inode]) - np.array(cent)
        ds[i] = dir
        newList[i] = inode
    a = quick_sort(lnods, 0, n -1, ds)
    return a

def vector2dLeft(x,y):
    return x[0]*y[1] - x[1]* y[0] < 0

def quick_sort(lists,i,j, ds):
    if i >= j:
        return lists
    pivot = ds[i]
    pi = lists[i]
    low = i
    high = j
    while i < j:
        while i < j and vector2dLeft(ds[j], pivot):
            j -= 1
        lists[i]=lists[j]
        ds[i] = ds [j]
        while i < j and not vector2dLeft(ds[i], pivot):
            i += 1
        lists[j]=lists[i]
        ds[j] = ds[i]
    lists[j] = pi
    ds[j] = pivot
    quick_sort(lists,low,i-1,ds)
    quick_sort(lists,i+1,high,ds)
    return lists
