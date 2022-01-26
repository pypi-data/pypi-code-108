import numpy as np
import pandas as pd
import math
import datetime
from sklearn.feature_selection import f_regression, mutual_info_regression
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from scipy import fft, arange, signal
from sklearn.utils.validation import column_or_1d
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from autoai_ts_libs.srom.joint_optimizers.auto.auto_regression import AutoRegression
from autoai_ts_libs.srom.estimators.regression.auto_ensemble_regressor import (
    EnsembleRegressor,
)
from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import xgb_dag, lgbm_dag
from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import (
    tiny_reg_dag,
    flat_reg_dag,
)
from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import (
    multi_output_flat_dag,
    multi_output_tiny_dag,
)
from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import (
    regression_chain_flat_dag,
    regression_chain_tiny_dag,
)
from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import (
    mimo_flat_dag,
    complete_mino_flat_dag,
)
from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import (
    xgboost_multi_dag,
    lgbm_multi_dag,
)
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from sklearn.base import BaseEstimator
from autoai_ts_libs.utils.messages.messages import Messages

MODEL_TYPES_SUPPORTED_FOR_DEEP_LEARNING = [KerasRegressor]
MODEL_TYPES_SUPPORTED_AS_ESTIMATOR = [KerasRegressor, BaseEstimator]


def check_model_type_is_dl(model):
    """
    check if model is deep learning
    """
    for i in MODEL_TYPES_SUPPORTED_FOR_DEEP_LEARNING:
        if isinstance(model, i):
            return True
    return False


def check_object_is_estimator(model):
    """
    check if model is estimator
    """
    for i in MODEL_TYPES_SUPPORTED_AS_ESTIMATOR:
        if isinstance(model, i):
            return True
    return False

def get_optimized_n_jobs(n_jobs=-1, no_outputs=1):
    """
    return optimized n_jobs based on n_jobs and no_outputs
    """
    if n_jobs == -1:
        n_jobs = cpu_count() -1
    if n_jobs < 1:
        n_jobs = 1
    return min(no_outputs, n_jobs)

def prepare_regressor(
    dag_granularity,
    total_execution_time,
    execution_time_per_pipeline,
    r_type,
    execution_platform="spark_node_random_search",
    n_leaders_for_ensemble=1,
    n_estimators_for_pred_interval=5,
    max_samples_for_pred_interval=1.0,
    ensemble_type="voting",
    n_jobs = -1
):
    """
    Builds a regressor object depending upon the dag_granularity and r_type.
    Parameters
    ----------
        dag_granularity : string (tiny, default, flat)
            granularity for execution
        total_execution_time : int
            Total execution time (minutes) for the auto Regression pipeline.
        execution_time_per_pipeline : int
            Total execution time (minutes) per pipeline.
        r_type :  string (AutoRegressor, AutoEnsemble)
            Type of regressor.
        execution_platform : string (spark_node_random_search)
            The platform on the which the algorithm is executed.
        n_leaders_for_ensemble : int
            Number of model for creating ensemble model.
        n_estimators_for_pred_interval : int
            Number of estimators to used.
        max_samples_for_pred_interval : float
            The number of samples to draw from X to train each base estimator.
        ensemble_type : string
            It can be voting or stacked.
        n_jobs : int
            n_jobs for parallel proccessing.
    Returns
    -------
        regressor
    """
    if n_jobs == 0 :
        n_jobs = 1

    options = {
        "total_execution_time": total_execution_time,
        "execution_time_per_pipeline": execution_time_per_pipeline,
        "execution_platform": execution_platform,
    }
    regressors = {"AutoRegressor": AutoRegression, "AutoEnsemble": EnsembleRegressor}

    if r_type not in regressors:
        raise Exception(Messages.get_message(r_type, message_id='AUTOAITSLIBS0036E'))

    if r_type in ["AutoEnsemble"]:
        options["n_leaders_for_ensemble"] = n_leaders_for_ensemble
        options["n_estimators_for_pred_interval"] = n_estimators_for_pred_interval
        options["max_samples_for_pred_interval"] = max_samples_for_pred_interval
        options["ensemble_type"] = ensemble_type

    if dag_granularity == "default":
        regressor = (r_type, regressors[r_type](**options))
    elif dag_granularity == "tiny":
        regressor = (r_type, regressors[r_type](stages=tiny_reg_dag, **options))
    elif dag_granularity == "flat":
        from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import get_flat_dag
        flat_reg_dag = get_flat_dag()
        regressor = (r_type, regressors[r_type](stages=flat_reg_dag, **options))
    elif dag_granularity == "multioutput_tiny":
        from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import get_multi_output_tiny_dag
        multi_output_tiny_dag = get_multi_output_tiny_dag(n_jobs)
        regressor = (
            r_type,
            regressors[r_type](stages=multi_output_tiny_dag, **options),
        )
    elif dag_granularity == "multioutput_flat":
        from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import get_multi_output_flat_dag
        multi_output_flat_dag = get_multi_output_flat_dag(n_jobs)
        regressor = (
            r_type,
            regressors[r_type](stages=multi_output_flat_dag, **options),
        )
    elif dag_granularity == "regression_chain_flat":
        regressor = (
            r_type,
            regressors[r_type](stages=regression_chain_flat_dag, **options),
        )
    elif dag_granularity == "regression_chain_tiny":
        regressor = (
            r_type,
            regressors[r_type](stages=regression_chain_tiny_dag, **options),
        )
    elif dag_granularity == "MIMO_flat":
        regressor = (r_type, regressors[r_type](stages=mimo_flat_dag, **options))
    elif dag_granularity == "MINO_complete_flat":
        regressor = (
            r_type,
            regressors[r_type](stages=complete_mino_flat_dag, **options),
        )
    elif dag_granularity == "multi_xgboost":
        from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import get_xgboost_multi_dag
        xgboost_multi_dag = get_xgboost_multi_dag(n_jobs)
        regressor = (r_type, regressors[r_type](stages=xgboost_multi_dag, **options))
    elif dag_granularity == "multi_lgbm":
        from autoai_ts_libs.srom.joint_optimizers.utils.regression_dag import get_lgbm_multi_dag
        lgbm_multi_dag = get_lgbm_multi_dag
        regressor = (r_type, regressors[r_type](stages=lgbm_multi_dag, **options))
    elif dag_granularity == "xgboost":
        regressor = (r_type, regressors[r_type](stages=xgb_dag, **options))
    elif dag_granularity == "lgbm":
        regressor = (r_type, regressors[r_type](stages=lgbm_dag, **options))
    else:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0037E'))
    return regressor
