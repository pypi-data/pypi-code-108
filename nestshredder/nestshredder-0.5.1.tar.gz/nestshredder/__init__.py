import pandas as pd
import os
import json
import sys
from nestshredder.pyshred_core import _shred_recursive

def shred_json(source_file_path,target_folder_path,object_name):

    if os.path.exists(target_folder_path) == False:
        is_success = 'Target Path Does Not Exist'
        print("1:Error - " + is_success )
        return "1:Error - " + is_success   

    if os.path.exists(source_file_path) == False:
        is_success = 'Source Path Does Not Exist'
        print("1:Error - " + is_success )
        return "1:Error - " + is_success   

    if object_name.find(" ")>0:
        is_success = f"One word object names please. You provided:{object_name}. Acceptable:{object_name.replace(' ','')}"
        print("1:Error - " + is_success)
        return "1:Error - " + is_success

    try:
        json_df = pd.read_json(source_file_path)
        is_success = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name)
    except Exception as e:        
        if str(e) == 'If using all scalar values, you must pass an index':
            new_list = []
            with open(source_file_path) as json_file:
                data = json.load(json_file)
                new_list.append(data)
                json_df = pd.DataFrame.from_dict(new_list)
                is_success = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name)
        else:
            is_success = str(e)

    if is_success != "0":
        print("1:Error - " + is_success )
        return "1:Error - " + is_success        
    else: 
        return "0:OK"

def shred_parquet(source_file_path,target_folder_path,object_name):

    if os.path.exists(target_folder_path) == False:
        is_success = 'Target Path Does Not Exist'
        print("1:Error - " + is_success )
        return "1:Error - " + is_success   

    if os.path.exists(source_file_path) == False:
        is_success = 'Source Path Does Not Exist'
        print("1:Error - " + is_success )
        return "1:Error - " + is_success   

    if object_name.find(" ")>0:
        is_success = f"One word object names please. You provided:{object_name}. Acceptable:{object_name.replace(' ','')}"
        print("1:Error - " + is_success)
        return "1:Error - " + is_success

    try:
        json_df = pd.read_parquet(source_file_path)
        is_success = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name)
    except Exception as e:        
        is_success = str(e)

    if is_success != "0":
        print("1:Error - " + is_success )
        return "1:Error - " + is_success        
    else: 
        return "0:OK"
