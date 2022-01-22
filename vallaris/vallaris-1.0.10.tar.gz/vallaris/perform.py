################# Vallaris Maps ##################
############## By : sattawat arab ###############
###### GIS Backend Engineer #########
########### i-bitz company limited ##############
##################### 2020 ######################

import time
import tempfile
import os
import json
import requests
from geopandas import GeoSeries
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
from vallaris.utils import *
from dotenv import load_dotenv
load_dotenv()


def setEnviron(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    
    try:
        msgBody = json.loads(parameter)
    except:
        msgBody = parameter

    try:
        GP_API_FEATURES_HOST = os.environ.get('GP_API_FEATURES_HOST', 'https://v2k-dev.vallarismaps.com/core/api/features')
        url = GP_API_FEATURES_HOST.split("/")[-4]
        Api_Key = msgBody["API-Key"]
        VallarisServer = GP_API_FEATURES_HOST

        if 'APIKey' in os.environ:
            del os.environ['APIKey']
        
        if 'VallarisServer' in os.environ:
            del os.environ['VallarisServer']
        
        os.environ["APIKey"] = Api_Key
        os.environ["VallarisServer"] = VallarisServer

    except:
        Api_Key = os.environ["APIKey"]
        VallarisServer = os.environ["VallarisServer"]

    return [Api_Key, VallarisServer]


def InputValue(storage, parameter):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter
    
    try:
        msgOption = msgBody
        input = msgOption['process']['inputs']['input'][0]['input']
        return input
    except Exception as e:
        print(e)
        input = False
        return input

def FileValue(storage, parameter):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        input = msgOption['process']['inputs']['input'][0]['input'][0]['value']
        file = str(input) + ".gpkg"
        return file
    except Exception as e:
        print(e)
        file = False
        return file

def FormatValue(storage, parameter):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter
    
    try:
        msgOption = msgBody
        format = msgOption['process']['inputs']['input'][0]['input'][0]['format']
        return format
    except Exception as e:
        print(e)
        format = False
        return format


def ParamValue(storage, parameter):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        param = msgOption['process']['inputs']['parameter'][0]['input']
        return param
    except Exception as e:
        print(e)
        param = False
        return param


def CollectionValue(storage, parameter):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter
    
    try:
        msgOption = msgBody
        collection = msgOption['process']['inputs']['input'][0]['input']
        dataset_id = collection[0]['value']
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]

        dataCollection = getData(storage, dataset_id, VallarisServer, Api_Key)

        if dataCollection != "something wrong":
            input = dataCollection
            return input

        else:
            input = False
            return input
    except Exception as e:
        print(e)
        input = False
        return input


def ExportFeatures(storage, parameter):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        collection = msgOption['id']
        dataset_id = collection
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]

        dataExport = getExport(storage, dataset_id, VallarisServer, Api_Key)

        if dataExport != "something wrong":
            return dataExport

        else:
            dataExport = False
            return dataExport

    except Exception as e:
        print(e)
        dataExport = False
        return dataExport


def CreateFeatures(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        collection = msgOption['id']
        data = msgOption['geojson']
        dataset_id = collection
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]
        data = msgOption['geojson']
        dirpath = tempfile.mkdtemp()
        with open(dirpath + '/data.json', 'w') as f:
            json.dump(data, f)

        pathFile = dirpath + '/data.json'
        dataImport = getImport(storage, dataset_id,
                               pathFile, VallarisServer, Api_Key)
        shutil.rmtree(dirpath)

        if dataImport != "something wrong":
            return dataImport

        else:
            dataImport = False
            return dataImport

    except Exception as e:
        print(e)
        dataImport = False
        return dataImport


def UpdateFeatures(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        dataset_id = msgOption['collectionId']
        features_id = msgOption['featuresId']
        data = msgOption['geojson']
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]
        dataEdit = editFeatures(storage, dataset_id,
                                features_id, data,  VallarisServer, Api_Key)

        if dataEdit != "something wrong":
            return dataEdit

        else:
            dataEdit = False
            return dataEdit

    except Exception as e:
        print(e)
        dataEdit = False
        return dataEdit


def DeleteFeatures(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        dataset_id = msgOption['collectionId']
        features_id = msgOption['featuresId']
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]
        dataDelete = delFeatures(
            storage, dataset_id, features_id,  VallarisServer, Api_Key)

        if dataDelete != "something wrong":
            return dataDelete

        else:
            dataDelete = False
            return dataDelete

    except Exception as e:
        print(e)
        dataDelete = False
        return dataDelete


def CreateCollection(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        title = msgOption['title']
        description = msgOption['title']
        itemType = msgOption['itemType']
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]

        dataNew = newCollection(
            storage, title, description, itemType, VallarisServer, Api_Key)

        if dataNew != "something wrong":
            return dataNew

        else:
            dataNew = False
            return dataNew

    except Exception as e:
        print(e)
        dataNew = False
        return dataNew


def UpdateCollection(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        dataset_id = msgOption['id']
        title = msgOption['title']
        description = msgOption['title']
        itemType = msgOption['itemType']
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]

        editImport = editCollection(
            storage, dataset_id, title, description, itemType, VallarisServer, Api_Key)

        if editImport != "something wrong":
            return editImport

        else:
            editImport = False
            return editImport

    except Exception as e:
        print(e)
        dataImport = False
        return dataImport


def DeleteCollection(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter
        
    try:
        msgOption = msgBody
        dataset_id = msgOption['id']
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]

        deleteData = delCollection(
            storage, dataset_id, VallarisServer, Api_Key)

        if deleteData != "something wrong":
            return deleteData

        else:
            deleteData = False
            return deleteData

    except Exception as e:
        print(e)
        deleteData = False
        return deleteData


def CreateTile(parameter, *args, **kwargs):
    storage = kwargs.get('storage', False)
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    try:
        msgOption = msgBody
        dataset_id = msgOption["data_filter"]['dataset_id']
        dataset_out = msgOption["data_filter"]['dataset_out']
        VallarisServer = os.environ["VallarisServer"]
        Api_Key = os.environ["APIKey"]

        tile = makeTile(
            storage, dataset_id, dataset_out, VallarisServer, Api_Key, parameter)

        if tile != "something wrong":
            return tile

        else:
            tile = False
            return tile

    except Exception as e:
        print(e)
        tile = False
        return tile


def ProcessSuccess(storage, parameter, msg, file_final):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    msgOption = msgBody
    _output = msgOption['process']['outputs'][0]['format']
    
    try :
        order = msgOption['process']['order']
    except :
        order = 1

    if "GeoJSON" in _output:
        _output = 'json'

    file_final = file_final
    layer = gpd.read_file(storage + '/' + file_final)
    layer.to_file(storage + '/' + str(_output) +
                  str(order) + ".gpkg", driver="GPKG")

    file_final_up = storage + '/' + str(_output) + str(order) + '.gpkg'
    out_msg = {
        "code": 200,
        "message": msg,
        "file": file_final_up
    }
    return json.dumps(out_msg)


def ProcessFail(storage, parameter, msg):
    try:
        msgBody = json.loads(parameter)["requestBody"]
    except:
        msgBody = parameter

    out_msg = {
        "code": 404,
        "message": msg,
        "file": "no data"
    }

    print("process failed")
    return json.dumps(out_msg)
