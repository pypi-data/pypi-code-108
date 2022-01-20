import pandas as pd 
from datetime import datetime 
import os 
import io
import numpy as np

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

def _shred_recursive(source_df,target_path,source_file,source_name,parent_name):

    try:

        nested_cols = []
        dict_cols = []

        if source_name != source_file:
            explode_df = source_df.explode(source_name)
            new_df = explode_df[source_name].apply(pd.Series)
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
            part_df = source_df[dc].apply(pd.Series)
            
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
            _shred_recursive(source_df=deliver_df,target_path=target_path,source_file=source_file,source_name=nc['col'],parent_name=parent_name+'~'+source_name) ###
            source_df.drop(columns=nc['col'],axis=1,inplace=True)

        if source_name == source_file:
            source_df.index.name = f'$_{parent_name}_id__'

        nodename = parent_name+'~'+source_name

        if os.path.exists(f"{target_path}/{nodename}/") == False:
            os.mkdir(f"{target_path}/{nodename}")

        for col in source_df.columns:
                weird = (source_df[[col]].applymap(type) != source_df[[col]].iloc[0].apply(type)).any(axis=1)
                if len(source_df[weird]) > 0:
                    source_df[col] = source_df[col].astype(str)
                if source_df[col].dtype == list:
                    source_df[col] = source_df[col].astype(str)

        source_df.to_parquet(f"{target_path}/{nodename}/{source_file}~{nodename}.parquet",index=True)

        return str(0)

    except Exception as e:

        return e

