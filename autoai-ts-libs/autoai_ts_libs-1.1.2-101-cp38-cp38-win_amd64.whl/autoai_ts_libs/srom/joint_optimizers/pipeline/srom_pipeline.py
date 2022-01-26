import collections
import copy
import logging
import multiprocessing
import warnings

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

LOGGER = logging.getLogger(__name__)


class SROMPipeline(BaseEstimator, object):
    """
        SROMPipeline is based on standard pipeline classes such as sklearn.pipeline.Pipeline \
    and pyspark.ml.Pipeline. But it has many additional utilities which \
    enhance the data science experience. \
    Like the known concept of pipeline, the idea is to assemble several steps that can be \
    cross-validated together while setting different parameters. \
    The major differentiation on these lines being that SROMPipeline allows \
    for multiple techniques to be configured for each step so that it will try all possible \
    combinations of options for that step with all other options for other steps and runs such \
    combination paths to allow model selection. For each of the such paths created, \
    it tries different parameters and chooses the best combination of parameters for techniques \
    in that path. For this, it enables various parameter settings as allowed by SROMParamGrid \
    implementation.
    Example:
        from autoai_ts_libs.srom.pipeline.srom_pipeline import SROMPipeline \
        from sklearn.datasets import make_classification \
        from sklearn.linear_model import LogisticRegression \
        from sklearn.svm import SVC \
        from sklearn.decomposition import PCA \
        from sklearn.model_selection import train_test_split \
        from sklearn.metrics import roc_curve \
        n_estimator = 10 \
        X, y = make_classification(n_samples=800) \
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5) \
        pca = PCA() \
        rt_lm = LogisticRegression() \
        svc = SVC() \
        pipeline = SROMPipeline() \
        # if your dataset is a single dataframe including the target column, \
        # you could also use add_input_meta_data to indicate that \
        # pipeline.add_input_meta_data(id_column = 'id', label_column = 'label') \
        pipeline.set_stages([[PCA()],[LogisticRegression(), SVC()]]) \
        pipeline.create_graph() \
        pipeline.execute(X_train, y_train) \
        model = pipeline.fit(X_train, y_train) \
        predictions = pipeline.predict(X_test) \
    """

    SOURCE_NODE_LABEL = "Start"

    def __init__(self):
        pass
          
    @property
    def paths(self):
        return self._sromgraph.paths

    @property
    def sromgraph(self):
        return self._sromgraph

    @property
    def stages(self):
        return self._sromgraph.stages

