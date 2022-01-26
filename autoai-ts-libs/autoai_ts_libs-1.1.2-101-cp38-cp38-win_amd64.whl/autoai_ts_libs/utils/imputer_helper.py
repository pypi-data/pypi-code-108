import copy
from autoai_ts_libs.srom.imputers.interpolators import PreMLImputer

import numpy as np
import pandas as pd
import copy
from autoai_ts_libs.utils.messages.messages import Messages
from sklearn.pipeline import Pipeline
import inspect
import logging
LOGGER = logging.getLogger(__name__)

def search_best_imputer(X, imputers, **imputer_params):
    """
    Method to select the best imputer.
    """
    best_imputer = None
    best_imputer_score = 0.0
    imputer_scores = []
    if len(imputers) < 1:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0061E'))

    if len(imputers) == 1:
        best_imputer = imputers[0]
        imputer_scores.append((best_imputer, best_imputer_score))
    else:
        random_sample_size = None
        if len(X) > 3000:
            random_sample_size = 3000
        pre_ml_imputer = PreMLImputer(random_sample_size=random_sample_size)
        pre_ml_imputer.default_options = imputers
        X = copy.copy(X)
        pre_ml_imputer.transform(X)
        best_imputer, best_imputer_score = pre_ml_imputer.get_best_imputer()
        imputer_scores = pre_ml_imputer.get_performance_score()

    if best_imputer.__class__.__name__!='fill' and ("imputer_fill_type" in imputer_params.keys() or
                                                    "imputer_fill_value" in imputer_params.keys()):
        LOGGER.warning(Messages.get_message(message_id='AUTOAITSLIBS0003W'))

    if best_imputer.__class__.__name__=='fill':
        if "imputer_fill_type" in imputer_params.keys():
            if imputer_params['imputer_fill_type'] == 'mean' or imputer_params['imputer_fill_type'] == 'median':
                if "imputer_fill_value" in imputer_params.keys():
                    LOGGER.warning(Messages.get_message(message_id='AUTOAITSLIBS0002W'))


    return best_imputer, best_imputer_score, imputer_scores 

def examine_missing_values(X, missing_val_identifier, imputation_threshold, only_detect=True):
    """
    Method to check if the input data X has missing values and the missing ratio is under the given threshold.
    """
    if X is None:
        return False

    if np.isnan(missing_val_identifier):
        x_mask = np.isnan(X)
    else:
        x_mask = (X == missing_val_identifier)

    if (np.count_nonzero(x_mask) == 0):
        return False
    else:
        if not only_detect:
            for i in range(x_mask.shape[1]):
                if np.count_nonzero(x_mask[:, i]) / len(x_mask) > imputation_threshold:
                    print(i, np.count_nonzero(x_mask[:, i]) / len(x_mask))
                    raise Exception(Messages.get_message(str(i + 1), message_id='AUTOAITSLIBS0060E'))

    return True

def get_skip_imputer_params(pipeline):
    tmp_fit_params = {}
    if isinstance(pipeline, Pipeline):
        for step_name_ in pipeline.named_steps.keys():
            if step_name_.endswith('_imputer'):
                if 'fit_params' in inspect.signature(pipeline.named_steps[step_name_].fit).parameters.keys():
                    tmp_fit_params[step_name_ + '__skip_fit'] = True
    return tmp_fit_params
        
