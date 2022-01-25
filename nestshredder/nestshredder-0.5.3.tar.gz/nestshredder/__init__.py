from numpy import dtype
import pandas as pd
import logging
import json
from nestshredder.pyshred_core import _shred_recursive, pad_dict_list
from nestshredder.pyshred_util import check_arguments

def shred_json(path_or_buf,target_folder_path,object_name,batch_ref=None,orient=None,dtype=None,convert_axes=None,convert_dates=True,keep_default_dates=True,precise_float=False,date_unit=None,encoding=None,encoding_errors='strict',lines=False,chunksize=None,compression='infer',nrows=None,storage_options=None,output_method=None):

    check_arguments(target_folder_path=target_folder_path,object_name=object_name,batch_ref=batch_ref)

    try:
        json_df = pd.read_json(path_or_buf,orient=orient,dtype=dtype,convert_axes=convert_axes,convert_dates=convert_dates,keep_default_dates=keep_default_dates,precise_float=precise_float,date_unit=date_unit,encoding=encoding,encoding_errors=encoding_errors,lines=lines,chunksize=chunksize,compression=compression,nrows=nrows,storage_options=storage_options)
        shred_outcome = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name,batch_ref)
    except Exception as e:        
        if str(e) == 'If using all scalar values, you must pass an index':
            new_list = []
            try:
                with open(path_or_buf) as json_file:
                    data = json.load(json_file)
                    new_list.append(data)
                    json_df = pd.DataFrame.from_dict(new_list)
                    shred_outcome = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name,batch_ref,output_method)
            except Exception as e:
                if str(e)[0:12] == 'expected str':
                    path_or_buf.seek(0)
                    data = json.loads(path_or_buf.read())
                    new_list.append(data)
                    json_df = pd.DataFrame.from_dict(new_list)
                    shred_outcome = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name,batch_ref,output_method)
                else:
                    shred_outcome = str(e)
                    logging.error(shred_outcome)
                    return
        elif str(e) == 'All arrays must be of the same length':  
            new_list = []
            try:
                with open(path_or_buf) as json_file:
                    data = json.load(json_file)
                    new_list.append(data)
                    padded_list = pad_dict_list(new_list,'n/a')
                    json_df = pd.DataFrame.from_dict(padded_list)
                    shred_outcome = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name,batch_ref,output_method)
            except Exception as e:
                # logging.info(str(e)[0:12])
                if str(e)[0:12] == 'expected str':
                    path_or_buf.seek(0)
                    data = json.loads(path_or_buf.read())
                    new_list.append(data)
                    json_df = pd.DataFrame.from_dict(new_list)
                    shred_outcome = _shred_recursive(json_df,target_folder_path,object_name,object_name,object_name,batch_ref,output_method)
                else:
                    shred_outcome = str(e)
                    logging.error(shred_outcome)
                    return
        else:
            shred_outcome = str(e)
    if shred_outcome != "0":
        logging.error(shred_outcome)
        return        
    else: 
        logging.info(f"Completed processing for object name: {object_name}")
        return

def shred_parquet(path_or_buf,target_folder_path,object_name,batch_ref=None,columns=None,output_method=None):

    check_arguments(target_folder_path,object_name,batch_ref)

    try:
        parquet_df = pd.read_parquet(path_or_buf,columns=columns)
        shred_outcome = _shred_recursive(parquet_df,target_folder_path,object_name,object_name,object_name,batch_ref,output_method)
    except Exception as e:        
        logging.error(str(e))
        return

    if shred_outcome != "0":
        logging.error(shred_outcome)
        return        
    else: 
        logging.info(f"Completed processing for object name: {object_name}.")
        return
