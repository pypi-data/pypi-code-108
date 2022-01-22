#coding:utf-8

from .Element import Element
from .MshReader import MshReader
from .lineInfo import lineInfo
from .FlaviaMshWriter import WriteFlaviaMsh
import numpy as np
from . import MathTools as mt
from .CalcConfigWriter import writeCalcConfig


def GenerateVoronoi(generateIGroups,outputFilePath,outputFolderPath,inieles,iniCoords):
    '''从三角形网格生成泰森多边形'''
    lineEleLib = {3:[[0,1],[1,2],[2,0]],4:[[0,1],[1,2],[2,3],[3,0]]}    #线在单元中的节点编号
    nlineEleLib = {3:3,4:4}         #不同节点的单元其边线的数量

    nline = 0
    lines = {}      #存储不重复的网格线
    eleLineIds = {}          #单元边线的整体编号


    eleLineState = {}       #单元边线状态，用于排除重复线
    nodeConnectedEles = {}      #节点相连的单元
    iniTriEles = {}         #需要生成泰森多边形的单元
    iniOtherEles = {}         #不需要生成泰森多边形的单元

    #遍历所有单元,寻找节点相连的单元
    for iele, ele in inieles.items():
        if ele.igroup in generateIGroups:
            iniTriEles[iele] = ele
            eleLineState[iele] = [False]*nlineEleLib[ele.nnode]
            eleLineIds[iele] = [0]*nlineEleLib[ele.nnode]
            for inode in ele.lnods:
                if inode not in nodeConnectedEles:
                    nodeConnectedEles[inode]=[]
                nodeConnectedEles[inode].append(ele)
        else:
            iniOtherEles[iele] = ele

    eleConnectedEles = {}      #单元相邻的单元
    ieleToVoInode = {}
    voInode = 0
    voCoords = {}
    #遍历所有单元,寻找单元相邻的单元,计算内心作为泰森多边形节点
    for iele, ele in iniTriEles.items():
        voInode += 1
        ieleToVoInode[iele] = voInode
        connectedEles = []
        ele.cent = mt.GetIncenter(iniCoords[ele.lnods[0]],iniCoords[ele.lnods[1]],iniCoords[ele.lnods[2]])
        voCoords[voInode] = ele.cent
        eleConnectedEles[iele] = connectedEles
        for inode in ele.lnods:
            for nearEle in nodeConnectedEles[inode]:
                if nearEle.id > iele and nearEle not in connectedEles:
                    #只需要将大编号单元放在小编号的单元的相邻列表中，可以减少后面的检索次数
                    connectedEles.append(nearEle)


    #遍历所有单元，找到不重复的线段,这一步有点费时间
    print('正在寻找网格线...')
    lineConnectedEles = {}
    for iele, ele in iniTriEles.items():
        inline = nlineEleLib[ele.nnode]
        localLineIndex = lineEleLib[inline]
        lineState = eleLineState[iele]
        for i in range(inline):
            if lineState[i]:
                continue
            lineState[i] = True
            pi1 = ele.lnods[localLineIndex[i][0]]
            pi2 = ele.lnods[localLineIndex[i][1]]
            #添加这条线
            nline +=1
            line = lineInfo(pi1,pi2,iniCoords)
            lines[nline] = line
            eleLineIds[iele][i] = nline
            lineEles = [ele]
            lineConnectedEles[nline] = lineEles
            #在相邻单元中排除这条线
            for nearEle in eleConnectedEles[iele]:
                nearLineState = eleLineState[nearEle.id]
                nearNline = nlineEleLib[nearEle.nnode]
                for j in range(nearNline):
                    if nearLineState[j]:
                        continue
                    pj1 = nearEle.lnods[localLineIndex[j][0]]
                    pj2 = nearEle.lnods[localLineIndex[j][1]]
                    if (pi1 == pj1 and pi2 == pj2) or (pi1 == pj2 and pi2 == pj1):
                        #重复线段
                        nearLineState[j] = True
                        eleLineIds[nearEle.id][j] = nline
                        lineEles.append(nearEle)




    #找边界点
    print('正在找边界...')
    IsEdgePoint = {}
    IsCornerPoint = {}
    nodeConnectedILines = {}
    for centerInode,nearEles in nodeConnectedEles.items():
        localLines = [] #节点周围的线的整体编号
        
        for ele in nearEles:
            eleNline = nlineEleLib[ele.nnode]
            localLineIndex = lineEleLib[inline]
            for i in range(eleNline):
                pi1 = ele.lnods[localLineIndex[i][0]]
                pi2 = ele.lnods[localLineIndex[i][1]]
                iline = eleLineIds[ele.id][i]
                if pi1 == centerInode or pi2 == centerInode:
                    if iline not in localLines:
                        localLines.append(iline)
        connectedNline = len(localLines)
        nodeConnectedILines[centerInode] = localLines
        #判断该点是否在边界上，根据管策定理，当点周围线的数量比单元数量多就是边界
        IsEdgePoint[centerInode] = connectedNline > len(nodeConnectedEles[centerInode])
        
        

    #找边界线,在边界线中点生成泰森多边形节点,模型角点也是多边形节点
    IsEdgeLine = {}
    edgeILineToVoInode = {}
    cornerInodeToVoInode = {}
    voInode = len(eleConnectedEles)  #泰森多边形单元边界节点起始编号
    hasJudged = [False] * len(lines)
    for centerInode,nearILines in nodeConnectedILines.items():
        for iline in nearILines:
            if hasJudged[iline-1]:
                continue
            hasJudged[iline-1] = True
            #与线相邻的单元只有一个，说明是边界线
            if len(lineConnectedEles[iline]) == 1:
                voInode += 1
                edgeILineToVoInode[iline] = voInode
                voCoords[voInode] = lines[iline].cent
                IsEdgeLine[iline] = True
            else:
                IsEdgeLine[iline] = False


    #遍历节点，创建泰森多边形,按节点数量分组
    print('正在创建泰森多边形...')
    vNgroup = 0
    igroup = 0
    vGroups = {}
    vGroupNnode = {}
    voronoiEles = {}
    for centerInode,nearEles in nodeConnectedEles.items():
        lnods = []
        if IsEdgePoint[centerInode]:
            #添加与该点连接的边界线
            for iline in nodeConnectedILines[centerInode]:
                if IsEdgeLine[iline]:
                    lnods.append(edgeILineToVoInode[iline])
            #如果顶点两侧的边界线夹角小于179.9°，认为是角点
            if mt.GetCosAngle(voCoords[lnods[0]],voCoords[lnods[1]],iniCoords[centerInode]) > -0.99:
                voInode += 1
                voCoords[voInode] = iniCoords[centerInode]
                cornerInodeToVoInode[centerInode] = voInode
                lnods.append(voInode)
            else:
                a=1

        #添加与该点连接的单元内心
        for nearEle in nearEles:
            lnods.append(ieleToVoInode[nearEle.id])
        #按逆时针排序
        mt.reOrderLine(lnods, voCoords, mt.GetCentFromNodes(lnods,voCoords))
        
        nnode = len(lnods)
        if nnode not in vGroupNnode:
            igroup +=1
            vGroups[igroup] = []
            vGroupNnode[nnode] = igroup
            
        vele = Element()
        vele.id = centerInode
        vele.nnode = nnode
        vele.igroup = vGroupNnode[nnode]
        vele.lnods = lnods
        vGroups[vele.igroup].append(vele)
        voronoiEles[centerInode] = vele

    #整理节点信息
    print('正在整理节点和单元编号...')
    resCoords = {}
    resEles = {}
    #先提取出没有生成泰森多边形分组的节点号
    originalCoord = {}
    originalGroup = {}
    npoints = 0
    nelems = 0
    ngroups = 0
    groupELes = {}
    #没有生成多边形分组的顶点
    for iele, ele in iniOtherEles.items():
        if ele.igroup not in originalGroup:
            ngroups += 1
            originalGroup[ele.igroup] = ngroups
            groupELes[ngroups] = []
        for inode in ele.lnods:
            if inode not in originalCoord:
                npoints += 1
                originalCoord[inode]=npoints
                resCoords[npoints] = iniCoords[inode]
    #没有生成多边形分组的单元，顶点索引重新编号
    for iele, ele in iniOtherEles.items():
        nelems += 1
        lnods = []
        newEle = Element()
        resEles[nelems] = newEle
        newEle.id = nelems
        newEle.igroup = originalGroup[ele.igroup]
        groupELes[newEle.igroup].append(newEle)
        newEle.nnode = ele.nnode
        newEle.lnods = lnods
        for inode in ele.lnods:
            lnods.append(originalCoord[inode])

    #添加上泰森多边形的节点和单元
    #先矫正多边形单元节点编号
    for igroup,eles in vGroups.items():
        gIgroup = igroup + ngroups #总体组号
        for ele in eles:
            nelems += 1
            ele.igroup = gIgroup
            ele.id = nelems
            if ele.igroup not in groupELes:
                groupELes[ele.igroup] = []
            groupELes[ele.igroup].append(ele)
            #调整单元节点编号
            for i in range(ele.nnode):
                ele.lnods[i] = ele.lnods[i] + npoints
    #添加多边形节点
    for inode,coord in voCoords.items():
        npoints += 1
        resCoords[npoints] = coord

    #写出到msh
    print('npoints=' + str(npoints))
    print('nelem  =' + str(nelems))
    print('ngroup =' + str(len(groupELes)))
    WriteFlaviaMsh(outputFilePath, resCoords, groupELes)
    print('group info:')
    writeCalcConfig(outputFolderPath, resCoords, groupELes)
    print('恭喜，生成成功！')       


if __name__ == '__main__':
    #读取从hm生成的msh文件,只能从三角形单元生成
    generateIGroups = [2]  #指定生成泰森多边形的分组，这些分组的单元必须是三角形，不能有双节点
    inputMshPath = r'tri.msh' #读取hm导出的Msh文件
    outputFilePath = r'voronoi.msh'  #输出的GID格式Msh文件
    outputFolderPath = r'.'            #输出的ele，cor文件夹目录


    mshReader = MshReader()
    mshReader.ReadHmMsh(inputMshPath)
    inieles= mshReader.elements
    iniCoords = mshReader.coords
    GenerateVoronoi(generateIGroups,outputFilePath,outputFolderPath,inieles,iniCoords)


