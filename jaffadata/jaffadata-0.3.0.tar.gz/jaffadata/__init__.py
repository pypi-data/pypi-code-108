import importlib.metadata

from jaffadata.core.dataset import AudioDataset, Dataset, DataSubset
from jaffadata.core.labels import binarize


concat = DataSubset.concat

__version__ = importlib.metadata.version(__name__)

__all__ = [
    '__version__',
    'AudioDataset',
    'Dataset',
    'DataSubset',
    'binarize',
    'concat',
]
