################# Vallaris Maps ##################
############## By : sattawat arab ###############
###### GIS Backend Engineer #########
########### i-bitz company limited ##############
##################### 2020 ######################

import time
import tempfile
import os
import shutil
import json
import requests
from geopandas import GeoSeries
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
from shapely.geometry import Polygon


def getData(storage, dataset_id, VallarisServer, Api_Key):
    try:
        dir = tempfile.mkdtemp()
        local_filename = dir + "/" + str(dataset_id) + ".geojson"
        
        try: 
            url = VallarisServer + "/1.0-beta/collections/" + str(dataset_id)+"/items/streaming"

            payload = {}
            headers = {
                'API-Key': Api_Key
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            print(response)
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes,
                                unit='iB', unit_scale=True)

            with open(local_filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()

            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")

                if not os.path.exists(dir):
                    shutil.rmtree(dir)

                return "something wrong"

            else:
                readdata = gpd.read_file(local_filename, encoding='utf-8')
                readdata.to_file(storage + '/' + dataset_id +
                                '.gpkg', driver="GPKG")

                if not os.path.exists(dir):
                    shutil.rmtree(dir)

                return storage + '/' + dataset_id + '.gpkg'
        except:
            url = VallarisServer + "/core/api/features/1.0-beta/collections/" + \
                str(dataset_id)+"/items/streaming"
            payload = {}
            headers = {
                'API-Key': Api_Key
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            print(response)
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes,
                                unit='iB', unit_scale=True)

            with open(local_filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()

            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")

                if not os.path.exists(dir):
                    shutil.rmtree(dir)

                return "something wrong"

            else:
                readdata = gpd.read_file(local_filename, encoding='utf-8')
                readdata.to_file(storage + '/' + dataset_id +
                                '.gpkg', driver="GPKG")

                if not os.path.exists(dir):
                    shutil.rmtree(dir)

                return storage + '/' + dataset_id + '.gpkg'


    except Exception as e:
        print(e)
        return 'something wrong'


def getExport(storage, dataset_id, VallarisServer, Api_Key):

    try:
        dir = tempfile.mkdtemp()
        local_filename = dir + "/" + str(dataset_id) + ".geojson"
        url = VallarisServer + "/core/api/features/1.0-beta/collections/" + \
            str(dataset_id)+"/items/streaming"
        payload = {}
        headers = {
            'API-Key': Api_Key
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes,
                            unit='iB', unit_scale=True)
        with open(local_filename, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong")

            if not os.path.exists(dir):
                shutil.rmtree(dir)

            return "something wrong"

        else:
            read_file = gpd.read_file(
                dir + '/' + dataset_id + '.geojson', encoding='utf-8')
            read_file.to_file(storage + '/' + dataset_id +
                              '.geojson', encoding='utf-8', driver="GeoJSON")

            if not os.path.exists(dir):
                shutil.rmtree(dir)

            return storage + '/' + dataset_id + '.geojson'

    except Exception as e:
        print(e)
        return 'something wrong'


def newCollection(storage, title, description, itemType, VallarisServer, Api_Key):
    try:
        url = VallarisServer + "/core/api/features/1.0-beta/collections"

        payload = json.dumps({
            "title": title,
            "description": description,
            "extent": {
                "spatial": {
                    "bbox": [
                        [
                            -180,
                            -90,
                            180,
                            90
                        ]
                    ],
                    "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                },
                "temporal": {
                    "interval": [
                        []
                    ],
                    "trs": "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"
                }
            },
            "itemType": itemType,
            "crs": [
                "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            ],
            "links": [
                {
                    "href": "http://data.example.org/collections/1/items",
                    "rel": "items",
                    "type": "application/geo+json",
                    "title": title
                }
            ],
            "tileConfig": {}
        })

        headers = {
            'API-Key': Api_Key,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        out_data = response.text

        return out_data

    except Exception as e:
        print(e)
        return 'something wrong'


def editCollection(storage, dataset_id, title, description, itemType, VallarisServer, Api_Key):
    try:
        url = VallarisServer + \
            "/core/api/features/1.0-beta/collections/" + str(dataset_id)
        payload = json.dumps({
            "title": title,
            "description": description,
            "extent": {
                "spatial": {
                    "bbox": [
                        [
                            -180,
                            -90,
                            180,
                            90
                        ]
                    ],
                    "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                },
                "temporal": {
                    "interval": [
                        []
                    ],
                    "trs": "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"
                }
            },
            "itemType": itemType,
            "crs": [
                "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            ],
            "public": False,
            "tileConfig": {},
            "links": [
                {
                    "href": "http://data.example.org/collections/1/items",
                    "rel": "items",
                    "type": "application/geo+json",
                    "title": title
                }
            ]
        })
        headers = {
            'API-Key': Api_Key,
            'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        out_data = response.text
        return out_data

    except Exception as e:
        print(e)
        return 'something wrong'


def delCollection(storage, dataset_id, VallarisServer, Api_Key):
    try:
        url = VallarisServer + \
            "/core/api/features/1.0-beta/collections/" + str(dataset_id)
        payload = {}
        headers = {
            'API-Key': Api_Key
        }

        response = requests.request(
            "DELETE", url, headers=headers, data=payload)
        out_data = response.text
        return out_data
    except Exception as e:
        print(e)
        return 'something wrong'


def getImport(storage, dataset_id, pathFile,  VallarisServer, Api_Key):
    try:
        dir = tempfile.mkdtemp()
        gdata = gpd.read_file(pathFile, encoding='utf-8')
        crt = len(gdata)
        print('total : ' + str(crt))
        max = 10
        crt2 = crt//max
        for i in range(0, crt2+1):
            st = 0 + (i*max)
            end = max + (i*max)
            out_data = gdata[st:end]
            crt_out_data = len(out_data)

            if crt_out_data < max:
                loop = end - (max - crt_out_data)
            else:
                loop = end

            out_data.to_file(dir + '/' + dataset_id + '_.geojson',
                             encoding='utf-8', driver="GeoJSON", ensure_ascii=False)

            with open(dir + '/' + dataset_id + '_.geojson', encoding='utf-8') as f:
                data = json.load(f)

            data_get = json.dumps(data, ensure_ascii=False)

            data2 = str(data_get).replace("'", '"')
            try:
                data3 = str(data2).replace("None", '""')
            except:
                data3 = data2

            url = VallarisServer + "/core/api/features/1.0-beta/collections/"+dataset_id+"/items"
            payload = str(data3)
            headers = {
                'API-Key': Api_Key,
                'Content-Type': 'application/json'
            }
            response = requests.request(
                "POST", url, headers=headers, data=payload.encode('utf-8'))
            # print(response.text)

            try:
                res_json = response.json()
                res_code = res_json['code']
            except:
                res_code = False

            if res_code != False:
                # print(res_code)
                print('import error: ' + str(loop))
                if not os.path.exists(storage + '/dataInvalid'):
                    os.makedirs(storage + '/dataInvalid')
                shutil.copy(dir + '/' + dataset_id + '_.geojson', storage + '/dataInvalid/' +
                            dataset_id + '_' + str(loop-max) + '_' + str(loop)+'.geojson')
                os.remove(dir + '/' + dataset_id + '_.geojson')
            else:
                os.remove(dir + '/' + dataset_id + '_.geojson')
                print('import success : ' + str(loop))

        if not os.path.exists(dir):
            shutil.rmtree(dir)

        return 'import success'

    except Exception as e:
        print(e)
        return 'something wrong'


def editFeatures(storage, dataset_id, features_id, data,  VallarisServer, Api_Key):

    try:
        url = VallarisServer + "/core/api/features/1.0-beta/collections/" + \
            str(dataset_id) + "/items/" + str(features_id)
        payload = json.dumps(data)
        headers = {
            'API-Key': Api_Key,
            'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        out_data = response.text
        return out_data

    except Exception as e:
        print(e)
        return 'something wrong'


def delFeatures(storage, dataset_id, features_id,  VallarisServer, Api_Key):

    try:
        url = VallarisServer + "/core/api/features/1.0-beta/collections/" + \
            str(dataset_id) + "/items/" + str(features_id)

        payload = {}
        headers = {
            'API-Key': Api_Key,
            'Content-Type': 'application/json'
        }

        response = requests.request(
            "DELETE", url, headers=headers, data=payload)
        out_data = response.text
        return out_data

    except Exception as e:
        print(e)
        return 'something wrong'


def makeTile(storage, dataset_id, dataset_out, VallarisServer, Api_Key, parameter):
    try:
        url = VallarisServer + \
            "/core/api/processes/vallaris/214bffaba098493005c5/" + \
            str(dataset_id)

        payload = json.dumps(parameter)
        headers = {
            'API-Key': Api_Key,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        out_data = response.text
        return out_data

    except Exception as e:
        print(e)
        return 'something wrong'
