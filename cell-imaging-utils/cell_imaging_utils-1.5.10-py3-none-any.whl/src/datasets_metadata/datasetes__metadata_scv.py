
import logging
import pandas as pd
import typing
from multipledispatch import dispatch
from src.datasets_metadata.datasetes__metadata_abstract import DatasetMetadataAbstract
from numpy import number

log = logging.getLogger(__name__)

"""
DatasetsMetaDataSCV
------------------
SCV implementation of DatasetMetadataAbstract

"""

class DatasetMetadataSCV(DatasetMetadataAbstract):
     
     def __init__(self,destenation,source=None) -> None:
         super().__init__(source,destenation)
         if (self.source is not None):
            self.data = pd.read_csv(self.source)
     
     def create(self):
          self.data.to_csv(self.destenation)
     
     
     
     
     
