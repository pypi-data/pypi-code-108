# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for downloading and loading automl models.
"""
import json
import logging
import os
import pickle
import tempfile
from typing import cast, Dict, Optional, Any, Tuple, List

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.package_utilities import _has_version_discrepancies
from azureml.automl.core.shared import constants as automl_shared_constants, logging_utilities
from azureml.automl.core.shared.exceptions import ConfigException, ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    DependencyWrongVersion, LoadModelDependencyMissing,
    ModelDownloadMissingDependency, RuntimeModuleDependencyMissing)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.core import Run
from . import constants


logger = logging.getLogger(__name__)


def _get_run_sdk_dependencies(
    run: Run,
    iteration: Optional[int] = None,
    check_versions: bool = True,
) -> Dict[str, str]:
    run_deps = dict()
    parent_run = run.parent

    if parent_run.__class__.__name__ == 'StepRun':
        try:
            # azureml.train.automl.client should not have a hard dependency
            # on azureml.pipeline.steps. Import the class here when required.
            from azureml.pipeline.steps.automl_step import AutoMLStepRun
            parent_run = AutoMLStepRun(parent_run)
        except ImportError as e:
            logger.warning("Package {0} not importable".format(str(e.name)))
            raise ConfigException._with_error(AzureMLError.create(
                ModelDownloadMissingDependency, target="download_automl_model", module="azureml-pipeline-steps"),
                inner_exception=e
            ) from e
    else:
        # Import AutoMLRun here to avoid circular dependency
        from .run import AutoMLRun
        if not isinstance(parent_run, AutoMLRun):
            parent_run = AutoMLRun(run.experiment, run.parent.id)

    run_deps = parent_run.get_run_sdk_dependencies(iteration=iteration, check_versions=False)
    return run_deps


def _download_automl_model(run: Run, model_name: str = constants.MODEL_PATH) -> Optional[Any]:
    with logging_utilities.log_activity(
        logger,
        activity_name=automl_shared_constants.TelemetryConstants.DOWNLOAD_MODEL
    ):
        # get the iteration of the best pipeline to check its package compatibility
        iteration_str = run.id.split('_')[-1]
        iteration = None if iteration_str == constants.BEST_RUN_ID_SUFFIX else int(iteration_str)

        # These dependencies are filtered by the azureml-* prefix at the time the run is created/running.
        azureml_run_deps = _get_run_sdk_dependencies(run, iteration=iteration, check_versions=False)

        if _has_version_discrepancies(azureml_run_deps, just_automl=True):
            logging.warn(
                "Please ensure the version of your local conda dependencies match "
                "the version on which your model was trained in order to properly retrieve your model."
            )

        _, suffix = os.path.splitext(model_name)
        model_path = 'model_{}.{}'.format(run.id, suffix)

        try:
            run.download_file(
                name=model_name, output_file_path=model_path, _validate_checksum=True)
        except Exception as e:
            raise ClientException(str(e)).with_generic_msg('Downloading AutoML model failed.') from None

        try:
            # Pass through any exceptions from loading the model.
            # Try is used here to ensure we can cleanup the side effect of model downlad.
            model = _load_automl_model(model_path, suffix)
            if model is None:
                # If we can retrieve the automl runtime version, we do so we can inform the user what to install.
                # Otherwise just tell them to install latest runtime version (this is not an expected scenario).
                automl_runtime_ver = azureml_run_deps.get("azureml-train-automl-runtime", None)
                msg = AutoMLErrorStrings.LOAD_MODEL_DEPENDENCY_MISSING.format(
                    module="azureml-train-automl-runtime",
                    ver="==" + automl_runtime_ver if automl_runtime_ver else None
                )
                logging.warn(msg)
                logger.warn(msg)
            return model
        except Exception as e:
            # ConfigExceptions already have the actions a user should take included
            # as part of the error. Only log the entire set of package mismatches in
            # cases where the error is unknown. In order to effectively do this, we retrieve
            # the file containing all dependencies for the run and compare them against the
            # current environment.
            # NOTE: This check is NOT a catch all. It will help users in cases where
            # the model is not serializable in the current environment, however it will
            # not help with cases where the model fails at runtime.
            if not isinstance(e, ConfigException):
                try:
                    with tempfile.NamedTemporaryFile() as fp:
                        run.download_file(automl_shared_constants.DEPENDENCIES_PATH, fp.name)
                        all_deps = json.load(fp)
                    _has_version_discrepancies(all_deps, just_automl=False)
                except Exception as e:
                    logging_utilities.log_traceback(e, logger)
            raise
        finally:
            try:
                if os.path.exists(model_path):
                    os.remove(model_path)
            except Exception:
                pass


def _load_automl_model(model_path: str, suffix: str = "pkl") -> Optional[Any]:
    """
    Load an automl model.

    This method should be used whenever unpickling an AutoML model.
    It should be used over pickle.load() in order to ensure a user
    can get a meaningful error message when package imcompatibilities
    arise.

    If the model can be unpickled in the current environment it is
    returned. If an exception is raised relating to
    azureml-train-automl-runtime, None is returned. This is due to
    legacy behavior. It is recommended callers of this function add
    a reasonable warning to the end user on what action to take in the
    case of runtime missing (install runtime, use model proxy, etc.).
    Otherwise the original exception will be raised.

    :param model_path: The path to the model on disk.
    :type model_path: str
    :return: The deserialized model.
    :raises: ConfigException if issues arise during model deserialization.
    """
    Contract.assert_value(
        model_path,
        "model_path",
        reference_code=ReferenceCodes._LOAD_MODEL_PATH_BAD_VALUE
    )

    Contract.assert_true(
        os.path.isfile(model_path),
        "The model path was either not found or is not a path to a file.",
        target="get_output",
        reference_code=ReferenceCodes._LOAD_MODEL_PATH_NOT_FILE_OR_NOT_FOUND,
        log_safe=True
    )

    # import xgboosterror to be used for error handling when local version is greater than
    # trained version. If xgboost is not installed we can safely cast this to NoneType.
    # We also set the xgboost version if present. In cases where we are unable to retrieve
    # the xgboost version, we expect an ImportError to be thrown rather than the other
    # handled exceptions (XGBoostError, AttributeError).
    xgb_ver = "notinstalled"
    try:
        from xgboost.core import XGBoostError
        import xgboost
        xgb_ver = xgboost.__version__
    except ImportError:
        XGBoostError = type(None)

    try:
        is_torch_model = (suffix == '.pt' or suffix == '.pth')
        import azureml.train.automl.runtime
        if not is_torch_model:
            with open(model_path, "rb") as model_file:
                fitted_model = pickle.load(model_file)  # type: Optional[Any]
                return fitted_model
        else:
            # Load the torch model with pytorch.
            import torch
            with open(model_path, 'rb') as fh:
                if torch.cuda.is_available():
                    logger.info("Using CUDA storage for loading torch model tensors.")
                    fitted_model = torch.load(fh, map_location=lambda storage, loc: storage.cuda())
                else:
                    logger.info("Using CPU storage for loading torch model tensors.")
                    fitted_model = torch.load(fh, map_location='cpu')
                return fitted_model

    except ImportError as e:
        logging_utilities.log_traceback(e, logger)
        if e.name == 'xgboost':
            # xgboost is not installed.
            raise ConfigException._with_error(
                AzureMLError.create(
                    LoadModelDependencyMissing,
                    target="get_output",
                    module="xgboost",
                    ver="=={}".format(automl_shared_constants.XGBOOST_SUPPORTED_VERSION),
                    reference_code=ReferenceCodes._MISSING_OPTIONAL_DEPENDENCY_XGBOOST
                ),
                inner_exception=e
            ) from e
        elif e.name == 'fbprophet':
            # fbprophet is not installed
            raise ConfigException._with_error(AzureMLError.create(
                LoadModelDependencyMissing, target="get_output", module="fbprophet", ver="==0.5"),
                inner_exception=e
            ) from e
        elif e.name == 'torch':
            # pytorch is not installed
            raise ConfigException._with_error(AzureMLError.create(
                LoadModelDependencyMissing, target="get_output", module="torch", ver=""),
                inner_exception=e
            ) from e
        elif e.name == 'pandas.core.internals.managers':
            try:
                import pandas as pd
                # pandas is installed in the environment but at an incompatible version
                error = AzureMLError.create(
                    DependencyWrongVersion,
                    target="get_output",
                    module="pandas",
                    ver=">=0.24,<1.0.0",
                    cur_version=pd.__version__,
                    reference_code=ReferenceCodes._INCOMPATIBLE_DEPENDENCY_PANDAS_VERSION
                )
            except Exception:
                # pandas is not installed
                error = AzureMLError.create(
                    LoadModelDependencyMissing, target="get_output", module="pandas", ver=">=0.24,<1.0.0",
                    reference_code=ReferenceCodes._MISSING_OPTIONAL_DEPENDENCY_PANDAS_VERSION)
            raise ConfigException(azureml_error=error, inner_exception=e) from e
        elif e.name == 'sklearn.preprocessing.imputation':
            try:
                import sklearn as skl
                # scikit-learn is installed in the environment but at an incompatible version
                error = AzureMLError.create(
                    DependencyWrongVersion,
                    target="get_output",
                    module="scikit-learn",
                    ver=">=0.19,<0.22",
                    cur_version=skl.__version__,
                    reference_code=ReferenceCodes._INCOMPATIBLE_DEPENDENCY_SCIKIT_VERSION
                )
            except Exception:
                # scikit-learn is not installed
                error = AzureMLError.create(
                    LoadModelDependencyMissing,
                    target="get_output",
                    module="scikit-learn",
                    ver=">=0.19,<0.22",
                    reference_code=ReferenceCodes._MISSING_OPTIONAL_DEPENDENCY_SCIKIT_VERSION
                )
            raise ConfigException(azureml_error=error, inner_exception=e) from e
        elif e.name not in ['runtime', 'azureml.train.automl.runtime']:
            # Check to see if importing azureml.train.automl.runtime specifically failed
            # If we do, current behavior returns None for the model, otherwise current behavior
            # raises the original exception. The handling above and below is for specific issues
            # which have been brought up from common customer issues.
            raise
        else:
            return None
    except Exception as e:
        # Catch all other unknown exceptions. We must treat XGBoostErrors as "unknown" becuase we cannot
        # explicitly except XGBoostErrors from the client (xgboost is not a requirement for client to run).
        logging_utilities.log_traceback(e, logger)
        if isinstance(e, XGBoostError):
            # We cannot guarantee XGBoost is installed so we cannot directly catch an XGBoostError.
            # Instead we must catch all extra errors and check if the error is of type XGBoostError (if
            # XGBoost is installed, otherwise the check will not take this path since the error cannot
            # be of type None). In this case, XGBoost is installed but at an incorrect version.
            raise ConfigException._with_error(
                AzureMLError.create(
                    DependencyWrongVersion,
                    target="get_output",
                    module="xgboost",
                    ver="=={}".format(automl_shared_constants.XGBOOST_SUPPORTED_VERSION),
                    cur_version=xgb_ver,
                    reference_code=ReferenceCodes._INCOMPATIBLE_DEPENDENCY_XGBOOST_VERSION
                ),
                inner_exception=e
            ) from e
        elif isinstance(e, AttributeError) and "XGBoostLabelEncoder" in str(e):
            # XGBoost on GPU is currently trained with a version different from cpu. We may need to warn
            # users to upgrade their version of XGBoost when they try to retrieve XGBoost models trained
            # on GPU. A common symptom of this incompatibility is an AttributeError from the XBGoostLabelEncoder.
            raise ConfigException._with_error(
                AzureMLError.create(
                    DependencyWrongVersion,
                    target="get_output",
                    module="xgboost",
                    ver="=={}".format(automl_shared_constants.XGBOOST_SUPPORTED_GPU_VERSION),
                    cur_version=xgb_ver,
                    reference_code=ReferenceCodes._INCOMPATIBLE_DEPENDENCY_XGBOOST_VERSION_GPU
                ),
                inner_exception=e
            ) from e
        # If we hit here, we are in new territory - we didn't run into an ImportError
        # and we didn't have a known exception type (XGBoostError).
        raise


def _download_automl_onnx_model(run: Run, model_name: str) -> Any:
    model_path = 'model_onnx_{}.onnx'.format(run.id)

    try:
        run.download_file(
            name=model_name, output_file_path=model_path, _validate_checksum=True)
    except Exception as e:
        raise ClientException(str(e)).with_generic_msg('Downloading AutoML ONNX model failed.') from None

    try:
        from azureml.automl.runtime.onnx_convert import OnnxConverter
        fitted_model = OnnxConverter.load_onnx_model(model_path)
    except ImportError:
        raise ConfigException._with_error(
            AzureMLError.create(
                RuntimeModuleDependencyMissing, target="onnx-model", module_name="azureml-train-automl-runtime")
        )
    finally:
        try:
            if os.path.exists(model_path):
                os.remove(model_path)
        except Exception:
            pass

    return fitted_model
