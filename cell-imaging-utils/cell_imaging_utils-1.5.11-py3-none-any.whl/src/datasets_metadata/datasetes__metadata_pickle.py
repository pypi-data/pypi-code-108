import logging
import pandas as pd
import typing
from multipledispatch import dispatch
from src.datasets_metadata.datasetes__metadata_abstract import DatasetMetadataAbstract

log = logging.getLogger(__name__)

"""
DatasetsMetaDataPickle
------------------
Pickle implementation of DatasetMetadataAbstract

"""

class DatasetMetadataPickle(DatasetMetadataAbstract):
     
     def __init__(self,destenation,source=None) -> None:
         super().__init__(source,destenation)
         if (self.source is not None):
            self.data = pd.read_pickle(self.source)
     
     def create(self):
          self.data.to_pickle(self.destenation)
     
     
     
     