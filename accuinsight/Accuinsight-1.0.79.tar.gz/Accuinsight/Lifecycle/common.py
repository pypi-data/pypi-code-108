import os
import sys
import json
import logging
import time
import datetime
from collections import OrderedDict

import boto3
from hdfs3 import HDFileSystem
from Accuinsight.modeler.core.LcConst import LcConst
from Accuinsight.modeler.core.LcConst.LcConst import ENV_JUPYTER_HOME_DIR
from Accuinsight.modeler.utils.runs_utils import ProgressPercentage
from Accuinsight.modeler.clients.modeler_api import WorkspaceRestApi
from Accuinsight.modeler.utils.os_getenv import get_os_env, get_current_notebook
from Accuinsight.modeler.entities.alarm import Alarm


class Common(object):
    def __init__(self):
        env_value = get_os_env('ENV')

        self.StorageInfo = None
        self.target_name = None
        self.save_path = None
        self.endpoint = None
        self.thresholds = None
        self.hook_url = None
        self.message = None
        self.feature_name = None
        self.data = None
        self.user_id = None
        self.storage_info_from_set = OrderedDict()
        self.workspace_alarm_api = WorkspaceRestApi(env_value[LcConst.BACK_END_API_URL],
                                                    env_value[LcConst.BACK_END_API_PORT],
                                                    env_value[LcConst.BACK_END_API_URI])
        self.workspace_alarm = Alarm()

        self.notebook_info = get_current_notebook()

    def set_storage(self,
                    access_key=None,  # aws-s3
                    secret_key=None,  # aws-s3
                    region=None,  # aws-s3
                    bucket_name=None,  # aws-s3
                    hdfs_uri=None,  # pipeline-hdfs
                    file_path=None,  # common
                    target=None,  # common
                    save_json=False,  # common - if it is TRUE, saving a storage information as a json file.
                    save_path=None  # common - if save_path is not None, the json file is saved in this path.
                    ):

        if target is None:
            raise ValueError('target을 입력해주시기 바랍니다.')

        ## make a directory for saving json file
        save_prefix = None
        if save_json:
            save_prefix_run = os.path.join(ENV_JUPYTER_HOME_DIR, 'runs')
            if not os.path.isdir(save_prefix_run):
                try:
                    os.mkdir(save_prefix_run)
                except:
                    pass
            save_prefix = os.path.join(save_prefix_run, 'storage-info-json')
            if not os.path.isdir(save_prefix):
                try:
                    os.mkdir(save_prefix)
                except:
                    pass

        ### HDFS
        if hdfs_uri is not None:
            storage_type = 'hdfs'

            split_1 = hdfs_uri.split('//')[1].split('/')
            split_2 = [i.split(':') for i in split_1 if ':' in i][0]

            self.storage_info_from_set['host'] = split_2[0]
            self.storage_info_from_set['port'] = split_2[1]
            self.storage_info_from_set['filePath'] = os.path.join('/', *split_1[1:])
            self.storage_info_from_set['target'] = target

        ### AWS - S3
        elif bucket_name is not None:
            storage_type = 's3'

            self.storage_info_from_set['myAccessKey'] = access_key
            self.storage_info_from_set['mySecretKey'] = secret_key
            self.storage_info_from_set['endpoint'] = 's3.' + region + '.amazonaws.com'
            self.storage_info_from_set['region'] = region
            self.storage_info_from_set['bucketType'] = 's3'
            self.storage_info_from_set['bucketName'] = bucket_name
            self.storage_info_from_set['filePath'] = file_path
            self.storage_info_from_set['fileName'] = file_path.split('/')[-1]
            self.storage_info_from_set['target'] = target

        ### Local
        else:
            storage_type = 'local'
            self.storage_info_from_set['filePath'] = file_path
            self.storage_info_from_set['fileName'] = file_path.split('/')[-1]
            self.storage_info_from_set['target'] = target

            self.save_path = file_path
            self.StorageInfo = self.storage_info_from_set
            self.target_name = target

        if save_json:
            if save_path is None:
                timestamp = str(datetime.datetime.now().date()).replace('-', '')
                dir_list = os.listdir(save_prefix)
                num = len([True for i in dir_list if timestamp in i])
                save_path = timestamp + '-' + str(num + 1).zfill(2) + '-' + storage_type + '-connection-info' + '.json'

            else:  # save_path is not None
                pass

            storage_info_full_path = os.path.join(save_prefix, save_path)
            with open(storage_info_full_path, 'w', encoding='utf-8') as save_file:
                json.dump(self.storage_info_from_set, save_file, indent='\t')

        if not save_json and save_path is not None:
            raise ValueError("'save_json=True'로 설정하시기 바랍니다.")

    def get_file(self, storage_json_file_name=None):
        if storage_json_file_name is not None:

            # meta file 저장하는 폴더 만들면, 이 경로는 수정돼야 함.
            storage_info_json_path = os.path.join(ENV_JUPYTER_HOME_DIR, storage_json_file_name)

            with open(storage_info_json_path) as jsonFile:
                self.StorageInfo = json.load(jsonFile)

        else:  # storage_json_file_name == None, when using set_storage() method.
            self.StorageInfo = self.storage_info_from_set

        ## define the target name
        self.target_name = self.StorageInfo['target']

        ### HDFS
        if 'host' in self.StorageInfo.keys():

            ## path for saving data
            save_dir = os.path.join(ENV_JUPYTER_HOME_DIR, 'data_from_hdfs')
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            else:
                pass

            split_list = list(filter(None, self.StorageInfo['filePath'].split('/')))

            HOST = self.StorageInfo['host']
            PORT = int(self.StorageInfo['port'])
            FILE_PATH = self.StorageInfo['filePath']
            FILE_DIR = '/'
            for i in split_list[:len(split_list) - 1]:
                FILE_DIR = os.path.join(FILE_DIR, i)
            FILE_NAME = split_list[-1]

            save_file_name = FILE_NAME.split('.')[0] + '_' + str(datetime.datetime.now().date()).replace('-', '') + '.'\
                             + FILE_NAME.split('.')[1]
            self.save_path = os.path.join(save_dir, save_file_name)
            self.endpoint = os.path.join('hdfs://', HOST, self.StorageInfo['port']) + FILE_PATH

            hdfs = HDFileSystem(host=HOST, port=PORT)
            hdfs.ls(FILE_DIR)

            sys.stdout.write('%s %s %s' % ('Downloading file...', FILE_NAME, '\n'))
            time.sleep(1)
            hdfs.get(FILE_PATH, self.save_path)
            logging.info(self.save_path)

        ### AWS-S3
        elif 'bucketName' in self.StorageInfo.keys():
            BUCKET_TYPE = self.StorageInfo['bucketType']
            BUCKET_NAME = self.StorageInfo['bucketName']
            FILE_PATH = self.StorageInfo['filePath']
            FILE_NAME = self.StorageInfo['fileName']
            # FILE_TYPE = self.StorageInfo['fileType']
            # FILE_DELIM = self.StorageInfo['fileDelim']
            ACCESS_KEY = self.StorageInfo['myAccessKey']
            SECRET_KEY = self.StorageInfo['mySecretKey']
            REGION = self.StorageInfo['region']
            URL = self.StorageInfo['endpoint']

            ## path for saving data
            save_dir = os.path.join(ENV_JUPYTER_HOME_DIR, 'data_from_aws')
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            else:
                pass

            save_file_name = FILE_NAME.split('.')[0] + '_' + str(datetime.datetime.now().date()).replace('-', '')\
                                  + '.' + FILE_NAME.split('.')[1]
            self.save_path = os.path.join(save_dir, save_file_name)

            # endpoint
            pre_url = 'https://' + BUCKET_NAME + '.' + URL
            self.endpoint = os.path.join(pre_url, FILE_PATH)

            client = boto3.client(BUCKET_TYPE,
                                  aws_access_key_id=ACCESS_KEY,
                                  aws_secret_access_key=SECRET_KEY,
                                  region_name=REGION)

            transfer = boto3.s3.transfer.S3Transfer(client)

            progress = ProgressPercentage(client, BUCKET_NAME, FILE_PATH)

            sys.stdout.write('%s %s %s' % ('Downloading file...', FILE_NAME, '\n'))
            transfer.download_file(BUCKET_NAME, FILE_PATH, self.save_path, callback=progress)
            logging.info(self.save_path)

        ### Local
        else:
            self.save_path = self.StorageInfo['filePath']

        return self.save_path, self.StorageInfo, self.target_name

    def set_data(self, data=None):
        if data is not None:
            self.data = data

    @staticmethod
    def _send_message(metric=None, current_value=None, message=None, thresholds=None, alarm_object=None, alarm_api=None):
        if alarm_object:
            messages = list()

            if thresholds:
                if current_value >= thresholds:
                    messages.append('[모델 학습 완료] ' + metric + '이 설정하신 thresolds: ' + str(thresholds) + '를 초과하였습니다.')

            if message:
                if isinstance(message, str):
                    messages.append(message)
                elif isinstance(message, list):
                    messages.extend(message)
                else:
                    raise ValueError("Wrong message input detected. Available type is 'str' and 'list'")

            if messages:
                for message in messages:
                    alarm_object.message = message
                    alarm_object.type = "Workspace"
                    alarm_api.call_rest_api(alarm_object.get_alarm_param(), "alarm")

    def set_slack(self, hook_url=None):
        if hook_url:
            self.workspace_alarm.notifiers['slack'] = hook_url

    def unset_slack(self):
        if 'slack' in self.workspace_alarm.notifiers.keys():
            del self.workspace_alarm.notifiers['slack']

    def set_mail(self, address=None):
        if address:
            self.workspace_alarm.notifiers['mail'] = address

    def unset_mail(self):
        if 'mail' in self.workspace_alarm.notifiers.keys():
            del self.workspace_alarm.notifiers['mail']

    def send_message(self, message=None, thresholds=None):
        if message and thresholds:
            raise ValueError("'message'와 'thresholds' 두 개의 arguments를 동시에 입력할 수 없습니다.")
        else:
            self.message = message
            self.thresholds = thresholds

    def unset_message(self):
        self.message = None
        self.thresholds = None

    def set_user_id(self, user_id):
        self.user_id = user_id

    def unset_user_id(self):
        self.user_id = None

    def set_features(self, feature_names):
        if str(type(feature_names)) == "<class 'list'>":
            self.feature_name = feature_names
        else:
            try:
                self.feature_name = feature_names.tolist()
            except:
                pass

            try:
                self.feature_name = list(feature_names)
            except AttributeError:
                raise ValueError('입력값으로 list 또는 pandas.core.indexes.base.Index를 사용하시기 바랍니다.')

        return feature_names

    def set_current_notebook(self):
        self.notebook_info = get_current_notebook()

    def get_current_notebook(self):
        return self.notebook_info
