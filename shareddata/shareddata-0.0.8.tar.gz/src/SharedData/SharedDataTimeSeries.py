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
import subprocess
from subprocess import run, PIPE
import boto3

from SharedData.Logger import Logger
from SharedData.AWS import S3SyncDownloadTimeSeries

class SharedDataTimeSeries:

    def __init__(self, sharedDataPeriod, tag, value=None):    
        self.sharedDataPeriod = sharedDataPeriod
        self.tag = tag
        
        self.sharedDataFeeder = sharedDataPeriod.sharedDataFeeder
        self.sharedData = sharedDataPeriod.sharedDataFeeder.sharedData        

        self.period = sharedDataPeriod.period
        self.periodSeconds = sharedDataPeriod.periodSeconds               
        self.feeder = self.sharedDataFeeder.feeder

        # Time series dataframe
        self.data = pd.DataFrame()
        self.index = pd.Index([])
        self.columns = pd.Index([])
                        
        if value is None: #Read dataset tag
            dataset = sharedDataPeriod.dataset
            sharedData = sharedDataPeriod.sharedData
            feeder = self.sharedDataFeeder.feeder
        
            if not tag in dataset.index:
                raise ValueError('tag '+tag+' not found in dataset!')
            else:
                self.startDate = dataset['startDate'][tag]
                self.collections = dataset['collections'][tag].split(',')
                _symbols = pd.Index([])
                for collection in self.collections:                
                    _symbols = _symbols.union(sharedData.getSymbols(collection))   
                    if len(_symbols)==0:
                        raise Exception('collection '+collection+' has no symbols!')
                _timeidx = sharedDataPeriod.getTimeIndex(self.startDate)                
                self.index = _timeidx
                self.columns = _symbols                                       
                
            self.symbolidx = {}
            for i in range(len(self.columns)):
                self.symbolidx[self.columns.values[i]] = i
            self.ctimeidx = sharedDataPeriod.getContinousTimeIndex(self.startDate)

            #allocate memory
            isCreate = self.Malloc()
            if isCreate:
                if self.sharedData.s3read:
                    path, shm_name = self.getDataPath()
                    S3SyncDownloadTimeSeries(path, shm_name)
                self.Read()                
        
        else: # map existing dataframe
            self.startDate = value.index[0]
            self.index = value.index
            self.columns = value.columns            
                       
            self.symbolidx = {}
            for i in range(len(self.columns)):
                self.symbolidx[self.columns.values[i]] = i

            self.ctimeidx = self.sharedDataPeriod.getContinousTimeIndex(self.startDate)
            #allocate memory
            isCreate = self.Malloc(value=value)

    def getDataPath(self):        
        shm_name = self.sharedData.database
        shm_name = shm_name + '/' + self.sharedDataFeeder.feeder
        shm_name = shm_name + '/' + self.period + '/' + self.tag
        path = Path(os.environ['DATABASE_FOLDER'])
        path =  path / shm_name        
        if not os.path.isdir(path):
            os.makedirs(path)
        return path, shm_name

    def get_loc_symbol(self, symbol):
        if symbol in self.symbolidx.keys():
            return self.symbolidx[symbol]
        else:
            return np.nan

    def get_loc_timestamp(self, ts):
        istartdate = self.startDate.timestamp() #seconds
        if not np.isscalar(ts):
            tidx = self.get_loc_timestamp_Jit(ts, istartdate, \
                self.periodSeconds, self.ctimeidx)            
            return tidx
        else:
            tids = np.int64(ts) #seconds
            tids = np.int64(tids - istartdate)
            tids = np.int64(tids/self.periodSeconds)
            if tids<self.ctimeidx.shape[0]:
                tidx = self.ctimeidx[tids]
                return tidx
            else:
                return np.nan
    
    @staticmethod
    @jit(nopython=True, nogil=True, cache=True)
    def get_loc_timestamp_Jit(ts, istartdate, periodSeconds, ctimeidx):
        tidx = np.empty(ts.shape, dtype=np.float64)
        len_ctimeidx = len(ctimeidx)
        for i in range(len(tidx)):
            tid = np.int64(ts[i])
            tid = np.int64(tid-istartdate)
            tid = np.int64(tid/periodSeconds)
            if tid < len_ctimeidx:
                tidx[i] = ctimeidx[tid]
            else:
                tidx[i] = np.nan
        return tidx

    def getValue(self,ts,symbol):
        sidx = self.get_loc_symbol(symbol)
        tidx = self.get_loc_timestamp(ts)
        if (not np.isnan(sidx)) & (not np.isnan(tidx)):
            return self.data.values[np.int64(tidx),int(sidx)]
        else:
            return np.nan

    def setValue(self,ts,symbol,value):
        sidx = self.get_loc_symbol(symbol)
        tidx = self.get_loc_timestamp(ts)
        if (not np.isnan(sidx)) & (not np.isnan(tidx)):
            self.data.values[np.int64(tidx),int(sidx)] = value

    def setValues(self,ts,symbol,values):
        sidx = self.get_loc_symbol(symbol)
        tidx = self.get_loc_timestamp(ts)
        self.setValuesSymbolJit(self.data.values, tidx, sidx, values)
    
    @staticmethod
    @jit(nopython=True, nogil=True, cache=True)
    def setValuesSymbolJit(values,tidx,sidx,arr):
        if not np.isnan(sidx):
            s = np.int64(sidx)
            i = 0
            for t in tidx:
                if not np.isnan(t):
                    values[np.int64(t),s] = arr[i]
                i=i+1

    @staticmethod
    @jit(nopython=True, nogil=True, cache=True)
    def setValuesJit(values,tidx,sidx,arr):
        i = 0
        for t in tidx:
            if not np.isnan(t):
                j = 0
                for s in sidx:
                    if not np.isnan(s):
                        values[np.int64(t),np.int64(s)] = arr[i,j]
                    j=j+1
            i=i+1

    # C R U D
    def Malloc(self, value=None):
        tini=time.time()
        Logger.log.debug('Malloc %s/%s/%s ...%.2f%% ' % \
            (self.feeder,self.period,self.tag,0.0))        

        #Create write ndarray
        path, shm_name = self.getDataPath()
        fpath = path / ('shm_info.json')

        try: # try create memory file
            rows = len(self.index)
            cols = len(self.columns)
            nbytes = int(rows*cols*8)

            self.shm = shared_memory.SharedMemory(\
                name = shm_name,create=True, size=nbytes)

            self.shmarr = np.ndarray((rows,cols),\
                dtype=np.float64, buffer=self.shm.buf)
            
            if not value is None:
                self.shmarr[:] = value.values.copy()
            else:
                self.shmarr[:] = np.nan
            
            self.data = pd.DataFrame(self.shmarr,\
                        index=self.index,\
                        columns=self.columns,\
                        copy=False)
            
            if not value is None:
                value = self.data

            with open(str(fpath), 'w+') as outfile:
                shm_info = {
                    'shm_name':shm_name,
                    'index': self.data.index.values.tolist(),
                    'columns': self.data.columns.values.tolist()                                 
                    }
                json.dump(shm_info, outfile, indent=3)

            Logger.log.debug('Malloc create %s/%s/%s ...%.2f%% %.2f sec! ' % \
                (self.feeder,self.period,self.tag,100,time.time()-tini))            

            return True
        except:
            pass
        
        if fpath.is_file():
            with open(str(fpath), 'r') as infile:                
                shm_info = json.load(infile)                
                self.index = pd.Index(shm_info['index']).astype('datetime64[ns]')
                self.columns = pd.Index(shm_info['columns'])
                shm_name = shm_info['shm_name']
                rows = len(self.index)
                cols = len(self.columns)

                # map memory file
                self.shm = shared_memory.SharedMemory(\
                    name=shm_name, create=False)
                self.shmarr = np.ndarray((rows,cols),\
                    dtype=np.float64, buffer=self.shm.buf)
                self.data = pd.DataFrame(self.shmarr,\
                            index=self.index,\
                            columns=self.columns,\
                            copy=False)
                
                if not value is None:
                    iidx = value.index.intersection(self.data.index)
                    icol = value.columns.intersection(self.data.columns)
                    self.data.loc[iidx, icol] = value.loc[iidx, icol]

                Logger.log.debug('Malloc map %s/%s/%s ...%.2f%% %.2f sec! ' % \
                    (self.feeder,self.period,self.tag,100,time.time()-tini))      
        return False
      

    def Read(self):   
        path, shm_name = self.getDataPath()        
        years = [int(x.stem) for x in path.glob('*.npy') if x.is_file()]
        fpaths = [x for x in path.glob('*.npy') if x.is_file()]
        files = pd.DataFrame([years,fpaths]).T
        files.columns = ['year','fpath']
        files = files.sort_values(by='year')
        nfiles = len(files.index)
        if nfiles>0:
            tini=time.time() 
            Logger.log.debug('Reading %s/%s/%s ...%.2f%% ' % \
                (self.feeder,self.period,self.tag,0.0))   
            n=0
            for f in files.index:
                fpath=files.loc[f,'fpath']            
                arr = np.load(str(fpath),mmap_mode='r')
                r ,c = arr.shape
                if (r>0):                   
                    idxfpath = str(fpath).replace('.npy','.csv')
                    with open(idxfpath,'r') as f:
                        dfidx = f.read()
                    dfidx = dfidx.split(',')
                    sidx = [self.get_loc_symbol(s) for s in dfidx[1:]]
                    sidx = np.array(sidx)                    
                    ts = (arr[:,0]).astype(np.int64) #seconds
                    tidx = self.get_loc_timestamp(ts)

                    self.setValuesJit(self.data.values,tidx,sidx,arr[:,1:])
                n=n+1                

            Logger.log.debug('Reading %s/%s/%s ...%.2f%% %.2f sec! ' % \
                (self.feeder,self.period,self.tag,100*(n/nfiles),time.time()-tini))

    def Write(self, busdays=None, startDate=None):
        tini = time.time()
        
        lastdate = self.data.last_valid_index()
        if (lastdate is None) | (busdays is None):
            lastdate = self.startDate
        elif not busdays is None:
            lastdate -=  BDay(busdays)

        if not startDate is None:
            lastdate = startDate
        
        startdatestr = lastdate.strftime('%Y-%m-%d')
        Logger.log.debug('Writing %s/%s/%s from %s ...%.2f%% ' % \
            (self.feeder,self.period,self.tag,startdatestr,0.0))
        
        path, shm_name = self.getDataPath()        
        if not os.path.isdir(path):
            os.makedirs(path)        
            
        years = self.data.loc[lastdate:,:].index.year.unique()
        ny = len(years)
        cy = 0        
        for y in years:
            idx = self.data.index[self.data.index.year==y]
            dfyear = self.data.loc[idx,:].copy()
            dfyear = dfyear.dropna(how='all').dropna(axis=1,how='all')
            if dfyear.shape[0]>0:
                dfyear.index = (dfyear.index.astype(np.int64)/10**9).astype(np.int64)
                dfyear = dfyear.reset_index()

                fpath_npy = path / (str(y)+'.npy')
                np.save(str(fpath_npy),dfyear.values.astype(np.float64))
                cols = ','.join(dfyear.columns)
                fpath_csv = path / (str(y)+'.csv')
                with open(fpath_csv, 'w') as f:
                    f.write(cols)
                if self.sharedData.s3write:
                    self.S3SyncUpload(fpath_npy)
                    self.S3SyncUpload(fpath_csv)
                cy=cy+1      

        Logger.log.debug('Writing %s/%s/%s from %s ...%.2f%% %.2f sec!' % \
            (self.feeder,self.period,self.tag,startdatestr,100*cy/ny,time.time()-tini))        
        
    def S3SyncUpload(self,localfilepath):
        Logger.debug('Uploading to S3 '+localfilepath+' ...')
        try:
            remotefilepath = localfilepath.replace(\
                os.environ['DATABASE_FOLDER'],os.environ['S3_BUCKET'])            
            s3 = boto3.resource('s3')
            s3.Bucket(os.environ['S3_BUCKET']).upload_file(localfilepath,remotefilepath)
            Logger.debug('Uploading to S3 SUCESS!')
        except Exception as e:
            Logger.error('Uploading to S3 ERROR!')