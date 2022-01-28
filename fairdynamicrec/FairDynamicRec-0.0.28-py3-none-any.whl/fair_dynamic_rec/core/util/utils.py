import re
from datetime import datetime
import glob
import os

def create_log_name(filename: str):
    _time = str(datetime.now())
    _time_obj = datetime.strptime(_time, '%Y-%m-%d %H:%M:%S.%f')
    _timestamp = _time_obj.strftime("%Y%m%d_%H%M%S")
    return filename.format(_timestamp)

def purge_old_logs(path: str):
    for file in glob.glob(path):
        if re.match(r'.*/FairDynamicRec_log.*', file):
            os.remove(file)

def get_param_config_name(parameters):
    param_name = parameters['name']['attr']['abb'] if parameters['name']['attr']['abb'] else parameters['name']['value']
    for key, value in parameters.items():
        if key != 'name':
            param_name += "-" + str(parameters[key]['attr']['abb'] if parameters[key]['attr']['abb'] else parameters[key]['value']) + str(parameters[key]['value'])
    return param_name
def get_legend_labels(rankers):
    labels = {}
    for ranker in rankers:
        param_name = get_param_config_name(ranker['config'])
        labels[param_name] = param_name
        if 'attr' in ranker['config']['name']:
            if 'viz-legend' in ranker['config']['name']['attr']:
                if ranker['config']['name']['attr']['viz-legend'].lower() == 'false':
                    labels[param_name] = ranker['config']['name']['attr']['abb']
    return labels

def get_dict_key_from_value(var_dict, value):
    return list(var_dict.keys())[list(var_dict.values()).index(value)]
def get_dict_keys_from_list(var_dict, value_list):
    result = []
    for value in value_list:
        result.append(get_dict_key_from_value(var_dict, value))
    return result
