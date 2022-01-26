# ************* Begin Copyright - Do not add comments here **************
#   Licensed Materials - Property of IBM
#
#   (C) Copyright IBM Corp. 2021, All Rights Reserved
#
# The source code for this program is not published or other-
# wise divested of its trade secrets, irrespective of what has
# been deposited with the U.S. Copyright Office.
# **************************** End Copyright ***************************

import numpy as np
from autoai_ts_libs.watfore.watfore_utils import WatForeUtils
from autoai_ts_libs.utils.predict import _PredictScorer
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from autoai_ts_libs.utils.messages.messages import Messages

def make_scorer(score_func, *, greater_is_better=True, **kwargs):
    """Make a scorer from a performance metric or loss function.
    This factory function wraps scoring functions for use in GridSearchCV
    and cross_val_score. It takes a score function, such as ``accuracy_score``,
    ``mean_squared_error``, ``adjusted_rand_index`` or ``average_precision``
    and returns a callable that scores an estimator's output.
    Read more in the :ref:`User Guide <scoring>`.
    Parameters
    ----------
    score_func : callable,
        Score function (or loss function) with signature
        ``score_func(y, y_pred, **kwargs)``.
    greater_is_better : boolean, default=True
        Whether score_func is a score function (default), meaning high is good,
        or a loss function, meaning low is good. In the latter case, the
        scorer object will sign-flip the outcome of the score_func.
    **kwargs : additional arguments
        Additional parameters to be passed to score_func.
    Returns
    -------
    scorer : callable
        Callable object that returns a scalar score; greater is better.
    """
    sign = 1 if greater_is_better else -1
    cls = _PredictScorer
    return cls(score_func, sign, kwargs)

def neg_avg_symmetric_mean_absolute_percentage_error(y_true, y_pred):
    return compute_average_matric("neg_avg_symmetric_mean_absolute_percentage_error", y_true, y_pred)

def avg_r2(y_true, y_pred):
    return compute_average_matric("avg_r2", y_true, y_pred)

def neg_avg_root_mean_squared_error(y_true, y_pred):
    return compute_average_matric("neg_avg_root_mean_squared_error", y_true, y_pred)

def neg_avg_mean_absolute_error(y_true, y_pred):
    return compute_average_matric("neg_avg_mean_absolute_error", y_true, y_pred)

def compute_average_matric(scoring, y_true, y_pred):
    if (isinstance(y_true, list)):
        column_is_target = False
        number_targets = len(y_true)
    else:
        column_is_target = True
        number_targets = y_true.shape[1]

    if (number_targets > 1 and ((scoring == "neg_avg_mean_absolute_error") or (scoring == "neg_avg_root_mean_squared_error"))):
        raise Exception(Messages.get_message(scoring, message_id='AUTOAITSLIBS0079E'))
    matric_value = []
    for i in range(number_targets):  # one TS
        if (column_is_target):
            y1D, y_pred1D = y_true[:, i].reshape(-1, 1), y_pred[:, i].reshape(-1, 1)
        else:
            y1D, y_pred1D = y_true[i].reshape(-1, 1), y_pred[i].reshape(-1, 1)

        matric_value1D = compute_matric(scoring, y1D, y_pred1D)

        if i == 0:
            matric_value = [matric_value1D]
        else:
            matric_value.append(matric_value1D)

    if number_targets > 1:  # MTS
        return -np.array(matric_value).mean(axis=0)
    else:  # UTS
        return -matric_value[0]

def compute_matric(scoring, y_true, y_pred):
    y_true, y_pred = np.array(y_true).ravel(), np.array(y_pred).ravel()

    # exclude nan based on y_true:
    idx = ~np.isnan(y_true)
    y_true, y_pred = y_true[idx], y_pred[idx]
    # exclude nan based on y_pred:
    idx = ~np.isnan(y_pred)
    y_true, y_pred = y_true[idx], y_pred[idx]

    if len(y_true) == 0 or len(y_pred) == 0:
        return np.nan

    try:
        # No multioutput='raw_values' param, so below functions return scalars
        if (scoring == "neg_avg_mean_absolute_error"):
            mae = mean_absolute_error(y_true, y_pred)
            return mae
        elif (scoring == "neg_avg_root_mean_squared_error"):
            mse = mean_squared_error(y_true, y_pred)
            return mse
        elif (scoring == "avg_r2"):
            r2 = r2_score(y_true, y_pred)
            # A constant model that always predicts the expected value of y, disregarding the input features,
            # would get a R^2 score of 0.0.
            if max(abs(y_pred - y_true)) < 1e-12:
                r2 = 1.0
            return r2
        elif (scoring == "neg_avg_symmetric_mean_absolute_percentage_error"):
            # smape = WatForeUtils.smape(y_true, y_pred)   # moved to adjusted_smape
            smape = WatForeUtils.adjusted_smape(y_true, y_pred)
            return smape
    except Exception as e:
        print('== Error in computing metrics: ', e)
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0080E'))

def get_scorer(scoring):
    """Get a scorer from string.
    Read more in the :ref:`User Guide <scoring_parameter>`.
    Parameters
    ----------
    scoring : str | callable
        scoring method as string. If callable it is returned as is.
        Supported {'neg_avg_mean_absolute_error', 'neg_avg_root_mean_squared_error', 'avg_r2', 'neg_avg_symmetric_mean_absolute_percentage_error'}
    Returns
    -------
    scorer : callable
        The scorer.
    """
    if scoring == "neg_avg_symmetric_mean_absolute_percentage_error":
        return make_scorer(neg_avg_symmetric_mean_absolute_percentage_error, greater_is_better=True)
    elif scoring == "avg_r2":
        return make_scorer(avg_r2, greater_is_better=True)
    elif scoring == "neg_avg_root_mean_squared_error":
        return make_scorer(neg_avg_root_mean_squared_error, greater_is_better=True)
    elif scoring == "neg_avg_mean_absolute_error":
        return make_scorer(neg_avg_mean_absolute_error, greater_is_better=True)
    else:
        raise Exception(Messages.get_message(scoring, message_id='AUTOAITSLIBS0078E'))