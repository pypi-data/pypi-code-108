import logging
import pandas as pd
import typing
from multipledispatch import dispatch
from cell_imaging_utils.datasets_metadata.dict.datasetes_metadata_abstract_dict import DatasetsMetaDataAbstractDict

log = logging.getLogger(__name__)

"""
DatasetsMetaDataPickle
------------------
Pickle implementation of DatasetMetadataAbstract

"""


class DatasetMetadataPickle(DatasetsMetaDataAbstractDict):

    def __init__(self, destenation, source=None) -> None:
        super().__init__(destenation, source)
        if (self.source is not None):
            self.data = pd.read_pickle(self.source)
        else:
            self.data = pd.DataFrame([])

    def create(self):
        self.data.to_pickle(self.destenation)
