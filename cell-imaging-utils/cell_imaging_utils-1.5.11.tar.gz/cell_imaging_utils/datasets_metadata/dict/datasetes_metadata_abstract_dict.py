import logging
import typing
from abc import ABC, abstractmethod
import pandas as pd
from multipledispatch import dispatch
from cell_imaging_utils.datasets_metadata.datasetes_metadata_abstract import DatasetsMetaDataAbstract

from numpy import number

log = logging.getLogger(__name__)

"""
DatasetsMetaDataAbstractDict
------------------
Abstract method th handle datasets metadata
the data is handled as DataFrame of pandas
has table shape


"""

class DatasetsMetaDataAbstractDict(DatasetsMetaDataAbstract):
     
     def __init__(self,destenation,source=None) -> None:
          super().__init__(destenation,source)
     

     
     
     
     
     
     
     
     