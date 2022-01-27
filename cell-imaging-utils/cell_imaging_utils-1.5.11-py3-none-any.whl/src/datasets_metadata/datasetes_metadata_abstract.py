import logging
import typing
from abc import ABC, abstractmethod
import pandas as pd
from multipledispatch import dispatch

from numpy import number

log = logging.getLogger(__name__)

"""
DatasetsMetaDataAbstract
------------------
Abstract method th handle datasets metadata
the data is handled as DataFrame of pandas


"""

class DatasetsMetaDataAbstract:
     
     def __init__(self,destenation,source=None) -> None:
         self.source:str = source
         self.destenation:str = destenation
         self.data:pd.DataFrame = None
     
     @abstractmethod
     def create(self):
          pass
     
     def get_data(self)->pd.DataFrame:
          return self.data
    
     
     
     
     
     
     
     