import tempfile
from pangeamt_nlp.multilingual_ressource import Dataset
from typing import Union


class DatasetCleaner:
    def __init__(self, dataset:Union[Dataset, str]):
        self._dataset = Dataset(dataset) if type(dataset) is str else dataset
        with tempfile.TemporaryDirectory() as tmpdirname:
            pass

    def get_dataset(self):
        return self._dataset
    dataset = property(get_dataset)
