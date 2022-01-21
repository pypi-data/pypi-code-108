from abc import ABC


class DataStorage(ABC):

    def __init__(self, args):

        self.args = args

    # abstract method
    def load_dataset(self, spark, read_all=True):
        pass

    # abstract method
    def save_dataset(self, df, output_dest):
        pass