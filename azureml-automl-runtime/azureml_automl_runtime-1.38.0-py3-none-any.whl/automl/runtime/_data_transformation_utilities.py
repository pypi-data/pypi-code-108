# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for data transformation."""
from typing import List, Union, Any, Optional, Dict, Mapping, Tuple, cast

import json
import logging
import numpy as np
import pandas as pd
import pickle
import scipy

from sklearn_pandas import DataFrameMapper

from .featurization import DataTransformer, data_transformer_utils, TransformerAndMapper
from .featurization._featurizer_container import FeaturizerContainer
from .featurization._unprocessed_featurizer import FeaturizerFactory
from .featurizer.transformer.featurization_utilities import get_transform_names, does_property_hold_for_featurizer
from azureml._common._error_definition import AzureMLError
from azureml._common.exceptions import AzureMLException
from azureml.automl.core.constants import FeatureType, FeaturizationRunConstants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ArtifactUploadFailed
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import CacheException, ClientException
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.runtime import frequency_fixer
from azureml.automl.runtime._engineered_feature_names import _GenerateEngineeredFeatureNames
from azureml.automl.runtime.distributed.utilities import get_unique_download_path
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.shared.types import CoreDataInputType, DataInputType
from azureml.core import Run
from azureml.exceptions import ServiceException as AzureMLServiceException, AzureMLAggregatedException
from azureml.automl.runtime.column_purpose_detection._time_series_column_helper import infer_objects_safe
from azureml.automl.runtime.column_purpose_detection.types import StatsAndColumnPurposeType
from azureml._restclient.models.featurization_config import FeaturizationConfig


logger = logging.getLogger(__name__)
_PICKLER = DefaultPickler()

_DUMMY_VALUES_FOR_TYPE = {
    "bytes": "example_value",
    "bool": False,
    "datetime": "2000-1-1",
    "float": 0.0,
    "int": 0,
    "object": "example_value",
    "str": "example_value",
    "timedelta": "1000"
}

_DUMMY_VALUES_FOR_FEATURE = {
    FeatureType.Numeric: _DUMMY_VALUES_FOR_TYPE["int"],
    FeatureType.DateTime: _DUMMY_VALUES_FOR_TYPE["datetime"]
}


def _upload_pickle(obj: Any, run_obj: Run, file_name: str) -> None:
    """
    Helper function for pickling and uploading object to storage with specified file name.

    :param obj: The object to be uploaded.
    :param run_obj: The run through which we upload the file.
    :param file_name: The name of the file to be created in storage.
    :return: None
    """
    _PICKLER.dump(obj, file_name)
    try:
        run_obj.upload_file(file_name, file_name)
    except AzureMLAggregatedException as error:
        if "Resource Conflict: ArtifactId" in error.message:
            logger.warning("Artifact upload failed with conflict. The file already exists")
        else:
            raise


def _download_pickle(file_name: str) -> Any:
    """
    Helper function for downloading file from storage.

    :param file_name: The name of the file to be downloaded.
    :return: The downloaded, unpickled object.
    """
    return _PICKLER.load(file_name)


def load_and_update_from_sweeping(data_transformer: DataTransformer,
                                  df: DataInputType) -> None:
    """
    Function called in the featurization run for updating the newly-instantiated data transformer
    with values from the setup iteration's data transformer that are necessary for full featurization.

    :param data_transformer: The data transformer to update.
    :param df: The input data used for recreating the column types mapping.
    :return: None.
    """

    run = Run.get_context()
    property_dict = run.get_properties()

    with logging_utilities.log_activity(logger=logger, activity_name="FeatureConfigDownload"):
        try:
            downloaded_path = get_unique_download_path(property_dict.get(FeaturizationRunConstants.CONFIG_PROP,
                                                       FeaturizationRunConstants.CONFIG_PATH))
            feature_config = _download_pickle(downloaded_path)
        except Exception as e:
            logging_utilities.log_traceback(
                exception=e,
                logger=logger,
                override_error_msg="Error when retrieving feature config from local node storage.")
            raise e

    data_transformer.transformer_and_mapper_list = feature_config

    with logging_utilities.log_activity(logger=logger, activity_name="EngineeredFeatureNamesDownload"):
        try:
            downloaded_path = get_unique_download_path(property_dict.get(FeaturizationRunConstants.NAMES_PROP,
                                                       FeaturizationRunConstants.NAMES_PATH))
            data_transformer._engineered_feature_names_class = \
                _download_pickle(downloaded_path)
        except Exception as e:
            logging_utilities.log_traceback(
                exception=e,
                logger=logger,
                override_error_msg="Error when retrieving feature names from local node storage.")
            raise e

    if data_transformer._columns_types_mapping is None:
        if isinstance(df, np.ndarray):
            df = pd.DataFrame(df)

        data_transformer._columns_types_mapping = data_transformer_utils.get_pandas_columns_types_mapping(df)

    data_transformer._feature_sweeped = True


def save_feature_config(feature_config: Union[List[TransformerAndMapper], DataFrameMapper]) -> None:
    """
    Logic for saving the transformer_and_mapper_list or mapper from the setup run's data transformer.

    :param feature_config: The feature config to be downloaded and used in the featurization run.
    :return: None.
    """
    run = Run.get_context()
    error = AzureMLError.create(ArtifactUploadFailed, target="feature_config")
    with logging_utilities.log_activity(logger=logger, activity_name="FeatureConfigUpload"):
        try:
            _upload_pickle(feature_config, run, FeaturizationRunConstants.CONFIG_PATH)
        except AzureMLServiceException:
            raise
        except AzureMLException as e:
            if hasattr(e, '_azureml_error') and e._azureml_error is None:
                e._azureml_error = error
            raise e


def save_engineered_feature_names(engineered_feature_names: _GenerateEngineeredFeatureNames) -> None:
    """
    Logic for saving the engineered feature names from the setup run's data transformer.

    :param engineered_feature_names: The feature names to be downloaded and used in the featurization run.
    :return: None.
    """
    run = Run.get_context()
    error = AzureMLError.create(ArtifactUploadFailed, target="feature_names")
    with logging_utilities.log_activity(logger=logger, activity_name="EngineeredFeatureNamesUpload"):
        try:
            _upload_pickle(engineered_feature_names, run, FeaturizationRunConstants.NAMES_PATH)
        except AzureMLServiceException:
            raise
        except AzureMLException as e:
            if hasattr(e, '_azureml_error') and e._azureml_error is None:
                e._azureml_error = error
            raise e


def pull_fitted_featurizers_from_cache(cache_store: Optional[CacheStore],
                                       featurizer_container: FeaturizerContainer) -> Mapping[int, Any]:
    """
    Pull any featurizers that were already fitted and cached in their own independent runs back
    into the DataTransformer. If missing from the cache, raise an exception.

    :param cache_store: The CacheStore.
    :param featurizer_container: Object containing featurizers and other relevant settings.
    :return: The featurizer index mapping that will be used to mutate the DataTransformer object.
    """
    cache_keys = [get_cache_key_from_index(featurizer.index) for featurizer
                  in featurizer_container if featurizer.is_cached]
    if cache_store is None:
        if len(cache_keys) > 0:
            raise ClientException("Cannot pull cached featurizers from null cache.", has_pii=False)
        return {}

    fitted_featurizers = cache_store.get(cache_keys)
    featurizer_index_mapping = {}
    for featurizer_cache_key in cache_keys:
        index = get_data_transformer_index_from_cache_key_string(featurizer_cache_key)
        if fitted_featurizers[featurizer_cache_key] is None:  # cache lookup failed and a default value was returned
            raise CacheException("Cached entry for featurizer index {} unexpectedly missing.".format(index),
                                 has_pii=False)
        featurizer_index_mapping[index] = fitted_featurizers[featurizer_cache_key]
    return featurizer_index_mapping


def get_data_transformer_index_from_cache_key_string(key_name: str) -> int:
    """
    Given the key string used to store a fitted featurizer in the cache, extract the index.

    :param key_name: The cache key string.
    :return: The index.
    """
    return int(key_name.split('_')[-1])


def get_cache_key_from_index(index: int) -> str:
    """
    Given a featurizer's index in the DataTransformer featurizer collection, generate the cache key.

    :param index: The index.
    :return: The cache key string.
    """
    return FeaturizationRunConstants.FEATURIZER_CACHE_PREFIX + str(index)


def count_nans_in_data(data: CoreDataInputType) -> int:
    """
    Count number of NaNs in the given data

    :param data: np.ndarray, pd.DataFrame, or scipy.sparse.spmatrix
    :return:
    """
    if data is None:
        return 0

    if isinstance(data, pd.DataFrame):
        return int(data.isna().sum().sum())

    if isinstance(data, np.ndarray):
        return int(pd.isna(data).sum().sum())

    return 0


def should_convert_data_to_sparse(data: CoreDataInputType, count_nans: Optional[int] = None) -> bool:
    """
    Check if input data needs to be converted into sparse matrix
    If already scipy.sparse.spmatrix, we don't need to convert.
    Else, check if data contains 50 percent or more NaNs.

    There are some models that take in sparse matrix but not NaNs (fails on assert_all_finite validation).
    In order to avoid this failure, we need to convert the data into sparse matrix.

    :param data: np.ndarray, pd.DataFrame, or scipy.sparse.spmatrix
    :param count_nans: count of nans in data
    :return:
    """
    if data is None:
        return False

    limit = int(data.size * 0.5)

    if count_nans is None:
        return count_nans_in_data(data) >= limit

    return count_nans >= limit


def convert_data_to_sparse(data: Optional[CoreDataInputType]) -> Optional[CoreDataInputType]:
    """
    Convert data into sparse matrix.

    :param data: np.ndarray, pd.DataFrame, or scipy.sparse.spmatrix
    :return: sparse matrix if converted, otherwise original data
    """
    if data is None or scipy.sparse.issparse(data):
        return data

    try:
        # Convert data to sparse matrix
        if isinstance(data, pd.DataFrame):
            csrmatrix = scipy.sparse.csr_matrix(data.values)
        else:
            csrmatrix = scipy.sparse.csr_matrix(data)

        # At this point, csrmatrix still contains np.nan, these need to be converted to appropriate numbers
        csrmatrix.data = np.nan_to_num(csrmatrix.data)
        # Afterwards, eliminate those nans explicitly converted to zeros so that it is not used for training
        csrmatrix.eliminate_zeros()

        logger.info("Converting data to sparse matrix succeeded.")
        return csrmatrix
    except Exception:
        logger.warning("Converting data to sparse matrix failed. Proceeding with original data.")
        return data


def _add_raw_column_names_to_X(X: DataInputType, x_raw_column_names: Optional[np.ndarray] = None,
                               time_column_name: Optional[str] = None) -> pd.DataFrame:
    """
    Add raw column names to X.

    :param x_raw_column_names: List of raw column names
    :param X: dataframe / array
    :raise ValueError if number of raw column names is not same as the number of columns in X
    :return: Dataframe with column names
    """
    # If X is already a DataFrame, then return X. Assumption here is that raw column names
    # are already present in the data frame header. The passed x_raw_column_names are not needed.
    if isinstance(X, pd.DataFrame):
        X = infer_objects_safe(X)
        if time_column_name is not None:
            try:
                X = frequency_fixer.convert_to_datetime(X, time_column_name)
            except Exception:
                pass
        return X

    # If x_raw_column_names is passed, check whether it is valid
    if x_raw_column_names is not None:
        # Combine the raw feature names with X
        number_of_columns = 1 if len(X.shape) == 1 else X.shape[1]
        Contract.assert_true(
            x_raw_column_names.shape[0] == number_of_columns,
            "Number of raw column names {} and number of columns in input data {} do not match".format(
                x_raw_column_names.shape[0], number_of_columns)
        )

    if not scipy.sparse.issparse(X):
        X_with_raw_columns = pd.DataFrame(
            data=X, columns=x_raw_column_names.tolist() if x_raw_column_names is not None else None)
        X_with_raw_columns = infer_objects_safe(X_with_raw_columns)
        # Do our best to convert time_column_name to datetime.
        if time_column_name is not None:
            try:
                X_with_raw_columns = frequency_fixer.convert_to_datetime(X_with_raw_columns, time_column_name)
            except Exception:
                pass
        return X_with_raw_columns
    else:
        # TODO: SparseDataFrame is deprecated, use regular DataFrame whose columns are SparseArrays
        return pd.SparseDataFrame(
            data=X, columns=x_raw_column_names.tolist() if x_raw_column_names is not None else None)


def _get_dummy_value_by_purpose_or_dtype(purpose: Optional[FeatureType] = None,
                                         npdtype: Optional[np.dtype] = None) -> Any:
    """
    Get dummy values by either purpose or dtype of the column. If dtype is provided, it will get preference
    over purpose since dtypes are more accurate. If dtype is not provided, dummy value is picked based on
    the purpose.

    :param purpose: The FeatureType of the column
    :param npdtype: The dtype of the column
    :return: The dummy value
    """
    if npdtype:
        # we know the dtype because it was pandas dataframe
        for dtype_substring in _DUMMY_VALUES_FOR_TYPE.keys():
            if dtype_substring in npdtype.name:
                return _DUMMY_VALUES_FOR_TYPE[dtype_substring]

    if purpose:
        # if the user passed a numpy array we rely on the column purpose.
        return _DUMMY_VALUES_FOR_FEATURE.get(str(purpose), _DUMMY_VALUES_FOR_TYPE['str'])

    # If neither the dtype nor column purpose is known, it means featurization was turned off and
    # the user passed a numpy array or a sparse matrix. We can safely return a numeric value.
    return _DUMMY_VALUES_FOR_TYPE['int']


def get_data_snapshot(data: pd.DataFrame) -> str:
    """
    Get the snapshot of the data.

    :param data: The data frame to be used as a template.
    :return: The data snapshot string.
    """
    first_row = data.head(1)
    column_names_and_types = data.dtypes.to_dict()
    df_str = _get_data_snapshot_helper(
        first_row,
        column_names_and_types=column_names_and_types,
        column_purposes=None)
    return 'pd.DataFrame(' + df_str + ')'


def _get_data_snapshot_helper(data: Union[pd.DataFrame, pd.Series],
                              column_names_and_types: Optional[Dict[str, np.dtype]] = None,
                              column_purposes: Optional[List[StatsAndColumnPurposeType]] = None) -> str:
    Contract.assert_type(data, "data", (pd.DataFrame, pd.Series))
    if isinstance(data, pd.DataFrame):
        Contract.assert_value(column_names_and_types, "column_names_and_types")
        col_str_list = []
        column_names_and_types = cast(Dict[str, np.dtype], column_names_and_types)
        for col in column_names_and_types.keys():
            dtype = column_names_and_types[col]
            col_val = _get_dummy_value_by_purpose_or_dtype(npdtype=dtype)
            col_val = json.dumps([col_val]) if isinstance(col_val, str) else [col_val]
            col_str = "{0}: pd.Series({1}, dtype={2})".format(
                json.dumps(col), col_val, json.dumps(str(dtype)))
            col_str_list.append(col_str)
        snapshot_str = "{" + ", ".join(col_str_list) + "}"
    else:
        # data is of type pd.Series
        if not column_purposes:
            # if column_purposes is not set, featurization was turned off
            # construct the column purpose array and set the purpose and raw_stats set to None
            column_purposes = [(None, None, col) for col in range(len(data))]  # type:ignore
        dummy_data = pd.Series([_get_dummy_value_by_purpose_or_dtype(purpose=purpose)  # type:ignore
                                for rawstats, purpose, col in column_purposes])
        snapshot_json_str = dummy_data.to_json(orient='values', date_format='iso')
        snapshot_str = str(json.loads(snapshot_json_str))
    return snapshot_str


class FeaturizationJsonParser:
    """
    Class for constructing and deconstructing the featurization JSON. Builds and saves it in the setup run for
    JOS to interpret, and processes the returned JSON from JOS in the featurization run.

    Example JSON:
    {
        "featurizers": [
            {
                "index": 0,
                "transformers": [
                    "StringCastTransformer",
                    "TfidfVectorizer"
                ]
            },
            {
                "index": 1,
                "transformers": [
                    "StringCastTransformer",
                    "TfidfVectorizer"
                ]
            },
            {
                "index": 2,
                "transformers": [
                    "StringCastTransformer",
                    "TfidfVectorizer",
                    "PretrainedTextDNNTransformer"
                ],
                "is_distributable": True,
                "is_separable": True
            }
        ]
    }
    """
    @staticmethod
    def _build_jsonifiable_featurization_props(feature_config: Union[List[TransformerAndMapper], DataFrameMapper]) \
            -> Dict[str, Union[List[Dict[str, Any]], bool]]:
        """
        Function encapsulating the JSON construction logic. Given the feature config, extracts the
        transformer names for each featurizer, notes that featurizer's index in the config, and
        associates any necessary flags (e.g. distributed) with the entry.

        :param feature_config: The feature_config generated in the setup run's data transformer.
        :return: A jsonifiable featurizer dict.
        """
        if isinstance(feature_config, DataFrameMapper):
            featurizers = [feature_config.features[i][1] for i in range(len(feature_config.features))]
        else:
            featurizers = [feature_config[i].transformers for i in range(len(feature_config))]

        featurizer_properties_list = []  # type: List[Dict[str, Any]]
        for index, featurizer in enumerate(featurizers):
            featurizer_properties_list.append({
                FeaturizationRunConstants.INDEX_KEY: index,
                FeaturizationRunConstants.TRANSFORMERS_KEY: get_transform_names(featurizer),
                FeaturizationRunConstants.IS_DISTRIBUTABLE:
                    does_property_hold_for_featurizer(featurizer, FeaturizationRunConstants.IS_DISTRIBUTABLE),
                FeaturizationRunConstants.IS_SEPARABLE:
                    does_property_hold_for_featurizer(featurizer, FeaturizationRunConstants.IS_SEPARABLE)
            })
        return {FeaturizationRunConstants.FEATURIZERS_KEY: featurizer_properties_list}

    @staticmethod
    def save_featurization_json(featurization_props: Dict[str, Union[List[Dict[str, Any]], bool]]) -> None:
        """
        Builds featurization json and saves it to the run's artifact store.

        :param featurization_props: The featurization properties distilled from the feature_config
        to be json serialized.
        :return: None.
        """
        run = Run.get_context()
        with logging_utilities.log_activity(logger=logger, activity_name="FeaturizationJsonUpload"):
            with open(FeaturizationRunConstants.FEATURIZATION_JSON_PATH, 'w') as file_obj:
                json.dump(featurization_props, file_obj)
            run.upload_file(FeaturizationRunConstants.FEATURIZATION_JSON_PATH,
                            FeaturizationRunConstants.FEATURIZATION_JSON_PATH)

    @staticmethod
    def parse_featurizer_container(json_props: str,
                                   is_onnx_compatible: bool = False) -> "FeaturizerContainer":
        """
        Given the fragment of the featurization JSON string corresponding to to the featurizer list,
        return the corresponding featurizer list object with the correct properties.

        :param json_props: The json fragment, containing the properties for the featurizers and featurizer list.
        :param is_onnx_compatible: Boolean flag for whether onnx is enabled or not.
        :return: The featurizer list object.
        """
        try:
            featurizer_container_properties = json.loads(json_props)
            list_of_featurizers = \
                [FeaturizerFactory.get_featurizer(featurizer_props, is_onnx_compatible=is_onnx_compatible)
                 for featurizer_props in featurizer_container_properties.pop(
                    FeaturizationRunConstants.FEATURIZERS_KEY)]
            return FeaturizerContainer(featurizer_list=list_of_featurizers, **featurizer_container_properties)
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            logger.exception("Malformed JSON provided to independent featurizer run.")
            logging_utilities.log_traceback(e, logger)
            raise
