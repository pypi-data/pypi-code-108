import requests
import os
import time

def uploadFile(fileDict,platoServerAPI):
    '''
    fileDict:{"csv":["path/xxx1.csv","path/xxx2.csv",...],"json":"xxx.json"}
    platoServerAPI:ip:port
    '''

    url = "http://{}/csv2platodb/upload".format(platoServerAPI)

    csvFileList=[
        ('csv',(csvFilePathItem.split("/")[-1],open(csvFilePathItem,'rb'),'text/csv'))
    for csvFilePathItem in fileDict["csv"]]
    jsonFileList=[
        ('json',(fileDict["json"].split("/")[-1],open(fileDict["json"],'rb'),'application/json'))
    ]
    files=csvFileList+jsonFileList

    response = requests.request("POST", url, files=files)

    print(response.text)
