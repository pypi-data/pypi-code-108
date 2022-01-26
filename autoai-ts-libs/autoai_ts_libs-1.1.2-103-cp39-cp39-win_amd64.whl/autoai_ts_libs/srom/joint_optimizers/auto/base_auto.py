import logging
import time
import uuid
import warnings
from abc import ABC, abstractmethod
from operator import itemgetter
import math
import tempfile
import os
import numpy as np
from sklearn.base import BaseEstimator
from autoai_ts_libs.utils.messages.messages import Messages
from autoai_ts_libs.srom.joint_optimizers.pipeline.srom_param_grid import SROMParamGrid
LOGGER = logging.getLogger(__file__)


class SROMAuto(ABC):
    """
    == BASE / ABSTRACT == \
    (adding this comment till standard nomenclature is not generated)
    An SROMAuto class implements the default version of the pipeline which other Auto pipelines \
    will build upon.
    """
    @abstractmethod
    def fit(self, X, y, **fit_params):
        pass

    @abstractmethod
    def predict(self, X):
        pass


class SROMAutoPipeline(SROMAuto, BaseEstimator):
    """
    == BASE / ABSTRACT == \
    (adding this comment till standard nomenclature is not generated)
    """

    @abstractmethod
    def __init__(
        self,
        level,
        save_prefix,
        execution_platform,
        cv,
        scoring,
        stages,
        execution_time_per_pipeline,
        num_options_per_pipeline_for_random_search,
        num_option_per_pipeline_for_intelligent_search,
        total_execution_time,
        bayesian_paramgrid,
        rbopt_paramgrid,
        param_grid,
        execution_round,
        **kwarg
    ):

        self.level = level
        self.save_prefix = save_prefix
        self.execution_platform = execution_platform
        self.cv = cv
        self.scoring = scoring
        self.stages = stages
        self.execution_time_per_pipeline = execution_time_per_pipeline
        self.num_options_per_pipeline_for_random_search = (
            num_options_per_pipeline_for_random_search
        )
        self.num_option_per_pipeline_for_intelligent_search = (
            num_option_per_pipeline_for_intelligent_search
        )
        self.total_execution_time = total_execution_time
        self.bayesian_paramgrid = bayesian_paramgrid
        self.rbopt_paramgrid = rbopt_paramgrid
        self.execution_round = execution_round

        # internal parameters to be optimized in subsequent phase
        self._top_k_bottom_nodes = 3
        self._top_k_paths = 3
        #self.best_estimator_so_far = None
        self.best_score_so_far = None
        self.explored_estimator = []
        self.explored_score = []
        self.csv_filename = ""
        self.dill_filename = ""
        self.estimator_id = 1
        self.best_path_info = None
        self.number_of_combinations = 0
        self.param_grid = param_grid
        # setting execution environment
        if execution_platform == "spark":
            self.execution_platform = "spark_node_random_search"
        elif execution_platform == "celery":
            self.execution_platform = "celery_node_random_search"
        else:
            pass

        if execution_platform is None:
            self.execution_platform = "spark_node_random_search"

        if len(kwarg) > 0:
            if 'best_estimator_so_far' in kwarg.keys():
                self.best_estimator_so_far = kwarg['best_estimator_so_far']
    

    @abstractmethod
    def _initialize_default_stages(self):
        pass

    def _get_sklearn_str_repr(self, sk_pipeline):
        str_rep = "["
        for sI in sk_pipeline.steps:
            str_rep = str_rep + str(sI) + ","
        str_rep = str_rep + "]"
        return str_rep.replace(" ", "").replace("\n", "")

    @abstractmethod
    def fit(self, X, y):
        
        if self.best_estimator_so_far:
            self.best_estimator_so_far.fit(X, y)
        else:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0016E'))
        return self

    @abstractmethod
    def predict(self, X):

        if self.best_estimator_so_far:
            return self.best_estimator_so_far.predict(X)

    def predict_proba(self, X):

        if self.best_estimator_so_far:
            if 'predict_proba' in dir(self.best_estimator_so_far):
                return self.best_estimator_so_far.predict_proba(X)
            elif 'decision_function' in dir(self.best_estimator_so_far):
                return self.best_estimator_so_far.decision_function(X)
            else:
                raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0017E'))

    def get_params(self, deep=True):
        ans = super().get_params(deep=deep)
        ans['best_estimator_so_far'] = self.best_estimator_so_far
        return ans
