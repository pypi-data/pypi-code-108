import pandas as pd

from . import data_aggregation
from . import data_collection
from . import importing 
from . import reports


class DataHandler:
    """ The main part of this package - an object to handle all the data. """
    def __init__(self):
        pass

    def load_csv(self, csv_path: str):
        pass

    def load_json(self, json_path: str):
        pass

    def load_data_path(self, path: str):
        filetype = path.split(".")[-1]

        if filetype == "csv":
            self.data = self.load_csv(path)
        elif filetype == "json":
            self.data = self.load_json(path)
