#coding:utf-8
from .Element import Element
import sys

class MshReader:
    '''读取模型文件'''
    mshfilePath = ''
    coords = {}
    elements={}
    npoin = 0
    nelem = 0
    ngroup = 0
    groupEle = {}
    ndimn = 2

    def ReadFromEleCor(self,elePath,corPath,eleHasNnode):
        '''从ele，cor文件中读取模型信息'''
        with open(corPath,'rU') as f:
            lines = f.readlines()
            nline = len(lines)
            #判断维度
            for i in range(nline):
                line = lines[i]
                L = line.split()
                if L == [] or L[0].isdigit() == False:
                    continue
                if float(L[-1]) == 0 or len(L) == 3:
                    self.ndimn = 2
                    ilist = [0,1]
                else:
                    self.ndimn = 3
                    ilist = [0,1,2]
                    print("只能用于二维模型")
                    sys.exit()
                break
            for line in lines:
                L = line.split() #将字符串转换为列表，列表的每一个元素为一个字符
                if L == []:
                    #是空的
                    continue
                self.npoin+=1
                id = int(L[0])
                #求最大最小坐标
                coord = [0] * self.ndimn
                for i in ilist:
                    coord[i] = float(L[i + 1])
                self.coords[id] = coord


        with open(elePath,'rU') as f:
            lines = f.readlines()
            for line in lines:
                L = line.split() #将字符串转换为列表，列表的每一个元素为一个字符
                if L == []:
                    #是空的
                    continue
                self.nelem+=1
                ele = Element()
                ele.id = int(L[0])
                lnodeOffset = 2
                if eleHasNnode:
                    ele.nnode = int(L[1])
                else:
                    #没有节点数量
                    lnodeOffset = 1
                    ele.nnode = len(L) - 2
                ele.lnods = [0]*ele.nnode
                ele.igroup = int(L[-1])

                for i in range(ele.nnode):
                    ele.lnods[i] = int(L[i+lnodeOffset])
                self.elements[ele.id] = ele
                
                if ele.igroup not in self.groupEle:
                    self.groupEle[ele.igroup] = []

                self.groupEle[ele.igroup].append(ele)
        self.ngroup = len(self.groupEle)

        

    def ReadHmMsh(self,filePath):
        '''读取hyperMesh使用GidCE.ptl导出的msh文件'''
        self.mshfilePath = filePath
        #通过获取ele和col的起始结束行来复制信息
        #同时获取总体模型范围和单元数量，分组数量等信息
        #原方法为复制每一行的数据累加到一个字符串中，然后写入文件，但对于大文件，该操作太慢，故舍弃
        with open(self.mshfilePath,'rU') as f:
            lines = f.readlines()
            nline = len(lines)
            flag = 0
            #判断维度
            for i in range(nline):
                line = lines[i]
                L = line.split()

                if L[0].isdigit() == False:
                    continue
                if float(L[-1]) == 0:
                    self.ndimn = 2
                    ilist = [0,1]
                else:
                    self.ndimn = 3
                    ilist = [0,1,2]
                    print("只能用于二维模型")
                    sys.exit()
                break
            maxCoord = [sys.float_info.min] * self.ndimn
            minCoord = [sys.float_info.max] * self.ndimn

            #读取msh
            for iline in range(nline):
                line = lines[iline]
                if iline % 100 == 0:
                    sys.stdout.write("iline" + str(iline) + "\r")
                L = line.split() #将字符串转换为列表，列表的每一个元素为一个字符
                if L == []:
                    #是空的
                    continue
                if L[0].isdigit() == False:
                    #是字符串
                    if 'node' in line.lower():
                        flag = 0
                    elif 'ele' in line.lower():
                        flag = 1
                    continue
                
                if flag == 0 :
                    #是节点坐标信息
                    self.npoin+=1
                    id = int(L[0])
                    #求最大最小坐标
                    coord = [0] * self.ndimn
                    for i in ilist:
                        coord[i] = float(L[i + 1])
                        if(maxCoord[i] < coord[i]):
                            maxCoord[i] = coord[i]
                        if(minCoord[i] > coord[i]):
                            minCoord[i] = coord[i]
                    self.coords[id] = coord
                    #colData+=line
                elif flag == 1:
                    #是单元信息
                    self.nelem+=1
                    ele = Element()
                    ele.id = int(L[0])
                    ele.nnode = int(L[1])
                    ele.lnods = [0]*ele.nnode
                    ele.igroup = int(L[-1])

                    for i in range(ele.nnode):
                        ele.lnods[i] = int(L[i+2])
                    self.elements[ele.id] = ele
                    
                    if ele.igroup not in self.groupEle:
                        self.groupEle[ele.igroup] = []

                    self.groupEle[ele.igroup].append(ele)

            self.ngroup = len(self.groupEle)