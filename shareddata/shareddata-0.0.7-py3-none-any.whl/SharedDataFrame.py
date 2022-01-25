# THIRD PARTY LIBS
import os,sys
import pandas as pd
import numpy as np
import json
import time

from numba import jit
from pandas.tseries.offsets import BDay
from pathlib import Path
from multiprocessing import shared_memory

from SharedData.Logger import Logger

class SharedDataFrame:

    def __init__(self, sharedDataPeriod, tag, df=None, malloc=True):    
        self.sharedDataPeriod = sharedDataPeriod
        self.tag = tag
        self.tagstr = self.tag.strftime('%Y%m%d%H%M')
        
        self.sharedDataFeeder = sharedDataPeriod.sharedDataFeeder
        self.feeder = sharedDataPeriod.sharedDataFeeder.feeder
        self.sharedData = sharedDataPeriod.sharedDataFeeder.sharedData

        self.period = sharedDataPeriod.period
        self.periodSeconds = sharedDataPeriod.periodSeconds               
        
        # Time series dataframe
        self.data = pd.DataFrame()
                        
        if df is None: #Read dataset tag  
            if malloc:          
                #allocate memory
                isCreate = self.Malloc()
                if not isCreate:
                    df = self.Read()
                    if not df.empty:
                        self.Malloc(df)
            else:
                self.data = self.Read()
        else: # map existing dataframe   
            #drop non number fields   
            df = df._get_numeric_data().astype(np.float64)
            #allocate memory
            isCreate = self.Malloc(df=df)

    #GETTERS AND SETTERS
    def getDataPath(self):        
        shm_name = self.sharedData.database
        shm_name = shm_name + '/' + self.sharedDataFeeder.feeder
        shm_name = shm_name + '/' + self.period + '/' + self.tag
        path = Path(os.environ['DATABASE_FOLDER'])
        path =  path / shm_name        
        if not os.path.isdir(path):
            os.makedirs(path)
        return path, shm_name

    # C R U D
    def Malloc(self, df=None):
        tini=time.time()
        Logger.log.debug('Malloc %s/%s/%s ...%.2f%% ' % \
            (self.feeder,self.period,self.tagstr,0.0))      

        #Create write ndarray
        path, shm_name = self.getDataPath()
        jsonpath = path / (self.tagstr+'.json')
        npypath = path / (self.tagstr+'.npy')

        trymap = False
        if not df is None:
            rows = len(df.index)
            cols = len(df.columns)
            nbytes = int(rows*cols*8)

            try:
                self.shm = shared_memory.SharedMemory(\
                    name = shm_name,create=True, size=nbytes)
                self.shmarr = np.ndarray((rows,cols),\
                    dtype=np.float64, buffer=self.shm.buf)            
                self.shmarr[:] = df.values.copy()
                self.data = pd.DataFrame(self.shmarr,\
                    index=df.index,\
                    columns=df.columns,\
                    copy=False)                                

                with open(str(jsonpath), 'w+') as outfile:
                    shm_info = {
                        'shm_name':shm_name,
                        'index': self.data.index.values.tolist(),
                        'columns': self.data.columns.values.tolist()                                 
                        }
                    json.dump(shm_info, outfile, indent=3)

                Logger.log.debug('Malloc create %s/%s/%s ...%.2f%% %.2f sec! ' % \
                    (self.feeder,self.period,self.tagstr,100,time.time()-tini))                
                return True
            except:
                trymap=True

        if (jsonpath.is_file()) & ((df is None) | (trymap)):
            with open(str(jsonpath), 'r') as infile:
                try:
                    shm_info = json.load(infile)
                    _index = pd.Index(shm_info['index'])
                    _columns = pd.Index(shm_info['columns'])
                    _shm_name = shm_info['shm_name']
                    rows = len(_index)
                    cols = len(_columns)
                    # map memory file
                    self.shm = shared_memory.SharedMemory(\
                        name=_shm_name, create=False)
                    self.shmarr = np.ndarray((rows,cols),\
                        dtype=np.float64, buffer=self.shm.buf)
                    self.data = pd.DataFrame(self.shmarr,\
                                index=_index,\
                                columns=_columns,\
                                copy=False)

                    if not df is None:
                        iidx = df.index.intersection(self.data.index)
                        icol = df.columns.intersection(self.data.columns)
                        self.data.loc[iidx, icol] = df.loc[iidx, icol].copy()
                                            
                    Logger.log.debug('Malloc map %s/%s/%s ...%.2f%% %.2f sec! ' % \
                        (self.feeder,self.period,self.tagstr,100,time.time()-tini))                    
                    return True
                except:
                    return False
        else:
            return False
      
    def Read(self):   
        tini = time.time()
        path, shm_name = self.getDataPath()
        jsonpath = path / (self.tagstr+'.json')
        npypath = path / (self.tagstr+'.npy')
            
        if (jsonpath.is_file()) & (npypath.is_file()):
            Logger.log.debug('Reading %s/%s/%s ...%.2f%% ' % \
                (self.feeder,self.period,self.tagstr,0.0))  
            with open(str(jsonpath), 'r') as infile:
                try:
                    shm_info = json.load(infile)
                    _index = pd.Index(shm_info['index'])
                    _columns = pd.Index(shm_info['columns'])
                    _shm_name = shm_info['shm_name']
                    rows = len(_index)
                    cols = len(_columns)
                    values = np.load(str(npypath),mmap_mode='r')

                    df = pd.DataFrame(values,\
                        index=_index,\
                        columns=_columns)

                    Logger.log.debug('Reading %s/%s/%s ...%.2f%% %.2f sec! ' % \
                        (self.feeder,self.period,self.tagstr,100,time.time()-tini))
                    return df
                except:
                    pass
                    Logger.log.error('File corrupted %s/%s/%s ...%.2f%% %.2f sec! ' % \
                        (self.feeder,self.period,self.tagstr,100,time.time()-tini))                
        return pd.DataFrame([])

    def Write(self,startDate=[]):
        tini = time.time()
        Logger.log.debug('Writing %s/%s  ...%.2f%% ' % \
            (self.period,self.tagstr,0.0))        

        path, shm_name = self.getDataPath()
        jsonpath = path / (self.tagstr+'.json')
        npypath = path / (self.tagstr+'.npy')
        with open(str(jsonpath), 'w+') as outfile:
            shm_info = {
                'shm_name':shm_name,
                'index': self.data.index.values.tolist(),
                'columns': self.data.columns.values.tolist()                                 
                }
            json.dump(shm_info, outfile, indent=3)
        
        np.save(str(npypath),self.data.values.astype(np.float64))

        Logger.log.debug('Writing %s/%s ...%.2f%% %.2f sec!' % \
            (self.period,self.tagstr,100,time.time()-tini))
        
