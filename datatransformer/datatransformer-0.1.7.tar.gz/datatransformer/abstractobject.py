#pylint: disable=C0114,C0115,C0116
import abc

class DataTransformer(abc.ABC):

    @property
    def dimensions(self):
        pass

    @property
    def dense_features(self):
        pass

    @property
    def sparse_features(self):
        pass

    @property
    def feature_columns(self):
        pass

    @property
    def labels(self):
        pass

    @classmethod
    def to_dataset(cls):
        pass
