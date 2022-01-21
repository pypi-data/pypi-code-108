from nebula.graph import ttypes,GraphService
from nebula.ConnectionPool import ConnectionPool
from nebula.Client import GraphClient
from maintain_PlatoUtils import wrapNebula2Df
import os
import time
import json
import pandas as pd
from maintain_PlatoUtils import maintain_csv2platodb_A_uploadFile
from maintain_PlatoUtils import maintain_csv2platodb_B_submitSchema
from maintain_PlatoUtils import maintain_csv2platodb_C_import
import tqdm
import requests
from string import punctuation
import time
import requests

def addTokenForEntities(gClient,gDBName,nodeIdAttrList,tabuList=[],projectName="",email=""):
    
    if "csv2platodb" not in os.listdir("."):
        os.mkdir("csv2platodb")
        
    if len(projectName)==0:
        projectName="tmp_{}".format(int(time.time()*1000))
        os.mkdir("csv2platodb/{}".format(projectName))
    
    if len(tabuList)==0:
        tabuList=list(punctuation)+["“","”","‘","’","，","。"]
    
    # 构建节点和边的数据
    schemaVertex=[]
    schemaEdge=[]
    for nodeItdPairItem in nodeIdAttrList:
        
        nodeType=nodeItdPairItem.split(".")[0]
        nodeIdAttr=nodeItdPairItem.split(".")[1]
        
        tgtNameDf=wrapNebula2Df(gClient.execute_query("LOOKUP ON {nodeType} WHERE {nodeType}.{nodeIdAttr}!='不可能的名字' \
                                                        YIELD {nodeType}.{nodeIdAttr} AS tgtName".format(nodeType=nodeType,
                                                                                                          nodeIdAttr=nodeIdAttr)))
        srcTokenPairList=[]
        tokenInfoList=[]
        for tgtNameItem in tqdm.tqdm(tgtNameDf["tgtName"].values.flatten().tolist(),desc=nodeType):
            tgtNameItem=tgtNameItem.lower()
            for tgtNameTokenItem in tgtNameItem:
                if tgtNameTokenItem not in tabuList:
                    tokenInfoList.append({"Name":tgtNameTokenItem})
                srcTokenPairList.append({"headEntity":tgtNameTokenItem,"tailEntity":tgtNameTokenItem})
        srcTokenPairDf=pd.DataFrame(srcTokenPairList)
        tokenInfoDf=pd.DataFrame(tokenInfoList)
            
        tokenInfoDf.to_csv("csv2platodb/{}/tokenInfo_{}.csv".format(projectName,nodeType),index=None)
        srcTokenPairDf.to_csv("csv2platodb/{}/consistOfRel_{}.csv".format(projectName,nodeType),index=None)
        
        schemaVertex.append({ 
                                "file_name":"tokenInfo_{}.csv".format(projectName,nodeType),
                                "node_type":"Token",
                                "id_col":"Name", 
                                "csv2plato_attr_map":{ 
                                    "Name":"Name"
                                },
                                "attr_type_map":{ 
                                    "Name":"string"
                                }
                            })
        schemaEdge.append({
                                "file_name":"consistOfRel_{}.csv".format(projectName,nodeType),
                                "edge_type":"consistOf",
                                "src_type":nodeType,
                                "tgt_type":"Token",
                                "src_id":"headEntity",
                                "tgt_id":"tailEntity"
                            })
    # 构建数据schema
    VESchema={
        "gDBName":gDBName,
        "vertex":schemaVertex,
        "edge":schemaEdge,
        "email":email
    }
    if len(email)==0:
        VESchema.pop("email")
    
    with open("csv2platodb/{}/tokenInfo_{}.csv".format(projectName,nodeType),"w+",encoding="utf8") as VESchemaFile:
        json.dump(VESchema,VESchemaFile)
    
    print("本地文件生成")
    return VESchema
        
        

if __name__=="__main__":

    '''
    图数据库属性转节点
    '''
    # test
    gHost="9.135.95.249"
    gPort=13708
    gUser="root"
    gPassword="nebula"
    gDbName="post_skill_school_ianxu"
    
    # # product
    # gHost="10.99.218.40"
    # gPort=8080
    # gUser="root"
    # gPassword="nebula"
    # gDbName="company_product_field_musklin"
    
    projectName="school_token"
    
    nodeIdAttrList=["School.SchoolName"] # 节点.节点id属性

    Connection_pool = ConnectionPool(gHost, gPort,network_timeout=300000)
    gClient = GraphClient(Connection_pool)
    gClient.authenticate(gUser, gPassword)
    gClient.execute_query("USE {}".format(gDbName))
    gClient.set_space(gDbName)

    VESchema=addTokenForEntities(gClient,gDbName,nodeIdAttrList,projectName=projectName)
    
    fileServerUrl="http://9.135.95.249:8083/csv2platodb/upload"
    csv2platoFolderItem="csv2platodb/{}".format(projectName)
    
    fileList=[]
    for fileItem in tqdm.tqdm(os.listdir(csv2platoFolderItem),desc=csv2platoFolderItem):
        if fileItem.split(".")[1]=="csv":
            fileList.append(("csv",(fileItem,open(csv2platoFolderItem+"/"+fileItem,'rb'),"test/csv")))
        if fileItem.split(".")[1]=="json":
            fileList.append(("json",(fileItem,open(csv2platoFolderItem+"/"+fileItem,'rb'),"application/json")))
            
    response = requests.request("POST", fileServerUrl, files=fileList)

    print(response.json())
    print("123")
    
    