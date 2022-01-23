import networkx as nx
import tensorflow as tf
import random
import tqdm
import pandas as pd
import numpy as np
from maintain_PlatoUtils.maintain_PlatoUtils import wrapNebula2Df
from gensim.models import Word2Vec

import stellargraph as sg
from stellargraph import datasets,IndexedArray
from stellargraph.layer import GraphSAGE, link_classification, HinSAGE,DeepGraphInfomax
from sklearn.model_selection import train_test_split
from stellargraph.data import UnsupervisedSampler,BiasedRandomWalk
from stellargraph.mapper import Node2VecNodeGenerator,Node2VecLinkGenerator
from stellargraph.layer import Node2Vec

from nebula.graph import ttypes,GraphService
from nebula.ConnectionPool import ConnectionPool
from nebula.Client import GraphClient

def downloadGraph(gClient,subGraph=[{"head":{"type":"Company","keyAttr":"CompanyName"},
                                        "tail":{"type":"Field","keyAttr":"FieldName"},
                                        "edgeType":["belongTo"]}],space="post_skill_school_ianxu"):
    totalG=None
    if len(subGraph)>0:
        gClient.execute_query("USE {}".format(space))
        totalHtDfList=[]
        for triItem in subGraph:
            headType=triItem["head"]["type"]
            headKeyAttr=triItem["head"]["keyAttr"]
            tailType=triItem["tail"]["type"]
            tailKeyAttr=triItem["tail"]["keyAttr"]
            if len(triItem["edgeType"])>0:
                edgeTypeGroupStr=",".join(triItem["edgeType"])
            else:
                edgeTypeGroupStr="*"
            subGraphSearchStr="LOOKUP ON {headType} WHERE {headType}.{headKeyAttr}!='不可能的名字'|\
                                    GO FROM $-.VertexID OVER {edgeTypeGroup} YIELD \
                                        '{headType}_'+$^.{headType}.{headKeyAttr} AS srcName,\
                                        '{tailType}_'+$$.{tailType}.{tailKeyAttr} AS tgtName".format(
                                            headType=headType,headKeyAttr=headKeyAttr,
                                            tailType=tailType,tailKeyAttr=tailKeyAttr,
                                            edgeTypeGroup=edgeTypeGroupStr
                                        )
            
            htDfItem=wrapNebula2Df(gClient.execute_query(subGraphSearchStr))
            
            if htDfItem.shape[0]>0:
                htDfItem.dropna(inplace=True)
                totalHtDfList.append(htDfItem)
                
        if len(totalHtDfList)>0:
            totalHtDf=pd.concat(totalHtDfList)
            totalHtList=totalHtDf.values.tolist()
        
            random.seed(15)
            totalG=nx.from_edgelist(totalHtList)
            
    return totalG
    

def graphEmbedding(gClient,subGraph=[{"head":{"type":"Company","keyAttr":"CompanyName"},
                                        "tail":{"type":"Field","keyAttr":"FieldName"},
                                        "edgeType":["belongTo"]}],space="post_skill_school_ianxu",
                   model="DeepWalk",vecSize=128,totalG=None):
    if totalG is not None:
        totalG=downloadGraph(gClient,subGraph=subGraph,space=space)
    myW2VModel=None
    for nodeItem in totalG.nodes:
        totalG.nodes[nodeItem]["feature"]=np.random.random([vecSize,])
    if model=="DeepWalk":
        walk_number = 100
        walk_length = 15
        
        totalSGG=sg.StellarGraph.from_networkx(totalG, node_features="feature")
        walker = BiasedRandomWalk(
                    totalSGG,
                    n=walk_number,
                    length=walk_length,
                    p=1,q=1
                )
        walks = walker.run(totalSGG.nodes())
        
        myW2VModel=Word2Vec(walks,vector_size=vecSize,epochs=5)
            
    return myW2VModel

            
if __name__=="__main__":

    gHost="9.135.95.249"
    gPort=13708
    gUser="root"
    gPassword="nebula"
    gSpace="company_product_field_musklin"

    srcConnection_pool = ConnectionPool(gHost, gPort,network_timeout=300000)
    gClient = GraphClient(srcConnection_pool)
    gClient.authenticate(gUser, gPassword)
    gClient.execute_query("use {}".format(gSpace))

    myEmbModel=graphEmbedding(gClient,subGraph=[{"head":{"type":"Post","keyAttr":"PostName"},
                                                    "tail":{"type":"Skill","keyAttr":"SkillName"},
                                                    "edgeType":["contain"]}],
                                                space="post_skill_school_ianxu",model="DeepWalk",
                                                batch_size=128)
    
    print(123)
