import pandas as pd
import numpy as np

import humailib.hasher as hh

class ProductCharacteristicsHelper:
    
    def __init__(self, gbq, table, product_column = 'Product_ID'):
        
        self.gbq = gbq
        self.table = table
        self.product_column = product_column
        self.df = self.__download()
        return
    
    def __download(self):
        
        self.df = self.gbq.download_table_to_pandas(self.table)
        return self.df
    
    def upload(self):
        
        self.gbq.upload_and_replace_table(self.df, self.table)
    
    def add_or_replace_columns(self, df, columns=None):
        
        if columns is None:
            columns = [c for c in df.columns if c != self.product_column]
            
        if self.df is None:
            print("[ProductCharacteristicsHelper::add_columns] table {} does not exist, creating...".format(self.table))
            self.df = df[columns].copy()
        else:
            print("[ProductCharacteristicsHelper::add_column] table {} exists, merging...".format(self.table))
            for c in columns:
                if c in self.df:
                    del self.df[c]

            self.df = self.df.merge(df[[self.product_column] + columns], on=self.product_column, how='outer')
            
        return self.df
    
    
class CustomerCharacteristicsHelper:
    
    def __init__(self, gbq, table, cid_column = 'Customer_ID', encryption = False):
        
        self.gbq = gbq
        self.table = table
        self.cid_column = cid_column
        self.encryption = encryption
        self.df = self.__download()
        return
    
    def __download(self):
        
        self.df = self.gbq.download_table_to_pandas(self.table)
        if self.df is not None and self.encryption:
            hh.decrypt_columns(self.df, columns=[self.cid_column])
        return self.df
    
    def upload(self):
        
        if self.df is not None and self.encryption:
            hh.encrypt_columns(self.df, columns=[self.cid_column])
        self.gbq.upload_and_replace_table(self.df, self.table)
    
    def add_or_replace_columns(self, df, columns=None):
        
        if columns is None:
            columns = [c for c in df.columns if c != self.cid_column]
            
        if self.df is None:
            print("[CustomerCharacteristicsHelper::add_columns] table {} does not exist, creating...".format(self.table))
            self.df = df[[self.cid_column] + columns].copy()
        else:
            print("[CustomerCharacteristicsHelper::add_column] table {} exists, merging...".format(self.table))
            for c in columns:
                if c in self.df:
                    del self.df[c]

            self.df = self.df.merge(df[[self.cid_column] + columns], on=self.cid_column, how='outer')
            
        return self.df
            
            
        
