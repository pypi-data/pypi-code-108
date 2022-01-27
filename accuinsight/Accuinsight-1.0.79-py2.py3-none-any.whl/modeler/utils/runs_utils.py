# progressbar in boto3
import threading
import sys
import math

class ProgressPercentage(object):
    def __init__(self, client, bucket, filename):
        self._filename = filename
        self._size = client.head_object(Bucket=bucket, Key=filename).get('ContentLength')
        self._seen_so_far = 0
        self._lock = threading.Lock()
    
    def __call__(self, bytes_amount):
        def convertSize(size):
            if (size == 0):
                return '0B'
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(size,1024)))
            p = math.pow(1024,i)
            s = round(size/p,2)
            return '%.2f %s' % (s,size_name[i])

        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            done = int(50 * self._seen_so_far / self._size)
            sys.stdout.write(
                    "\r[%s%s] %s/%s  (%.2f%%)        " % (
                    '=' * done, ' ' * (50-done) , convertSize(self._seen_so_far), convertSize(self._size),
                    percentage))

            sys.stdout.flush()

# get awsInfo from datacatalog
import os
import json
from pathlib import Path
from collections import OrderedDict
import requests


def get_aws_info(sub_path):
    host = 'https://accuinsight-dev.cloudz.co.kr/datacatalogapi/'
    
    headers = {'Content-Type': 'application/json', 'userid': 'bigdata_poc'} # 2차 고도화 예정
    
    url = host + sub_path
    
    response = requests.request("GET", url, headers=headers, verify=False)
    awsInfo = json.loads(response.content)
    
    connectInfo = OrderedDict()
    
    connectInfo['my_access_key'] = awsInfo['connection']['credential']['accessKey']
    connectInfo['my_secret_key'] = awsInfo['connection']['credential']['secretKey']
    connectInfo['endpoint'] = awsInfo['connection']['url']
    
    splitEndpoint = awsInfo['location'].split('/')[2:]

    connectInfo['region'] = awsInfo['connection']['url'].split('.')[1]
    connectInfo['bucket_type'] = awsInfo['connection']['type']
    connectInfo['bucket_name'] = splitEndpoint[0]
    connectInfo['file_path'] = os.path.join(*splitEndpoint[1:])
    connectInfo['file_name'] = splitEndpoint[-1]
    connectInfo['file_type'] = awsInfo['dataSourceType']
    connectInfo['file_delim'] = awsInfo['dataSourceDelimiter']
    
    return(connectInfo)
