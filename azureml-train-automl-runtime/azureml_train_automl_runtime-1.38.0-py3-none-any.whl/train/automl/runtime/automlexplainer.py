# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functions for explaining automated ML models in Azure Machine Learning.

Included classes allow understanding of *feature importance* during model training. Classification and regression
models allow for different feature importance output. For an overview, see [Model interpretability in Azure Machine
Learning](https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability).

Feature importance is primarily used in the same sense as SHapley Additive exPlanations (SHAP). For more information
and links to papers with precise definitions, see [SHAP GitHub](https://github.com/slundberg/shap). For additional
background on feature importance, see [this paper about LIME](https://arxiv.org/abs/1602.04938), an explanation
technique. A different approach on feature importance can be found in [this
paper](http://people.dbmi.columbia.edu/noemie/papers/15kdd.pdf), with the same techniques used in the
[InterpretML package](https://github.com/interpretml/interpret).
"""
import logging
import numpy as np

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared import logging_utilities
from azureml._common.exceptions import AzureMLException
from azureml._restclient.exceptions import ServiceException
from azureml.automl.core.model_explanation import _convert_explanation, _get_valid_notebook_path_link
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExplainabilityPackageMissing
from azureml.automl.runtime.cpu_utilities import _get_num_physical_cpu_cores_model_explanations
from azureml.automl.runtime.training_utilities import _is_sparse_matrix_int_type, _upgrade_sparse_matrix_type
from azureml.train.automl import _logging  # type: ignore
from azureml.train.automl.exceptions import ConfigException, SystemException
from azureml.train.automl.runtime.automl_explain_utilities import _prepare_time_series_data_with_look_back_features
from .ensemble import Ensemble


logger = logging.getLogger(__name__)


def retrieve_model_explanation(child_run):
    """
    Retrieve the model explanation from the run history.

    Returns a tuple of the following values

    - shap_values - For regression models, this returns a matrix of feature importance values.
      For classification models, the dimension of this matrix is (# examples x # features).
    - expected_values - The expected value of the model applied to the set of initialization examples.
    - overall_summary - The model level feature importance values sorted in descending order.
    - overall_imp - The feature names sorted in the same order as in overall_summary or the indexes
      that would sort overall_summary.
    - per_class_summary - The class level feature importance values sorted in descending order when
      classification model is evaluated. Only available for the classification case.
    - per_class_imp - The feature names sorted in the same order as in per_class_summary or the indexes
      that would sort per_class_summary. Only available for the classification case.

    :param child_run: The run object corresponding to best pipeline.
    :type child_run: azureml.core.run.Run
    :return: tuple(shap_values, expected_values, overall_summary, overall_imp, per_class_summary and per_class_imp)
    :rtype: (list, list, list, list, list, list)
    """
    logging.warning("retrieve_model_explanation() will be deprecated. " +
                    "Please use the workflow described at the link " +
                    _get_valid_notebook_path_link() + " to compute explanations for AutoML models and consuming them.")
    try:
        from azureml.interpret import ExplanationClient

        client = ExplanationClient.from_run(child_run)
        explanation = client.download_model_explanation(raw=False)

        return _convert_explanation(explanation)
    except ImportError as e:
        raise ConfigException._with_error(AzureMLError.create(
            ExplainabilityPackageMissing, target="retrieve_model_explanation", missing_packages=e.name),
            inner_exception=e
        ) from e


def explain_model(fitted_model, X_train, X_test, best_run=None, features=None, y_train=None, **kwargs):
    """
    Explain the model with the specified X_train and X_test data.

    Returns a tuple of shap_values, expected_values, overall_summary, overall_imp, per_class_summary, and
    per_class_imp where

    - shap_values - For regression models, this returns a matrix of feature importance values.
      For classification models, the dimension of this matrix is (# examples x # features).
    - expected_values - The expected value of the model applied to the set of initialization examples.
    - overall_summary - The model level feature importance values sorted in descending order.
    - overall_imp - The feature names sorted in the same order as in overall_summary or the indexes
      that would sort overall_summary.
    - per_class_summary - The class level feature importance values sorted in descending order when
      classification model is evaluated. Only available for the classification case.
    - per_class_imp - The feature names sorted in the same order as in per_class_summary or the indexes
      that would sort per_class_summary. Only available for the classification case.

    :param fitted_model: The fitted automated ML model.
    :type fitted_model: sklearn.pipeline
    :param X_train: A matrix of feature vector examples for initializing the explainer.
    :type X_train: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    :param X_test: A matrix of feature vector examples on which to explain the model's output.
    :type X_test: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    :param y_train: Training labels for aiding time series explanations.
    :type y_train: pandas.DataFrame or numpy.ndarray
    :param best_run: The run object corresponding to best pipeline.
    :type best_run: azureml.core.run.Run
    :param features: A list of feature names.
    :type features: list[str]
    :param kwargs:
    :type kwargs: dict
    :return: The model's explanation.
    :rtype: (list, list, list, list, list, list)
    """
    msg = "explain_model() will be deprecated. Please use the workflow described at the link " + \
          _get_valid_notebook_path_link() + " to compute explanations for AutoML models."
    logging.warning(msg)
    logger.warning(msg)
    run_id = ""
    try:
        from interpret_community.mimic import MimicExplainer
        from interpret_community.mimic.models.lightgbm_model import LGBMExplainableModel
        from azureml.interpret._internal.explanation_client import ExplanationClient
        from azureml.automl.core.shared.constants import TimeSeriesInternal, Transformers

        if best_run is not None:
            run_id = best_run.id

        logger.info("[RunId:{}]Start explain model function.".format(run_id))
        # Transform the dataset for datatransformer and timeseries transformer only.
        # Also, we need to remove nans from the generations of the look-back features for all models,
        # since classical forecasting models are also explained by regression models.
        # Ensembling pipeline may group the miro pipelines into one step
        for name, transformer in fitted_model.steps[:-1]:
            if (transformer is not None) and \
                    (name == Transformers.X_TRANSFORMER or name == Transformers.TIMESERIES_TRANSFORMER):
                if name == Transformers.TIMESERIES_TRANSFORMER:
                    if y_train is not None:
                        X_train = transformer.transform(X_train, y_train)
                        y_train = X_train.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
                        X_train, y_train = _prepare_time_series_data_with_look_back_features(
                            timeseries_transformer=transformer,
                            algo_name=fitted_model.steps[-1][0],
                            X=X_train,
                            y=y_train
                        )
                        X_test = transformer.transform(X_test)
                        y_test_pseudo = np.zeros(X_test.shape[0])
                        X_test, y_test_pseudo = _prepare_time_series_data_with_look_back_features(
                            timeseries_transformer=transformer,
                            algo_name=fitted_model.steps[-1][0],
                            X=X_test,
                            y=y_test_pseudo
                        )
                    else:
                        raise ConfigException._with_error(
                            AzureMLError.create(
                                ArgumentBlankOrEmpty, target="y_train", argument_name="y_train"
                            )
                        )
                else:
                    X_train = transformer.transform(X_train)
                    X_test = transformer.transform(X_test)

                features = transformer.get_engineered_feature_names()

        # To explain the pipeline which should exclude datatransformer
        fitted_model = Ensemble._transform_single_fitted_pipeline(fitted_model)

        if _is_sparse_matrix_int_type(X_train):
            logger.info("Integer type detected for X_train, need to upgrade to float type")
        if _is_sparse_matrix_int_type(X_test):
            logger.info("Integer type detected for X_test, need to upgrade to float type")

        explainer_data_X_train = _upgrade_sparse_matrix_type(X_train)
        explainer_data_X_test = _upgrade_sparse_matrix_type(X_test)

        # Set the number of cores for LightGBM model
        explainable_model_args = {}
        explainable_model_args['n_jobs'] = _get_num_physical_cpu_cores_model_explanations()

        class_labels = kwargs.get('classes', None)
        explainer = MimicExplainer(
            fitted_model, explainer_data_X_train, LGBMExplainableModel, features=features, classes=class_labels,
            augment_data=False, explainable_model_args=explainable_model_args
        )

        include_local_importance = kwargs.get('include_local_importance', True)
        # Explain the model and save the explanation information to artifact
        explanation = explainer.explain_global(explainer_data_X_test, include_local=include_local_importance)

        if best_run is not None:
            client = ExplanationClient.from_run(best_run)
            topk = kwargs.get('top_k', 100)
            client.upload_model_explanation(explanation, top_k=topk)

        logger.info("[RunId:{}]End explain model function.".format(run_id))

        return _convert_explanation(explanation, include_local_importance=include_local_importance)
    except ImportError as import_error:
        logging_utilities.log_traceback(import_error, logger, is_critical=False)
        message = "[RunId:{}]Explain model function met import error.".format(run_id)
        logger.warning(message)
        raise ConfigException._with_error(AzureMLError.create(
            ExplainabilityPackageMissing, target="explain_model", missing_packages=import_error.name),
            inner_exception=import_error
        ) from import_error
    except (ServiceException, AzureMLException) as e:
        logging_utilities.log_traceback(e, logger, is_critical=False)
        message = "[RunId:{}]Explain model function met service error.".format(run_id)
        logger.warning(message)
        raise
    except Exception as e:
        logging_utilities.log_traceback(e, logger, is_critical=False)
        message = "[RunId:{}]Explain model function met some error.".format(run_id)
        logger.warning(message)
        raise SystemException.from_exception(e).with_generic_msg(message)
