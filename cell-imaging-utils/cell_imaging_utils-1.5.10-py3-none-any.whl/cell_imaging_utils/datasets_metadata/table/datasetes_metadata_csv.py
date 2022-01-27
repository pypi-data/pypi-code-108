
import logging
from cell_imaging_utils.datasets_metadata.table.datasetes_metadata_abstract_table import DatasetsMetaDataAbstractTable
import pandas as pd
import typing
from multipledispatch import dispatch
from numpy import number

log = logging.getLogger(__name__)

"""
DatasetsMetaDataSCV
------------------
SCV implementation of DatasetMetadataAbstract

"""


class DatasetMetadataSCV(DatasetsMetaDataAbstractTable):

    def __init__(self, destenation, source=None) -> None:
        super().__init__(destenation, source)
        if (self.source is not None):
            self.data = pd.read_csv(self.source)
        else:
             self.data = pd.DataFrame([],columns=[])
    def create(self):
        self.data.to_csv(self.destenation)
