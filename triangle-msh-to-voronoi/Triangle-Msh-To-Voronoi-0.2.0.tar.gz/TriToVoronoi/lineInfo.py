#coding:utf-8

class lineInfo:
    inode = 0
    jnode = 0
    cent = []
    def __init__(self,inode,jnode,coords):
        self.inode = inode
        self.jnode = jnode
        x = coords[inode]
        y = coords[jnode]
        n = len(x)
        self.cent = [0]*n
        for i in range(n):
            self.cent[i] = (x[i] + y[i])*0.5