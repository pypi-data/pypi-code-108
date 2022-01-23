import pandas as pd
import json
import tqdm
import os
import requests
import http.client
import mimetypes
from codecs import encode
import numpy as np
import argparse
import joblib
from maintain_PlatoUtils.maintain_PlatoUtils import existTag,wrapNebula2Df,existEdge,delEdge,delVertex
import joblib
import sys
import os.path as osp

csv2platoDTypeDict={
    "object":"string",
    "float64":"double",
}

def evalDataType(myDf):
    '''
    分析DataFrame的属性的数据类型
    '''
    attrTypeDict=dict(
        (colItem,csv2platoDTypeDict.get(str(myDf[colItem].dtype),colItem))
        for colItem in myDf.columns
    )
    return attrTypeDict

def uploadFolder(dataFolder,platoUrl):
    
    from sys import _getframe
    from pathlib import Path
    frame = _getframe(1)
    curr_file = Path(frame.f_code.co_filename)
    a=str(curr_file.parent.joinpath(dataFolder).resolve())
    print(a)
    
    if "uploadSchema.json" in os.listdir(dataFolder):
        
        with open(os.path.join(dataFolder,"uploadSchema.json").replace("\\","/"),"r",encoding="utf8") as uploadSchemaFile:
            uploadSchemaJson=json.load(uploadSchemaFile)
        
        if "vertex" in uploadSchemaJson:
            for vertexTypeItem in uploadSchemaJson["vertex"]:
                filePath=vertexTypeItem["file_path"]
                uploadFile(filePath,platoUrl=platoUrl)
            
        if "edge" in uploadSchemaJson:
            for edgeTypeItem in uploadSchemaJson["edge"]:
                filePath=edgeTypeItem["file_path"]
                uploadFile(filePath,platoUrl=platoUrl)
    
def remakeRawSchema(rawSchemaJson,csvFolder="",gClient=None):
    '''
    数据需要已上传至服务器的data/csv文件夹内才能使用
    将上传至服务器的schema调整为即将上传至图数据库的schema
    同时，data/csv内的节点信息csv文件会增加newMadeSysID列
    schema数据如下：
    {
        "gDbName":"DemoSpace",
        "vertex":[
            {
                "cover_label":True,
                "file_name":"vertexData.csv",
                "node_type":"vertexClass",
                "id_col":"vertexIDColName",
                "csv2plato_attr_map":{
                    "csvAttr":"platoAttr"
                },
                "attr_type_map":{
                    "csvAttr":"platoAttrType"
                }
            },
            ......
        ],
        "edge":[
            {
                "cover_label":True,
                "file_name":"edgeInfo.csv",
                "edge_type":"edgeClass",
                "src_type":"srcClass1",
                "tgt_type":"tgtClass2",
                "src_id":"srcIdAttr",
                "tgt_id":"tgtIdAttr",
            },
            ......
        ]
    }
    '''
    ##########################################
    # vertex.cover_label
    # escape:同名不更新√
    # plus:同名仅更新属性不删除属性√
    # cover:同名直接覆盖属性×
    # ,delete:同名删除样本x
    # ,escape:不同名不处理×
    # ,cover:不同名删除×
    #
    # edge.cover_label
    # escape:同头尾节点不更新×
    # plus:同头尾节点仅更新属性不删除属性×
    # cover:同头尾节点直接覆盖属性×
    # ,delete:同头节点名删除样本x
    # ,escape:不同头节点名不处理×
    # ,cover:不同头节点名删除×
    #########################################

    if csvFolder[-1]=="/":
        csvFolder=csvFolder[:-1]
    
    for vertexI,_ in tqdm.tqdm(enumerate(rawSchemaJson["vertex"]),desc="vertex"):
        rawSchemaJson["vertex"][vertexI]["file_path"]=csvFolder+"/"+rawSchemaJson["vertex"][vertexI]["file_name"]
        csvDfItem=pd.read_csv(rawSchemaJson["vertex"][vertexI]["file_path"])
        csvDfItem[rawSchemaJson["vertex"][vertexI]["id_col"]]=csvDfItem[rawSchemaJson["vertex"][vertexI]["id_col"]].astype(str)
        vertexType=rawSchemaJson["vertex"][vertexI]["node_type"]
        csvDfItem["newMadeSysID"]=vertexType+"_"+csvDfItem[rawSchemaJson["vertex"][vertexI]["id_col"]].astype(str)

        coverLabel=rawSchemaJson["vertex"][vertexI].get("cover_label","escape,cover")
        vertexDataProcess=coverLabel.split(",")[0]
        vertexAttrProcess=coverLabel.split(",")[1]

        # 节点数据控制
        if vertexDataProcess=="cover":
            nodeType=rawSchemaJson["vertex"][vertexI]["node_type"]
            nodeIdAttr=rawSchemaJson["vertex"][vertexI]["id_col"]
            sysVertexSearchStr="LOOKUP ON {nodeType} WHERE {nodeType}.{nodeIdAttrKey}!='不可能的名字'".format(
                                                                                                                    nodeType=nodeType,
                                                                                                                    nodeIdAttrKey=nodeIdAttr
                                                                                                                )
            # print(sysVertexSearchStr)
            sysIdList=wrapNebula2Df(gClient.execute_query(sysVertexSearchStr)).values.flatten().tolist()
            delVertex(gClient,sysIdList)
        elif vertexDataProcess=="escape":
            pass
        
        # 节点属性控制
        if vertexAttrProcess=="escape":
            nodeType=rawSchemaJson["vertex"][vertexI]["node_type"]
            nodeIdAttr=rawSchemaJson["vertex"][vertexI]["id_col"]
            csvDfItem=pd.DataFrame([row for row in json.loads(csvDfItem.to_json(orient="records")) 
                                        if existTag(nodeType, nodeIdAttr, row[rawSchemaJson["vertex"][vertexI]["id_col"]],gClient)==False])
        elif vertexAttrProcess=="plus":
            
            nodeItemCInfoDf=csvDfItem.copy(deep=True)
            
            nodeType=rawSchemaJson["vertex"][vertexI]["node_type"]
            nodeIdAttr=rawSchemaJson["vertex"][vertexI]["id_col"]
            nodeIdList=nodeItemCInfoDf[rawSchemaJson["vertex"][vertexI]["id_col"]].values.flatten().tolist()
            
            searchBatch=32
            nodeItemGInfoDfList=[]
            for nodeIdI in range(0,len(nodeIdList),searchBatch):
                queryStrList=[]
                for nodeIdIItem in range(nodeIdI,min(nodeIdI+searchBatch,len(nodeIdList))):
                    queryStrItem="LOOKUP ON {nodeType} WHERE {nodeType}.{nodeIdAttr}=='{nodeIdVal}'| FETCH PROP ON {nodeType} $-.VertexID".format(nodeType=nodeType,
                                                                                                                                                nodeIdAttr=nodeIdAttr,
                                                                                                                                                nodeIdVal=nodeIdList[nodeIdIItem])
                    queryStrList.append(queryStrItem)
                queryStr=" UNION ".join(queryStrList)
                nodeItemGInfoDf=wrapNebula2Df(gClient.execute_query(queryStr))
                nodeItemGInfoDfList.append(nodeItemGInfoDf)
            nodeItemGInfoDf=pd.concat(nodeItemGInfoDfList)
            
            # print("nodeItemCInfoDf:",nodeItemCInfoDf.columns)
            # print("nodeItemGInfoDf:",nodeItemGInfoDf.columns)
            if nodeItemGInfoDf.shape[0]>0:
                for colItem in nodeItemCInfoDf.columns:
                    if colItem in nodeItemGInfoDf:
                        idAttrKey=rawSchemaJson["vertex"][vertexI]["id_col"]
                        if colItem !=  idAttrKey:
                            changedIdList=nodeItemCInfoDf.loc[(nodeItemCInfoDf[colItem].isna())|
                                                            (nodeItemCInfoDf[colItem]=="null")|
                                                            (nodeItemCInfoDf[colItem]==""),idAttrKey].values.flatten().tolist()

                            cIdDf=nodeItemCInfoDf.loc[nodeItemCInfoDf[idAttrKey].isin(changedIdList),idAttrKey]
                            gIdDf=nodeItemGInfoDf.loc[nodeItemGInfoDf[idAttrKey].isin(changedIdList),idAttrKey]
                            
                            # print(nodeItemCInfoDf.loc[nodeItemCInfoDf[idAttrKey].isin(gIdDf),:])
                            # print(nodeItemGInfoDf.loc[nodeItemGInfoDf[idAttrKey].isin(gIdDf),:])

                            nodeItemCInfoDf.loc[nodeItemCInfoDf[idAttrKey].isin(gIdDf),colItem]=\
                                nodeItemGInfoDf.loc[nodeItemGInfoDf[idAttrKey].isin(gIdDf),colItem].values
            
            csvDfItem=nodeItemCInfoDf
        elif vertexAttrProcess=="cover":
            pass
        # print("csvDfItem:",csvDfItem.head())
        
        csvDfItem.to_csv(rawSchemaJson["vertex"][vertexI]["file_path"],index=None)
        rawSchemaJson["vertex"][vertexI]["old_id_col"]=rawSchemaJson["vertex"][vertexI]["id_col"]
        rawSchemaJson["vertex"][vertexI]["id_col"]="newMadeSysID"
        if "csv2plato_attr_map" not in rawSchemaJson["vertex"][vertexI] or len(rawSchemaJson["vertex"][vertexI]["attr_type_map"])==0: # 若没有属性映射则进行同名映射
            vertexItemDf=pd.read_csv(rawSchemaJson["vertex"][vertexI]["file_path"])
            rawSchemaJson["vertex"][vertexI]["csv2plato_attr_map"]=dict((colItem,colItem) for colItem in vertexItemDf.columns)
        if "attr_type_map" not in rawSchemaJson["vertex"][vertexI] or len(rawSchemaJson["vertex"][vertexI]["attr_type_map"])==0: # 若没有属性数据类型约束则自动生成
            vertexItemDf=pd.read_csv(rawSchemaJson["vertex"][vertexI]["file_path"])
            CPAttrTypeDict=evalDataType(vertexItemDf)
            rawSchemaJson["vertex"][vertexI]["attr_type_map"]=CPAttrTypeDict

    for edgeI,_ in tqdm.tqdm(enumerate(rawSchemaJson["edge"]),desc="edge"):
        rawSchemaJson["edge"][edgeI]["file_path"]=csvFolder+"/"+rawSchemaJson["edge"][edgeI]["file_name"]
        csvDfItem=pd.read_csv(rawSchemaJson["edge"][edgeI]["file_path"])
        srcType=rawSchemaJson["edge"][edgeI]["src_type"]
        tgtType=rawSchemaJson["edge"][edgeI]["tgt_type"]
        edgeType=rawSchemaJson["edge"][edgeI]["edge_type"]
        srcIdAttr=rawSchemaJson["edge"][edgeI]["src_id"]
        tgtIdAttr=rawSchemaJson["edge"][edgeI]["tgt_id"]
        csvDfItem[rawSchemaJson["edge"][edgeI]["src_id"]]=csvDfItem[rawSchemaJson["edge"][edgeI]["src_id"]].astype(str).apply(lambda row:srcType+"_"+row if srcType+"_" not in row else row) # 同src的newMadeSysID对应
        csvDfItem[rawSchemaJson["edge"][edgeI]["tgt_id"]]=csvDfItem[rawSchemaJson["edge"][edgeI]["tgt_id"]].astype(str).apply(lambda row:tgtType+"_"+row if tgtType+"_" not in row else row) # 同tgt的newMadeSysID对应

        coverLabel=rawSchemaJson["edge"][edgeI].get("cover_label","escape,escape,cover")
        headEdgeDataProcess,tailEdgeDataProcess,edgeAttrDataProcess=coverLabel.split(",")

        # 头节点边样本控制
        if headEdgeDataProcess=="cover":
            oldSysId=wrapNebula2Df(gClient.execute_query("LOOKUP ON {srcType} WHERE {srcType}.{srcIdAttr}!='不可能的名字'".format(
                                                                                                                                srcType=srcType,
                                                                                                                                srcIdAttr=srcIdAttr
                                                                                                                            ))).values.tolist()
            for batchI in tqdm.tqdm(range(0,len(oldSysId),1024),desc="head edges control-cover"):
                oldSysIdGroup=[str(oldSysIdItem) for oldSysIdItem in oldSysId[batchI:batchI+1024]]
                delEdge(gClient,oldSysIdGroup)
        elif headEdgeDataProcess=="escape":
            pass

        # 尾节点边样本控制
        if tailEdgeDataProcess=="cover":
            oldSysId=wrapNebula2Df(gClient.execute_query("LOOKUP ON {tgtType} WHERE {tgtType}.{tgtIdAttr}!='不可能的名字'".format(
                                                                                                                                tgtType=tgtType,
                                                                                                                                tgtIdAttr=tgtIdAttr
                                                                                                                            ))).values.tolist()
            for batchI in tqdm.tqdm(range(0,len(oldSysId),1024),desc="tail edges control-cover"):
                oldSysIdGroup=[str(oldSysIdItem) for oldSysIdItem in oldSysId[batchI:batchI+1024]]
                delEdge(gClient,oldSysIdGroup)
        elif tailEdgeDataProcess=="escape":
            pass

        # 边属性控制
        if edgeAttrDataProcess=="escape":
            stList=csvDfItem.loc[:,[srcIdAttr,tgtIdAttr]].values.tolist()
            newStList=[]
            csvDfItemList=[]
            batchSize=1024
            for stPairI in tqdm.tqdm(range(0,len(stList),batchSize),desc="edge attr control-escape"):
                srcItemType=[stPairItem[0].split("_")[0] for stPairItem in stList[stPairI:stPairI+batchSize]]
                srcItemIdValList=["_".join(stPairItem[0].split("_")[1:]) for stPairItem in stList[stPairI:stPairI+batchSize]]
                tgtItemType=[stPairItem[1].split("_")[0] for stPairItem in stList[stPairI:stPairI+batchSize]]
                tgtItemIdValList=["_".join(stPairItem[1].split("_")[1:]) for stPairItem in stList[stPairI:stPairI+batchSize]]
                for stPairII in range(len(tgtItemIdValList)):
                    srcItemIdKey=srcIdAttr
                    srcItemIdVal=srcItemIdValList[stPairII]
                    tgtItemIdKey=tgtIdAttr
                    tgtItemIdVal=tgtItemIdValList[stPairII]
                    if existEdge(srcItemType,srcItemIdKey,srcItemIdVal,tgtItemType,tgtItemIdKey,tgtItemIdVal,edgeType,gClient)==False:
                        srcKV="{}_{}".format(srcItemType,srcItemIdVal)
                        tgtKV="{}_{}".format(tgtItemIdKey,tgtItemIdVal)
                        newStList.append([srcKV,tgtKV])
                        csvDfItemRow={srcIdAttr:srcKV,tgtIdAttr:tgtKV}
                        csvDfItemList.append(csvDfItemRow)
            csvDfItem=pd.DataFrame(csvDfItemList)
        elif edgeAttrDataProcess=="plus":
            htList=json.loads(csvDfItem.to_json(orient="records"))
            newHTList=[]
            htSearchBatchSize=128
            for htI in tqdm.tqdm(range(0,len(htList),htSearchBatchSize),desc="edge attr control-plus"):
                queryStrList=[]
                for htItem in htList[htI:htI+htSearchBatchSize]:
                    htItem=htList[htI]
                    srcIdVal=htItem[srcIdAttr]
                    tgtIdVal=htItem[tgtIdAttr]
                    attrList=[keyItem for keyItem in htItem if keyItem not in [srcIdAttr,tgtIdAttr]]
                    attrGroupStr=",".join(["{edgeType}.{attrName} AS {attrName}".format(edgeType=edgeType,attrName=attrItem) for attrItem in attrList])
                    queryItemStr="LOOKUP ON {headType} WHERE {headType}.{headIdAttrKey}=='{headIdAttrVal}'|\
                                            GO FROM $-.VertexID OVER {edgeType} WHERE $$.{tailType}.{tailIdAttrKey}=='{tailIdAttrVal}'\
                                                YIELD {attrGroup}".format(
                                                    headType=srcType,
                                                    headIdAttrKey=srcIdAttr,
                                                    headIdAttrVal=srcIdVal,
                                                    edgeType=edgeType,
                                                    tailType=tgtType,
                                                    tailIdAttrKey=tgtIdAttr,
                                                    tailIdAttrVal=tgtIdVal,
                                                    attrGroup=attrGroupStr
                                                )
                    queryStrList.append(queryItemStr)
                queryStr=" UNION ".format(queryStrList)
                htItemDf=wrapNebula2Df(gClient.execute_query(queryStr))
                newHTItemList=json.loads(htItemDf.to_json(orient="records"))
                for keyItem in attrList:
                    if newHTItemList[0][keyItem] is None or np.nan(newHTItemList[0][keyItem]) or newHTItemList[0][keyItem]=="null":
                        newHTItemList[0][keyItem]=htItem[keyItem]
                newHTList+=newHTItemList
            csvDfItem=pd.DataFrame(newHTList)
        elif edgeAttrDataProcess=="cover":
            pass

        csvDfItem.to_csv(rawSchemaJson["edge"][edgeI]["file_path"],index=None)
        if "csv2plato_attr_map" not in rawSchemaJson["edge"][edgeI] or len(rawSchemaJson["edge"][edgeI]["attr_type_map"])==0:
            edgeItemDf=pd.read_csv(rawSchemaJson["edge"][edgeI]["file_path"])
            rawSchemaJson["edge"][edgeI]["csv2plato_attr_map"]=dict((colItem,colItem) for colItem in edgeItemDf.columns)
        if "attr_type_map" not in rawSchemaJson["edge"][edgeI] or len(rawSchemaJson["edge"][edgeI]["attr_type_map"])==0:
            edgeItemDf=pd.read_csv(rawSchemaJson["edge"][edgeI]["file_path"])
            CPAttrTypeDict=evalDataType(edgeItemDf)
            rawSchemaJson["edge"][edgeI]["attr_type_map"]=CPAttrTypeDict
    
    return rawSchemaJson

def buildGraphDB(gClient,uploadSchemaJson,realDbName=None,force=False):
    
    typeDefaultDict={
        "string":"null",
        "double":0.0,
        "int":0
    }
    
    if force==False:
        isexist="IF EXIST"
    else:
        isexist=""

    if realDbName is None:
        realDbName=uploadSchemaJson["gDbName"]
    
    queryList=["DROP SPACE {} {};CREATE SPACE IF NOT EXISTS {}".format(isexist,realDbName,realDbName)]
    
    for vertexInfo in uploadSchemaJson["vertex"]:
        attrNameTypeGroup=[(vertexInfo["csv2plato_attr_map"][attrKeyItem],
                            vertexInfo["attr_type_map"].get(attrKeyItem,"string"))
                           for attrKeyItem in vertexInfo["csv2plato_attr_map"]]
        attrNameTypeGroupStr=",".join([" ".join(groupItem)+" DEFAULT {}".format(typeDefaultDict[groupItem[1]]) 
                                       for groupItem in attrNameTypeGroup])
        queryItemStr="CREATE TAG IF NOT EXISTS {vertexType}({attrGroupStr})".format(
                                                                    vertexType=vertexInfo["node_type"],
                                                                    attrGroupStr=attrNameTypeGroupStr
                                                                    )
        indexQueryItemStr="CREATE TAG INDEX IF NOT EXISTS \
                            {tagTypeLower}_{tagIndexLower}_index ON {tagType}({vertexIdAttr});\
                            REBUIL TAG INDEX {tagTypeLower}_{tagIndexLower}_index OFFLINE".format(
                                                                        tagType=vertexInfo["node_type"],
                                                                        vertexIdAttr=vertexInfo["id_col"],
                                                                        tagTypeLower=vertexInfo["node_type"].lower(),
                                                                        tagIndexLower=vertexInfo["id_col"].lower()
                                                                    )
        queryList.append(queryItemStr)
        queryList.append(indexQueryItemStr)
        
    for edgeInfo in uploadSchemaJson["edge"]:
        attrNameTypeGroup=[(edgeInfo["csv2plato_attr_map"][attrKeyItem],
                            edgeInfo["attr_type_map"].get(attrKeyItem,"string"))
                           for attrKeyItem in edgeInfo["csv2plato_attr_map"]]
        attrNameTypeGroupStr=",".join([",".join(groupItem)+" DEFAULT {}".format(typeDefaultDict[groupItem[1]])
                                       for groupItem in attrNameTypeGroup])
        queryItemStr="CREATE EDGE IF NOT EXISTS {edgeType}({attrGroupStr})".format(
                                                                    edgeType=edgeInfo["edge_type"],
                                                                    attrGroupStr=attrNameTypeGroupStr
                                                                    )
        queryList.append(queryItemStr)
    
    queryStr=";".join(queryList)
    gClient.execute_query(queryStr)

def uploadFile(filepath,platoUrl="http://9.135.95.249:7001"):

    url = platoUrl+"/api/files/upload"

    newFilePath=filepath[:filepath.index(".csv")]+"_copy.csv"
    pd.read_csv(filepath).to_csv(newFilePath,header=None,index=None)
    dataList = []
    boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=filename; filename={0}'.format(newFilePath)))

    fileType = mimetypes.guess_type(newFilePath)[0] or 'application/octet-stream'
    dataList.append(encode('Content-Type: {}'.format(fileType)))
    dataList.append(encode(''))

    with open(newFilePath, 'rb') as f:
        dataList.append(f.read())
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=Content-Disposition;'))

    dataList.append(encode('Content-Type: {}'.format('text/plain')))
    dataList.append(encode(''))

    dataList.append(encode("form-data"))
    dataList.append(encode('--' + boundary))
    dataList.append(encode('Content-Disposition: form-data; name=name;'))
    body = b'\r\n'.join(dataList)

    headers = {
        'Proxy-Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': '*/*',
        'Origin': platoUrl,
        'Referer': platoUrl+'/import',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': '_ga=GA1.1.152281212.1620638476; _gid=GA1.1.1165891708.1630551473; x-client-ssid=17ba9820824-91dabf2075180054237c14cb90d316c04da7064c; x-host-key-front=17ba982086f-036361ce77df67838d947d8c522a9c2ecc4fe227; x-host-key-ngn=17ba9820824-8f6fc182b3bf107c56e7f4e98120e8d99fecabb3; Hm_lvt_b9cb5b394fd669583c13f8975ca64ff0=1628591085,1629950390,1630551473,1630636476; locale=ZH_CN; nsid=f4a441a23dae744c54b8f96960a04ee2; nh=10.99.218.40:8080; nu=root; np=nebula; Hm_lpvt_b9cb5b394fd669583c13f8975ca64ff0=1630636498; _gat_gtag_UA_60523578_4=1',
        'Content-type': 'multipart/form-data; boundary={}'.format(boundary)
    }

    response = requests.request("POST", url, headers=headers, data=body)

    print(response.text)

if __name__=="__main__":
    
    dataFolder="csv2platodb/attr2Vertex_1629250000"
    platoUrl="http://9.135.95.249:7001"
    # platoUrl="http://10.99.218.40:8081"
    
    uploadFolder(dataFolder,platoUrl)
    
    print("finished")
                
