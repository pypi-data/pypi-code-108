import os
import re
import glob
import json
import numpy as np
import pandas as pd
import more_itertools as mit
from operator import itemgetter
from Accuinsight.modeler.core.sklearnModelType import ONEVS
from Accuinsight.modeler.core import lossFuncInfo


def model_type(model_name):
    if 'tensorflow' in str(model_name):
        return 'tf.keras'
    elif 'keras' in str(model_name):
        return 'keras'
    elif 'state_dict' in dir(model_name):
        return 'pytorch'

    tmp_name = str(model_name)
    if '(' in tmp_name:
        tmp_name = str(model_name)[:str(model_name).find('(')]
    elif '<' in tmp_name:
        tmp_name = str(model_name).split('.')[0][1:]

    if any(i in tmp_name for i in ONEVS):
        idx1 = list(mit.locate(str(model_name), lambda x: x == "="))[0]
        idx2 = list(mit.locate(str(model_name), lambda x: x == "("))[1]
        return str(model_name)[idx1 + 1:idx2]
        
    return tmp_name
        
        
def trial_number_all(DB_path, file_type):
    os.chdir(DB_path)
    str_file_type = '*.' + file_type
    file_list = glob.glob(str_file_type)
    regex = re.compile('\d+')
    
    trialNumList = []
    
    for i in range(len(file_list)):
        try:
            num = np.int(file_list[i][regex.search(file_list[i]).start():regex.search(file_list[i]).end()])
            trialNumList.append(num)
        except:
            pass
    
    try:
        trial_num = max(trialNumList) + 1
    except:
        trial_num = 1
    
    os.chdir(r'..')                  ######## 상위 디렉토리로 이동 (경우에 따라서 변경 필요!!!!!) ########
    return str(trial_num)


def trial_num_json(DB_path, file_type):
    os.chdir(DB_path)
    str_file_type = '*.' + file_type
    file_list = glob.glob(str_file_type)
    regex = re.compile('\d+')
    
    trialNumList = []
    
    for i in range(len(file_list)):
        try:
            num = np.int(file_list[i][regex.search(file_list[i]).start():regex.search(file_list[i]).end()])
            trialNumList.append(num)
        except:
            pass
    
    try:
        trial_num = max(trialNumList)
    except:
        trial_num = 1
    
    os.chdir(r'..')                  ######## 상위 디렉토리로 이동 (경우에 따라서 변경 필요!!!!!) ########
    return str(trial_num)


# model parameter
class from_model(object):
    def __init__(self, model_name):
        try:
            self.parDict = model_name.get_params()
            self.keyList = list(model_name.get_params().keys())
        except:                                                   # lightGBM
            self.parDict = model_name.params
            self.keyList = list(model_name.params.keys())
            
    def all_params(self):
        # multiclass
        try:
            parkey = [i for i in self.parDict.keys() if '__' in i]
        
            parvalue = itemgetter(*parkey)(self.parDict)
            parvalue = list(parvalue)
        
            parkey = list(map(lambda x: x[x.find('__') + 2:], parkey))
            
            all_dict = dict()
            for i in range(len(parkey)):
                all_dict[parkey[i]] = parvalue[i]
            
            if 'random_state' in all_dict.keys():
                all_dict.pop('random_state')
            
            return all_dict
        
        # binary
        except TypeError:
            return self.parDict
    
    def param_keys(self):
        parkey = [i for i in self.parDict.keys() if '__' in i]
        parkey = list(map(lambda x: x[x.find('__') + 2:], parkey))
        if len(parkey) != 0:
            try:
                parkey.remove('random_state')
            except ValueError:
                pass

            return parkey
        else:
            return list(self.parDict.keys())


def is_classification(model_name):
    if hasattr(model_name.loss, 'get_config'):      # tensorflow
        if model_name.loss.get_config()['name'] in lossFuncInfo.CLASSIFICATION:
            return True
    
        elif model_name.loss.get_config()['name'] in lossFuncInfo.REGRESSION:
            return False
    
        else:
            raise ValueError('현재 설정한 loss는 지원되지 않습니다. 관리자에게 문의하십시오.')
        
    else:                                          # keras
        if model_name.loss in lossFuncInfo.CLASSIFICATION:
            return True

        elif model_name.loss in lossFuncInfo.REGRESSION:
            return False

        else:
            raise ValueError('현재 설정한 loss는 지원되지 않습니다. 관리자에게 문의하십시오.')


def feature_name(savedPath, StorageInfo, targetName, data=None):
    if data is not None:
        try:
            feature_name = list(data.keys())
        except AttributeError:
            raise TypeError('지원하지 않는 데이터 형식입니다. 현재 지원하는 데이터 형식은 json과 pandas.core.frame.DataFrame입니다.')

    else:
        if StorageInfo is None:
            fileType = savedPath.split('.')[-1]

        elif 'host' in StorageInfo:  # HDFS
            fileType = StorageInfo['filePath'].split('.')[1]

        else:  # AWS S3
            fileType = StorageInfo['fileName'].split('.')[1]
        
        if fileType == 'json':
            with open(savedPath) as jsonFile:
                json_data = json.load(jsonFile)
            feature_name = list(json_data.keys())
        elif fileType == 'csv':
            feature_name = list(pd.read_csv(savedPath).columns)
            if 'Unnamed: 0' in feature_name and feature_name[0] == 'Unnamed: 0':
                feature_name.remove('Unnamed: 0')
        else:
            raise TypeError('{type}은 지원하지 않는 데이터 형식입니다. 현재 지원하는 데이터 형식은 json과 csv입니다.'.format(type=fileType))
    
    if targetName in feature_name:
        feature_name.remove(targetName)

    return feature_name
