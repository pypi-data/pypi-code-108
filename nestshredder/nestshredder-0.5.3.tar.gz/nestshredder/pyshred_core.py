from distutils.errors import CompileError
import pandas as pd 
from datetime import datetime 
import os 
import numpy as np
import logging
import csv

def pad_dict_list(dict_list, padel):
    lmax = 0
    for d in dict_list:
        for lname in d.keys():
            lmax = max(lmax, len(d[lname]))
        for lname in d.keys():
            ll = len(d[lname])
            if  ll < lmax:
                d[lname] += [padel] * (lmax - ll)
    return dict_list

def _shred_recursive(source_df,target_path,source_file,source_name,parent_name,batch_ref=None,output_method=None):

    try:

        nested_cols = []
        dict_cols = []

        if source_name != source_file:
            explode_df = source_df.explode(source_name)
            new_df = explode_df[source_name].apply(pd.Series,convert_dtype=False,dtype=object)
            source_df = new_df
            if len(source_df.columns) ==1: ##if the source is generated from an array then correct for the 'zero' column. Parquet doesn't like it.
                if 0 in source_df.columns:
                    new_col_header = []
                    new_col_header.append(source_name)
                    source_df.columns = new_col_header
            else:
                if 0 in source_df.columns: ### random zeros - this may be the artefact of something more serious but... we'll see I guess!
                    source_df.drop(inplace=True,columns=[0])

        if parent_name == source_file:
            parent_name = parent_name[parent_name.find("_")+1:]
            source_name = source_name[source_name.find("_")+1:] 

        if parent_name != source_name:
            source_df = source_df.rename_axis('$_'+parent_name+'_id__').reset_index()
            source_df.index.name = '$_'+source_name + '_id__'
        else:
            source_df.index.name = '$_'+source_name + '_id__'
        
        for c in source_df:
            if any(isinstance(obj, (np.ndarray,list)) for obj in source_df[c]): ###ignore me
                nested_cols.append({'col':c,'type':'np.ndarray'})
            elif any(isinstance(obj, (dict)) for obj in source_df[c]):
                dict_cols.append(c)

        for dc in dict_cols:
            part_df = None
            part_df = source_df[dc].apply(pd.Series,convert_dtype=False,dtype=object)
            list_old_cols = []
            list_old_cols = part_df.columns.tolist()
            list_new_cols = []
            
            for l in list_old_cols:
                list_new_cols.append(str(dc)+'-'+str(l))
            
            part_df.columns = list_new_cols

            for nc in part_df:
                if any(isinstance(obj, (np.ndarray,list)) for obj in part_df[nc]): ###ignore me
                    if {'col':nc,'type':'np.ndarray'} not in nested_cols:
                        nested_cols.append({'col':nc,'type':'np.ndarray'})
                elif any(isinstance(obj, (dict)) for obj in part_df[nc]):
                    if nc not in dict_cols:
                        dict_cols.append(nc)

            for pc in list_new_cols:
                source_df[pc] = part_df[pc]

            source_df.drop(columns=dc,axis=1, inplace=True)

        for nc in nested_cols:
            deliver_df = None
            deliver_df = pd.DataFrame(source_df[nc['col']])
            _shred_recursive(source_df=deliver_df,target_path=target_path,source_file=source_file,source_name=nc['col'],parent_name=parent_name+'~'+source_name,batch_ref=batch_ref,output_method=output_method) ###
            source_df.drop(columns=nc['col'],axis=1,inplace=True)

        if source_name == source_file:
            source_df.index.name = f'$_{parent_name}_id__'

        nodename = parent_name+'~'+source_name

        if batch_ref is None:
            if os.path.exists(f"{target_path}/{nodename}/") == False:
                os.mkdir(f"{target_path}/{nodename}")
        else:
            if os.path.exists(f"{target_path}/{batch_ref}/") == False:
                os.mkdir(f"{target_path}/{batch_ref}")
            if os.path.exists(f"{target_path}/{batch_ref}/{nodename}/") == False:
                os.mkdir(f"{target_path}/{batch_ref}/{nodename}")

        for col in source_df.columns:
                weird = (source_df[[col]].applymap(type) != source_df[[col]].iloc[0].apply(type)).any(axis=1)
                if len(source_df[weird]) > 0:
                    source_df[col] = source_df[col].astype(str)
                if source_df[col].dtype == list:
                    source_df[col] = source_df[col].astype(str)

        if batch_ref is None:
            output_df(output_method,source_df,target_path,batch_ref,nodename,source_file,compression=None)
        else:
            source_df.insert(0,'$batchref',batch_ref)
            output_df(output_method,source_df,target_path,batch_ref,nodename,source_file,compression=None)

        return str(0)

    except Exception as e:
        logging.error('Error at recursive shredding core.')
        return e

def output_df(method,source_df,target_path,batch_ref,nodename,source_file,compression=None):

    try:

        if method == 'parquet' or method is None:
            if compression is None:
                source_df.to_parquet(f"{target_path}/{batch_ref}/{nodename}/{source_file}~{nodename}.parquet",index=True)
            elif compression in ['snappy', 'gzip', 'brotli']:
                source_df.to_parquet(f"{target_path}/{batch_ref}/{nodename}/{source_file}~{nodename}.parquet",index=True,compression=compression)
            else:
                logging.error(f"Invalid output compression '{compression}' defined.")
        
        if method == 'json':
            if compression is not None:
                logging.warn(f"Output compression {compression} not supported for JSON at this time.")
            source_df.to_json(path_or_buf=f"{target_path}/{batch_ref}/{nodename}/{source_file}~{nodename}.json",index=True,orient='records')

        if method == 'csv':
            if compression is not None:
                logging.warn(f"Output compression {compression} not supported for CSV at this time.")
            source_df.to_csv(path_or_buf=f"{target_path}/{batch_ref}/{nodename}/{source_file}~{nodename}.csv",index=True,sep='|',header=True,quoting=csv.QUOTE_NONNUMERIC)
    except Exception as e:
        logging.error('Error at shred output.')
        return e