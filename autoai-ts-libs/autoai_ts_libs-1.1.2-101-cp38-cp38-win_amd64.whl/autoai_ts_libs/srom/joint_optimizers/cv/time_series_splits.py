import logging
import numpy as np
import pandas as pd
from sklearn.model_selection._split import _BaseKFold
from sklearn.utils import indexable
from sklearn.utils.validation import _num_samples
from autoai_ts_libs.utils.messages.messages import Messages

LOGGER = logging.getLogger(__name__)


class TimeSeriesTrainTestSplit(_BaseKFold):
    """
    This class is for splitting time series into two part - \
    training and testing. \
    n_test_size is the number of datapoints selected from \
    the end of time series as the test data point.
    """
    
    def __init__(self, n_test_size=10, n_splits=1, overlap_len=0):
        self.n_splits = n_splits
        self.n_test_size = n_test_size
        self.overlap_len = overlap_len

    def split(self, X, y=None, groups=None):
        indexable_results = indexable(X, y, groups)
        X, y, groups = indexable_results[0], indexable_results[1], indexable_results[2]
        n_samples = _num_samples(X)

        if self.n_test_size > n_samples:
            raise ValueError(Messages.get_message(self.n_test_size, n_samples, message_id='AUTOAITSLIBS0018E'))

        if n_samples - self.n_test_size < self.n_test_size:
            LOGGER.warning(Messages.get_message(message_id='AUTOAITSLIBS0001W'))

        indices = np.arange(n_samples)
        test_starts = [n_samples-self.n_test_size]

        for test_start in test_starts:
            yield (indices[0:test_start], indices[test_start- self.overlap_len:n_samples])
