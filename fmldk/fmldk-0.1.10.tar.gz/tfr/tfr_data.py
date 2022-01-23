#!/usr/bin/env python
# coding: utf-8

import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions
import pandas as pd
import numpy as np
from joblib import Parallel, delayed
import itertools
import random
from datetime import datetime, timedelta
import os
from pathlib import Path
import csv
import re
import gc
import math as m
import time

class tfr_dataset:
    def __init__(self, col_dict, window_len, fh, batch, min_nz, PARALLEL_DATA_JOBS, PARALLEL_DATA_JOBS_BATCHSIZE):
        """
        col_dict: dictionary of various column groups {id_col:'',
                                                       target_col:'',
                                                       time_index_col:'',
                                                       static_num_col_list:[],
                                                       static_cat_col_list:[],
                                                       temporal_known_num_col_list:[],
                                                       temporal_unknown_num_col_list:[],
                                                       temporal_known_cat_col_list:[],
                                                       temporal_unknown_cat_col_list:[],
                                                       strata_col_list:[],
                                                       sort_col_list:[],
                                                       wt_col:''}
        window_len: history_len + forecast_horizon
        fh: forecast_horizon
        batch: batch_size (per strata)
        min_nz: min. no. of non-zeros in the target input series to be eligible for train/test batch
        
        """
        self.col_dict = col_dict
        self.window_len = window_len
        self.fh = fh
        self.batch = batch
        self.min_nz = min_nz
        self.PARALLEL_DATA_JOBS = PARALLEL_DATA_JOBS
        self.PARALLEL_DATA_JOBS_BATCHSIZE = PARALLEL_DATA_JOBS_BATCHSIZE
        
        # extract columnsets from col_dict
        self.id_col = self.col_dict.get('id_col', None)
        self.target_col = self.col_dict.get('target_col', None)
        self.time_index_col = self.col_dict.get('time_index_col', None)
        self.strata_col_list = self.col_dict.get('strata_col_list', [])
        self.sort_col_list = self.col_dict.get('sort_col_list', [])
        self.wt_col = self.col_dict.get('wt_col', None)
        self.static_num_col_list = self.col_dict.get('static_num_col_list', [])
        self.static_cat_col_list = self.col_dict.get('static_cat_col_list', [])
        self.temporal_known_num_col_list = self.col_dict.get('temporal_known_num_col_list', [])
        self.temporal_unknown_num_col_list = self.col_dict.get('temporal_unknown_num_col_list', [])
        self.temporal_known_cat_col_list = self.col_dict.get('temporal_known_cat_col_list', [])
        self.temporal_unknown_cat_col_list = self.col_dict.get('temporal_unknown_cat_col_list', [])

        if (self.id_col is None) or (self.target_col is None) or (self.time_index_col is None):
            raise ValueError("Id Column, Target Column or Index Column not specified!")

        # full columnset for train/test/infer
        self.col_list = [self.id_col] + [self.target_col] +                         self.static_num_col_list + self.static_cat_col_list +                         self.temporal_known_num_col_list + self.temporal_unknown_num_col_list +                         self.temporal_known_cat_col_list + self.temporal_unknown_cat_col_list

        self.cat_col_list = self.static_cat_col_list + self.temporal_known_cat_col_list + self.temporal_unknown_cat_col_list

        # get columnset indices
        self.id_index =  self.col_list.index(self.id_col)
        self.target_index = self.col_list.index(self.target_col)
        self.static_num_indices = [i for i in range(len(self.col_list)) if self.col_list[i] in self.static_num_col_list]
        self.static_cat_indices = [i for i in range(len(self.col_list)) if self.col_list[i] in self.static_cat_col_list]
        self.temporal_known_num_indices = [i for i in range(len(self.col_list)) if self.col_list[i] in self.temporal_known_num_col_list]
        self.temporal_unknown_num_indices = [i for i in range(len(self.col_list)) if self.col_list[i] in self.temporal_unknown_num_col_list]
        self.temporal_known_cat_indices = [i for i in range(len(self.col_list)) if self.col_list[i] in self.temporal_known_cat_col_list]
        self.temporal_unknown_cat_indices = [i for i in range(len(self.col_list)) if self.col_list[i] in self.temporal_unknown_cat_col_list]
        
        # column indices dict
        self.col_index_dict = {'id_index': [self.id_col, self.id_index],
                               'target_index': [self.target_col, self.target_index],
                               'static_num_indices': [self.static_num_col_list, self.static_num_indices],
                               'static_cat_indices': [self.static_cat_col_list, self.static_cat_indices],
                               'temporal_known_num_indices': [self.temporal_known_num_col_list, self.temporal_known_num_indices],
                               'temporal_unknown_num_indices': [self.temporal_unknown_num_col_list, self.temporal_unknown_num_indices],
                               'temporal_known_cat_indices': [self.temporal_known_cat_col_list, self.temporal_known_cat_indices],
                               'temporal_unknown_cat_indices': [self.temporal_unknown_cat_col_list, self.temporal_unknown_cat_indices]} 
        
        
    def get_keys(self, data):
        """
        if strata_col specified:
            Returns a dictionary with strata_col values as Keys & corresponding id_col array as Values
        else:
            Returns a dictionary with only one item, a 'null' Key & an array of id_col values
        """
        def wt_fn(x):
            return x.groupby([self.id_col], sort=True)[self.wt_col].first().values
    
        if len(self.strata_col_list)>0:
            keys_dict = data.groupby(self.strata_col_list, sort=True)[self.id_col].unique().to_dict()
            if self.wt_col:
                wts_dict = data.groupby(self.strata_col_list, sort=True).apply(lambda x: wt_fn(x)).to_dict()
            else:
                wts_dict = data.groupby(self.strata_col_list, sort=True)[self.id_col].apply(lambda x: np.ones(x.nunique()) ).to_dict()
        else:
            keys_dict = {'ID': sorted(data[self.id_col].unique())}
            if self.wt_col:
                wts_dict = {'ID': data.groupby([self.id_col], sort=True)[self.wt_col].mean().values}
            else:
                wts_dict = {'ID': np.ones(data[self.id_col].nunique())}
                
        return keys_dict, wts_dict

    def dict_sampler(self, v, w):
        """
        random sample of size 'batch' from an array returned as list
        """
        w = w/np.sum(w) # ensure sum of probabilities==1

        if self.batch > len(v):
            replace = True # if not enough items (less than batch size, sample with replace) 
        else:
            replace = False
            
        return list(np.random.choice(v, size=self.batch, replace=replace, p=w))

    def select_ids(self, keys_dict, wts_dict):
        """
        Sample Ids for a train/test iteration from the Keys_dict
        """
        n_jobs = min(len(keys_dict),4)
        sample_id = Parallel(n_jobs=n_jobs, batch_size=self.PARALLEL_DATA_JOBS_BATCHSIZE)(delayed(self.dict_sampler)(v1,v2) for (k1,v1),(k2,v2) in zip(keys_dict.items(), wts_dict.items()) )
        sample_id = list(itertools.chain.from_iterable(sample_id))
        random.shuffle(sample_id)
        return sample_id

    def select_arrs(self, df):
        """
        Extract train/test samples from each sampled Id as 2-D arrays [window_len, num_columns]
        """
        groups = df.groupby([self.id_col])
        sampled_arr = Parallel(n_jobs=self.PARALLEL_DATA_JOBS, batch_size=self.PARALLEL_DATA_JOBS_BATCHSIZE)(delayed(self.df_sampler)(gdf) for _,gdf in groups)
        arr_list = [tup[0] for tup in sampled_arr]
        pad_list = [tup[1] for tup in sampled_arr]
        arr = np.stack(arr_list, axis=0)
        pad_arr = np.stack(pad_list, axis=0)
        return arr, pad_arr

    def df_sampler(self, gdf):
        """
        Helper function for select_arrs
        
        gdf = gdf.reset_index(drop=True)
        first_nonzero_index = gdf[self.target_col].ne(0).idxmax()
        gdf = gdf.iloc[first_nonzero_index:,:]
        gdf = gdf.reset_index(drop=True)
        
        """
        gdf = gdf.reset_index(drop=True)
        delta = len(gdf) - self.window_len
        if delta<0:
            arr = gdf.loc[:,self.col_list].reset_index(drop=True).values
            # left pad to window_len with 0
            pad_len = np.abs(delta)
            arr = np.pad(arr,pad_width=((pad_len,0),(0,0)), mode='constant', constant_values=0)
        elif delta==0:
            pad_len = 0
            rand_start = 0
            arr = gdf.loc[rand_start:rand_start + self.window_len - 1, self.col_list].reset_index(drop=True).values
        else:
            pad_len = 0
            rand_start = random.randrange(delta)
            arr = gdf.loc[rand_start:rand_start + self.window_len - 1, self.col_list].reset_index(drop=True).values
        return (arr, pad_len)
    
    def df_infer_sampler(self, gdf):
        """
        Helper function for select_all_arrs
        """
        gdf = gdf.reset_index(drop=True)
        delta = len(gdf) - self.window_len
        if delta<0:
            arr = gdf.loc[:,self.col_list].reset_index(drop=True).values
            pad_len = np.abs(delta)
            arr = np.pad(arr,pad_width=((pad_len,0),(0,0)), mode='constant', constant_values=0)
            date_arr = gdf.loc[:,self.time_index_col].reset_index(drop=True).values
            date_arr = np.pad(date_arr,pad_width=((pad_len,0)), mode='constant', constant_values=0)
            date_arr = date_arr[-self.fh:]
        elif delta==0:
            pad_len = 0
            rand_start = 0
            arr = gdf.loc[rand_start:rand_start + self.window_len - 1, self.col_list].reset_index(drop=True).values
            date_arr = gdf.loc[rand_start:rand_start + self.window_len - 1, self.time_index_col].reset_index(drop=True).tail(self.fh).values
        else:
            pad_len = 0
            rand_start = random.randrange(delta)
            arr = gdf.loc[rand_start:rand_start + self.window_len - 1, self.col_list].reset_index(drop=True).values
            date_arr = gdf.loc[rand_start:rand_start + self.window_len - 1, self.time_index_col].reset_index(drop=True).tail(self.fh).values
        return (arr, pad_len, date_arr)
    
    def select_all_arrs(self, data):
        """
        Use for inference dataset
        """
        groups = data.groupby([self.id_col])
        sampled_arr = Parallel(n_jobs=self.PARALLEL_DATA_JOBS, batch_size=self.PARALLEL_DATA_JOBS_BATCHSIZE)(delayed(self.df_infer_sampler)(gdf) for _,gdf in groups)
        arr_list = [tup[0] for tup in sampled_arr]
        pad_list = [tup[1] for tup in sampled_arr]
        date_list = [tup[2] for tup in sampled_arr]
        arr = np.stack(arr_list, axis=0)
        pad_arr = np.stack(pad_list, axis=0)
        date_arr = np.stack(date_list, axis=0)
        id_arr = arr[:,-1:,0]
        
        """
        arr_list = []
        pad_list = []
        date_list = []
        for gname, gdf in data.groupby([self.id_col]):
            arr, pad_len = self.df_sampler(gdf)
            date_arr = gdf[self.time_index_col].tail(self.fh).values
            arr_list.append(arr)
            pad_list.append(pad_len)
            date_list.append(date_arr)
        arr = np.stack(arr_list, axis=0)
        pad_arr = np.stack(pad_list, axis=0)
        date_arr = np.stack(date_list, axis=0)
        id_arr = arr[:,-1:,0]
        """
        return arr, pad_arr, id_arr, date_arr
    
    def sort_dataset(self, data):
        """
        sort pandas dataframe by provided col list & order
        """
        if len(self.sort_col_list) > 0:
            data = data.sort_values(by=self.sort_col_list, ascending=True)
        else:
            pass
        return data
    
    def check_null(self, data):
        """
        Check for columns containing NaN
        """
        null_cols = []
        null_status = None
        for col in self.col_list:
            if data[col].isnull().any():
                null_cols.append(col)
        
        if len(null_cols)>0:
            null_status == True
        else:
            null_status == False
        
        return null_status, null_cols
    
    def data_generator(self, data):
        """
        outputs:
        --------
        arr: [batch,window_len,len(col_list)]
        pad_arr as list: [pad_len_arr1, pad_len_arr2, ...]

        """
        keys_dict, wts_dict = self.get_keys(data)
        while True:
            sample_id = self.select_ids(keys_dict, wts_dict)
            df = data.query("{}==@sample_id".format(self.id_col))
            arr, pad_arr = self.select_arrs(df)
            valid_indices = np.where(np.count_nonzero(arr[:,:self.window_len-self.fh,self.target_index].astype(np.float32)>0,axis=1)>=self.min_nz)
            arr = arr[valid_indices]
            pad_arr = pad_arr[valid_indices]
            model_in, model_out, scale, weights  = self.preprocess(arr, pad_arr)
            yield model_in.astype(str), model_out.astype(float), scale.astype(float), weights.astype(float)

    def vocab_list(self, data):
        """
        Function to generate default embedding dimensions for categorical vars as 3rd root of no. of unique values.
        
        vocab_dict = {}
        embed_dict = {}
        
        for col in self.cat_col_list:
            col_unique_vals = data[col].astype(str).unique().tolist()
            vocab_dict[col] = col_unique_vals
            emb_dim = max(m.ceil(len(col_unique_vals)**0.33),2)
            embed_dict[col] = emb_dim
        """
        vocab_dict = {}
        for k,d in self.col_index_dict.items():
            if k in ['static_cat_indices','temporal_known_cat_indices','temporal_unknown_cat_indices']:
                if len(d[0])>0:
                    cols_val_list = []
                    cols_dim_list = []
                    for col in d[0]:
                        col_unique_vals = data[col].astype(str).unique().tolist()
                        emb_dim = max(m.ceil(len(col_unique_vals)**0.33),2)       
                        cols_val_list.append(col_unique_vals)
                        cols_dim_list.append(emb_dim)
                    vocab_dict[k] = [d[0], cols_val_list, cols_dim_list]
                           
        return vocab_dict
    
    def preprocess(self, sample_arr, pad_arr):
        """
        Preprocess_samples Tensorflow Ops & outputs resp.
        """
        sequence_len = int(self.window_len)
        max_input_len = int(self.window_len - self.fh)
        
        sid =  sample_arr[..., [self.id_index]].astype(str)
        target = sample_arr[..., [self.target_index]].astype(float)
        
        # target outlier correction
        SU = np.maximum(3.0*np.quantile(target[:,:max_input_len,:], q=0.9, axis=1, keepdims=True), 0)
        SL = np.minimum(3.0*np.quantile(target[:,:max_input_len,:], q=0.05, axis=1, keepdims=True), 0)
        target = np.clip(target, a_min=SL, a_max=SU)
        
        # scale target : target/target_mean
        target_nz_count = np.maximum(np.count_nonzero(np.abs(target[:,:max_input_len,:]), axis=1).reshape(-1,1,1), 1.0)
        target_sum = np.sum(np.abs(target[:,:max_input_len,:]), axis=1, keepdims=True)
        target_nz_mean = np.divide(target_sum, target_nz_count) + 1.0
        target_scaled = np.divide(target, target_nz_mean)
        
        # build model_in array  
        model_in = np.concatenate((sid, target_scaled), axis=-1)
        model_out = target_scaled[:,-self.fh:,:]
        
        if len(self.static_num_indices) > 0:
            static_num = sample_arr[..., self.static_num_indices].astype(float)
            # scale
            static_nz_count = np.maximum(np.count_nonzero(np.abs(static_num), axis=1).reshape(-1,1,len(self.static_num_indices)), 1.0)
            static_sum = np.sum(np.abs(static_num), axis=1, keepdims=True)
            static_nz_mean = np.divide(static_sum, static_nz_count) + 1.0
            static_num = np.divide(static_num, static_nz_mean)
            # merge
            model_in = np.concatenate((model_in, static_num), axis=-1)
            
        if len(self.static_cat_indices) > 0:
            static_cat = sample_arr[..., self.static_cat_indices].astype(str)
            # merge
            model_in = np.concatenate((model_in, static_cat), axis=-1)

        if len(self.temporal_known_num_indices) > 0:
            known_num = sample_arr[..., self.temporal_known_num_indices].astype(float)
            # scale
            known_nz_count = np.maximum(np.count_nonzero(np.abs(known_num), axis=1).reshape(-1,1,len(self.temporal_known_num_indices)), 1.0)
            known_sum = np.sum(np.abs(known_num), axis=1, keepdims=True)
            known_nz_mean = np.divide(known_sum, known_nz_count) + 1.0
            known_num = np.divide(known_num, known_nz_mean)
            # merge
            model_in = np.concatenate((model_in, known_num), axis=-1)

        if len(self.temporal_unknown_num_indices) > 0:
            unknown_num = sample_arr[..., self.temporal_unknown_num_indices].astype(float)
            # scale
            unknown_nz_count = np.maximum(np.count_nonzero(np.abs(unknown_num[:,:max_input_len,:]), axis=1).reshape(-1,1,len(self.temporal_unknown_num_indices)), 1.0)
            unknown_sum = np.sum(np.abs(unknown_num[:,:max_input_len,:]), axis=1, keepdims=True)
            unknown_nz_mean = np.divide(unknown_sum, unknown_nz_count) + 1.0
            unknown_num = np.divide(unknown_num, unknown_nz_mean)
            # merge
            model_in = np.concatenate((model_in, unknown_num), axis=-1)
   
        if len(self.temporal_known_cat_indices) > 0:
            known_cat = sample_arr[..., self.temporal_known_cat_indices].astype(str)
            # merge
            model_in = np.concatenate((model_in, known_cat), axis=-1)

        if len(self.temporal_unknown_cat_indices) > 0:
            unknown_cat = sample_arr[..., self.temporal_unknown_cat_indices].astype(str)
            # merge
            model_in = np.concatenate((model_in, unknown_cat), axis=-1)
            
        rel_age = np.broadcast_to((np.arange(0,sequence_len,1)/sequence_len).reshape(-1,1), target.shape)
        model_in = np.concatenate((model_in, rel_age), axis=-1) 
        
        # scale
        scale_in = np.broadcast_to(target_nz_mean, target.shape)
        model_in = np.concatenate((model_in, scale_in), axis=-1)
        scale_out = np.broadcast_to(target_nz_mean, model_out.shape)
            
        mask_list = []
        for pad_len in pad_arr:
            if pad_len > 0:
                mask = np.concatenate((-1*np.ones((1,pad_len)), np.ones((1,sequence_len-pad_len))), axis=1)
            else:
                mask = np.ones((1,sequence_len))
            mask_list.append(mask)

        # mask & relative age
        mask = np.vstack(mask_list).reshape(-1,sequence_len,1)
        model_in = np.concatenate((model_in, mask), axis=-1)

        # sample weights
        weights = np.squeeze(target_nz_mean)/np.quantile(np.squeeze(target_nz_mean), q=0.8)
        weights = np.clip(weights, a_min=0.5, a_max=1.0)
        weights = weights.reshape(-1,1)
        #weights = np.expand_dims(weights.reshape(-1,1), axis=-1)
        #weights = np.tile(weights, [1,sequence_len,1])
        
        return model_in, model_out, scale_out, weights
    
    def split_train_test(self, data):
        train_data = data[data[self.time_index_col]<=self.train_till].reset_index(drop=True)
        test_data = data[data[self.time_index_col]<=self.test_till].groupby(self.id_col).apply(lambda x: x[-self.window_len:]).reset_index(drop=True)
        return train_data, test_data
    
    def train_test_dataset(self, data, train_till, test_till):
        self.train_till = train_till
        self.test_till = test_till
        
        # check null
        null_status, null_cols = self.check_null(data)
        if null_status:
            print("NaN column(s): ", null_cols)
            raise ValueError("Column(s) with NaN detected!")
        
        # sort & split into train, test dfs
        data = self.sort_dataset(data)
        train_data, test_data = self.split_train_test(data)
        
        # check samples
        check_gen = self.data_generator(train_data)
        x, y, s, w = next(check_gen)
        
        num_features = x.shape[-1]
        
        trainset = tf.data.Dataset.from_generator(lambda: self.data_generator(train_data),
                                                  output_types=(tf.string, tf.float32, tf.float32, tf.float32),
                                                  output_shapes=(tf.TensorShape((None, self.window_len, num_features)),
                                                                 tf.TensorShape((None, self.fh, 1)),
                                                                 tf.TensorShape((None, self.fh, 1)),
                                                                 tf.TensorShape((None, 1))) )
        
        testset = tf.data.Dataset.from_generator(lambda: self.data_generator(test_data),
                                                output_types=(tf.string, tf.float32, tf.float32, tf.float32),
                                                output_shapes=(tf.TensorShape((None, self.window_len, num_features)), 
                                                               tf.TensorShape((None, self.fh, 1)),
                                                               tf.TensorShape((None, self.fh, 1)),
                                                               tf.TensorShape((None, 1))))
       
        return trainset, testset
    
    def infer_dataset(self, data, history_till, future_till):
        self.history_till = history_till
        self.future_till = future_till
        
        # check null
        null_status, null_cols = self.check_null(data)
        if null_status:
            print("NaN column(s): ", null_cols)
            raise ValueError("Column(s) with NaN detected!")
            
        # sort & filter to recent context
        data = self.sort_dataset(data)
        data = data[data[self.time_index_col]<=self.future_till].groupby(self.id_col).apply(lambda x: x[-self.window_len:]).reset_index(drop=True)
        arr, pad_arr, id_arr, date_arr = self.select_all_arrs(data)
        model_in, model_out, scale, _ = self.preprocess(arr, pad_arr)
        input_tensor = tf.convert_to_tensor(model_in.astype(str), dtype=tf.string)
        # for evaluation
        actuals_arr = model_out*scale
        
        if len(self.static_cat_col_list)>0:
            stat_arr_list = []
            for col, i in zip(self.static_cat_col_list, self.static_cat_indices):
                stat_arr = model_in[:,-1:,i].astype(str)
                stat_arr_list.append(stat_arr)    
            stat_arr = np.concatenate(stat_arr_list, axis=1)        
            actuals_df = pd.DataFrame(np.concatenate((id_arr.reshape(-1,1), stat_arr, actuals_arr.reshape(-1,self.fh)), axis=1))
            actuals_columns = ['id'] + self.static_cat_col_list + ['actual_{}'.format(i) for i in range(self.fh)]
            id_columns = ['id'] + self.static_cat_col_list
            actuals_df.columns = actuals_columns
            actuals_df = actuals_df.melt(id_vars=id_columns, value_name='actual').sort_values(id_columns).drop(columns=['variable'])
            actuals_df = actuals_df.rename_axis('index').sort_values(by=['id','index']).reset_index(drop=True)
            # merge with forecast period dates
            date_df = pd.DataFrame(date_arr.reshape(-1,)).rename(columns={0:'period'})
            actuals_df = pd.concat([actuals_df, date_df], axis=1)
            actuals_df['actual'] = actuals_df['actual'].astype(np.float32)
        else:
            actuals_df = pd.DataFrame(np.concatenate((id_arr.reshape(-1,1), actuals_arr.reshape(-1,self.fh)), axis=1))
            actuals_columns = ['id'] + ['actual_{}'.format(i) for i in range(self.fh)]
            id_columns = ['id']
            actuals_df.columns = actuals_columns
            actuals_df = actuals_df.melt(id_vars=id_columns, value_name='actual').sort_values(id_columns).drop(columns=['variable'])
            actuals_df = actuals_df.rename_axis('index').sort_values(by=['id','index']).reset_index(drop=True)
            # merge with forecast period dates
            date_df = pd.DataFrame(date_arr.reshape(-1,)).rename(columns={0:'period'})
            actuals_df = pd.concat([actuals_df, date_df], axis=1)
            actuals_df['actual'] = actuals_df['actual'].astype(np.float32)
         
        return [input_tensor, scale, id_arr, date_arr], actuals_df
    
    def baseline_infer_dataset(self, data, history_till, future_till, ignore_cols):
        self.history_till = history_till
        self.future_till = future_till
        
        # check null
        null_status, null_cols = self.check_null(data)
        if null_status:
            print("NaN column(s): ", null_cols)
            raise ValueError("Column(s) with NaN detected!")
            
        # sort & filter to recent context
        data = self.sort_dataset(data)
        data = data[data[self.time_index_col]<=self.future_till].groupby(self.id_col).apply(lambda x: x[-self.window_len:]).reset_index(drop=True)
        
        # zero out columns in ignore_cols for baseline forecast
        for col in ignore_cols:
            data[col] = np.where(data[self.time_index_col]>self.history_till, 0, data[col])
        
        arr, pad_arr, id_arr, date_arr = self.select_all_arrs(data)
        model_in, model_out, scale, _ = self.preprocess(arr, pad_arr)
        input_tensor = tf.convert_to_tensor(model_in.astype(str), dtype=tf.string)
        
        return [input_tensor, scale, id_arr, date_arr]

    


# In[ ]:




