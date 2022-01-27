from collections import namedtuple
import numpy as np
from scipy import stats
from sklearn import metrics

ModelPredStats = namedtuple("ModelPredStats", ["r2", "r2_adj", "p_value", "mae", "rmse", "p_value_err_normal"])


def x_model_pred_stats(y_true, y_pred, y_alt='mean', k=None):
    """
    Calculates various statistics on model predictions, including:
        p_value: the p_value of the test that the absolute errors of the pred are less than the absolute errors of the alt
        p_value_err_normal: the p_value of the test that the errors are normally distributed
        r2_adj: adjusted r-squared (requires the k parameter to be set)

    Args:
        y_true: true values
        y_pred: predicted values
        y_alt: alternative (null) model, typically mean of train data
        k: number of variables in the model (for calculating r2_adj)

    Returns: ModelPredStats
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    if y_alt == 'mean':
        y_alt = y_true.mean()

    err_pred = np.abs(y_true - y_pred)
    err_alt = np.abs(y_true - y_alt)

    res = stats.ttest_rel(err_pred, err_alt, alternative='less')
    p_value = res.pvalue
    if p_value is np.nan:
        p_value = None

    errors = y_true - y_pred
    p_value_err_normal = None
    try:
        p_value_err_normal = stats.normaltest(errors).pvalue
    except ValueError:
        pass

    if p_value_err_normal is np.nan:
        p_value_err_normal = None

    r2 = metrics.r2_score(y_true, y_pred)
    n = len(y_true)
    r2_adj = None
    if k is not None and n - k - 1 > 0:
        r2_adj = 1 - ((1-r2)*(n-1))/(n-k-1)

    mae = np.mean(err_pred)
    rmse = metrics.mean_squared_error(y_true, y_pred, squared=False)
    res = ModelPredStats(r2=r2, r2_adj=r2_adj, p_value=p_value, mae=mae, rmse=rmse, p_value_err_normal=p_value_err_normal)
    return res
