import os
from pathlib import Path
import pandas as pd
import numpy as np
import time
import subprocess

from SharedData.Logger import Logger
from SharedData.AWS import S3SyncDownloadMetadata

class Metadata():
    
    def __init__(self, name, s3read=False, s3write=False):
        self.name = name
        self.s3read = s3read
        self.s3write = s3write
        self.xls = {}
        self.static = pd.DataFrame([])        
        self.symbols = pd.DataFrame([],dtype=str)
        self.series = pd.Series([],dtype=str)
        self.fpath = Path(os.environ['DATABASE_FOLDER'])

        self.pathxls = self.fpath /  ('Metadata/'+name+'.xlsx')
        self.pathpkl = self.fpath /  ('Metadata/'+name+'.pkl')
        self.pathsymbols = self.fpath /  ('Metadata/'+name+'_SYMBOLS.pkl')
        self.pathseries = self.fpath /  ('Metadata/'+name+'_SERIES.pkl')

        if not os.path.isdir(self.pathpkl.parents[0]):
            os.makedirs(self.pathpkl.parents[0]) 

        if (self.s3read):
            S3SyncDownloadMetadata(self.pathpkl,self.name)
            
        # prefer read pkl
        if self.pathpkl.is_file():            
            tini = time.time()
            Logger.log.debug('Loading symbols collection ' + name + ' ...')
            self.static = pd.read_pickle(self.pathpkl)
            self.static = self.static.sort_index()
            if self.pathsymbols.is_file():
                self.symbols = pd.read_pickle(self.pathsymbols)
                self.symbols = self.symbols.sort_index()
            if self.pathseries.is_file():
                self.series = pd.read_pickle(self.pathseries)
                self.series = self.series.sort_index()
            Logger.log.debug('%.2f done!' % (time.time()-tini))
        elif self.pathxls.is_file():
            tini = time.time()
            Logger.log.debug('Loading symbols collection ' + name + ' ...')
            self.xls = pd.read_excel(self.pathxls,sheet_name=None)
            self.static = self.xls['static']
            if 'symbols' in self.xls.keys():
                self.symbols = self.xls['symbols']
            if not self.static.empty:
                self.static = self.static.set_index(self.static.columns[0])
            if not self.symbols.empty:
                self.symbols = self.symbols.set_index(self.symbols.columns[0])
            Logger.log.debug('%.2f done!' % (time.time()-tini))


    def save(self,save_excel=False):
        tini = time.time()
        Logger.log.debug('Saving symbols collection ' + self.name + ' ...')  
        if not os.path.isdir(self.pathpkl.parents[0]):
            os.makedirs(self.pathpkl.parents[0])                          
        self.static.to_pickle(self.pathpkl)
        if not self.symbols.empty:
            self.symbols.to_pickle(self.pathsymbols)
        if not self.series.empty:
            self.series.to_pickle(self.pathseries)
        if save_excel:
            writer = pd.ExcelWriter(self.pathxls, engine='xlsxwriter')            
            self.static.to_excel(writer,sheet_name='static')        
            if not self.symbols.empty:
                self.symbols.to_excel(writer,sheet_name='symbols')
            writer.save()        
        self.debug('%.2f done!' % (time.time()-tini))
    
    def mergeUpdate(self,newdf):
        ddidx = newdf.index.duplicated()
        if ddidx.any():
            newdf = newdf[~newdf.index.duplicated(keep='first')]
            Logger.log.warning('Collection merge duplicated index for new dataframe!')
        ddidx = self.static.index.duplicated()
        if ddidx.any():
            self.static = self.static[~self.static.index.duplicated(keep='first')]
            Logger.log.warning('Collection merge duplicated index for static dataframe!')
        newcolsidx = ~newdf.columns.isin(self.static.columns)
        if newcolsidx.any():
            newcols = newdf.columns[newcolsidx]
            for c in newcols:
                self.static.loc[:,c] = newdf[c]                
        newidx = ~newdf.index.isin(self.static.index)
        if newidx.any():
            self.static = self.static.reindex(index=self.static.index.union(newdf.index))
        newcol = ~newdf.columns.isin(self.static.columns)
        if newcol.any():
            self.static = self.static.reindex(columns=self.static.columns.union(newdf.columns))
        self.static.update(newdf)
