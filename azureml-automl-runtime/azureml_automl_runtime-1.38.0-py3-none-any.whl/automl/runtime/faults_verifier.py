# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for the Data faults and misconfigurations for AutoML."""
from typing import Dict, List, Optional, Any, Set, Union
from collections import OrderedDict
import json
import logging
import os
import pkg_resources

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.constants import AutoMLJson
from azureml.automl.core.shared.types import GrainType
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.automl_run_context import AutoMLAbstractRunContext
from azureml.automl.runtime.column_purpose_detection.types import StatsAndColumnPurposeType
from azureml.automl.core.constants import FeatureType as _FeatureType
from azureml.automl.core.constants import SupportedTransformers as _SupportedTransformers
from azureml.automl.core.constants import TransformerParams as _TransformerParams
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.stats_computation.raw_stats import RawFeatureStats

from azureml.automl.runtime.featurization.data_transformer import DataTransformer


logger = logging.getLogger(__name__)


class VerifierResults:
    PASSED = "passed"
    ALERTED = "alerted"
    FIXED = "fixed"
    DONE = "done"
    STATUS = {PASSED, ALERTED, FIXED, DONE}


class VerifiedFaultsTypes:
    CLASS_BALANCING = "_class_balancing"
    TRAIN_TEST_SPLIT = "_train_test_split"
    MISSING_VALUE_IMPUTATION = "_missing_value"
    DETECT_HIGH_CARDINAL_FEATURES = "_detect_high_cardinal_feature"
    CROSS_VALIDATION = "_cross_validation"
    ROLLING_WINDOW_FEATURES = "_rolling_window_features"
    LAGS_FEATURE = "_lags_features"
    LOOKBACK_FEATURES = "_lookback_features"
    TIMESERIES_REGULARITY = "_timeseries_regularity"
    TIMESERIES_SHORT_SERIES_HANDLING = "_timeseries_short_series_handling"
    TIMESERIES_AGGREGATION = "_timeseries_aggregation"
    TIMESERIES_ID_DETECTION_UTILITIES = "_timeseries_id_detection_utilities"


class ValidParameterKeys:
    COLUMN_NAME = "column_name"
    MISSING_VALUES = "missing_values"
    IMPUTATION_TYPE = "imputation_type"
    DATASET = "dataset"
    ROW_COUNTS = "row_counts"
    PERCENTAGE = "percentage"
    NUMBER_OF_FOLDS = "number_of_folds"
    CONTENT_TYPE = "content_type"
    SIZE_OF_SMALLEST_CLASS = "size_of_smallest_class"
    NAME_OF_SMALLEST_CLASS = "name_of_smallest_class"
    NUM_OF_SAMPLES = "num_of_samples"
    NUM_OF_MISSING_VALUES = "missing_value_count"
    SERIES_DROPPED = "series_dropped"
    SERIES_PADDED = "series_padded"
    SERIES_DROPPED_NAMES = "series_dropped_names"
    SERIES_PADDED_NAMES = "series_padded_names"
    SERIES_FREQ = "series_freq"
    TIME_SERIES_AGG_FUN = "aggregation_function"
    NUM_OF_DUPLICATE_TIME_INDEX = "number_of_duplicate_time_index"
    DETECTED_TIME_SERIES_ID_COLUMN_NAMES = "detected_time_series_id_column_names"


class ValidParameterValues:
    MEAN = "mean"
    MODE = "mode"
    TRAIN = "train"
    TEST = "test"
    CATEGORICALHASH = "categorical_hash"
    TEXT = "text"
    HASHES = "hashes"


class VerifiedFault:
    def __init__(self,
                 type_name: str,
                 result: str,
                 parameters: Optional[List[Dict[str, Any]]],
                 is_child_run_specific: Optional[bool] = False):
        self.type = type_name
        self.result = result
        self.is_child_run_specific = is_child_run_specific
        if parameters is None:
            self.parameters = []   # type: List[Any]
        else:
            self.parameters = parameters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "result": self.result,
            "parameters": self.parameters
        }


class VerifiedResult:
    def __init__(self,
                 fault: VerifiedFault,
                 description: Dict[str, Any]):

        self.type = fault.type
        self.result = fault.result
        self.parameters = fault.parameters

        self.fr_type = description["name"]
        self.fr_result = description["states"][self.result]
        self.fr_learn_more = description["learn_more"]
        self.fr_param_preface = description["parameter_preface"]
        self.fr_parameters = []     # type: List[Dict[Any, str]]

        for param in fault.parameters:
            temp_dict = {}
            for each in param.keys():
                temp_dict[description["parameters"][each]["name"]] = param[each]
            self.fr_parameters.append(temp_dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "result": self.result,
            "parameters": self.parameters,
            "friendly_type": self.fr_type,
            "friendly_result": self.fr_result,
            "friendly_parameters": self.fr_parameters,
            "friendly_learn_more": self.fr_learn_more,
            "friendly_parameter_preface": self.fr_param_preface
        }


class VerifierManager:
    PACKAGE_NAME = 'azureml.automl.runtime'
    REFERENCE_FILE_PATH = pkg_resources.resource_filename(PACKAGE_NAME, 'faults_verifier_message.json')

    def __init__(self):
        self.data_faults_dict = OrderedDict()   # type: Dict[str, VerifiedFault]
        self.ret_dict = {}           # type: Dict[str, Any]

    @property
    def data_faults_names(self) -> List[str]:
        return list(self.data_faults_dict.keys())

    def has_fault_member(self, fault_name: str) -> bool:
        return fault_name in self.data_faults_dict.keys()

    def add_data_fault(self,
                       fault_name: str,
                       result: str,
                       parameters: Optional[List[Dict[str, Any]]] = None,
                       is_child_run_specific: Optional[bool] = False) -> None:
        """
        Add fault to faults dictionary.

        data_faults_dict contains list of data faults and its verification results.
        Refer to VerifiedFaultsTypes for possible data faults that AutoML verifies.
        :param fault_name: name of the data fault
        :param result: result of the fault verification
        :param parameters: additional parameters to display with fault
        :param is_child_run_specific: if this fault is specific to a child run
        :return:
        """
        fault = VerifiedFault(fault_name, result, parameters, is_child_run_specific)
        if self.has_fault_member(fault_name):
            Contract.assert_true(
                self.data_faults_dict[fault_name].to_dict() == fault.to_dict(),
                message="fault ({}) already captured in data_faults_dict ({}), but with different results".format(
                    fault_name, list(self.data_faults_dict.keys())),
                target="data_fault",
                reference_code=ReferenceCodes._FAULT_VERIFIER_CONFLICT, log_safe=True
            )
            logger.info("fault ({}) already captured in data_faults_dict ({}), skipping fault addition".format(
                fault_name, list(self.data_faults_dict.keys())))
        else:
            self.data_faults_dict[fault_name] = fault

    def change_data_fault_result(
            self,
            fault_name: str,
            to_result: str
    ) -> None:
        """
        Change the status of one specific data faults. Will raise if the fault does not exists.

        :param fault_name: The name of the fault.
        :param to_result: The new status.
        """
        Contract.assert_true(
            self.has_fault_member(fault_name),
            message="fault_name ({}) does not exist in data_faults_dict. Existing keys: ({})".format(
                fault_name, list(self.data_faults_dict.keys())),
            target="data_fault",
            reference_code=ReferenceCodes._FAULT_VERIFIER_NOT_EXIST, log_safe=True
        )
        self.data_faults_dict[fault_name].result = to_result

    def add_data_fault_parameter(self, fault_name: str, parameters: Dict[str, str]) -> None:
        self.data_faults_dict[fault_name].parameters.append(parameters)

    def get_elaborate_dicts(self, friendly_desc: Dict[str, Any]) -> List[Any]:

        dict_list = []

        for fault_name in self.data_faults_dict.keys():
            fault = self.data_faults_dict[fault_name]
            res_obj = VerifiedResult(fault, friendly_desc["types"][fault.type])
            dict_list.append(res_obj.to_dict())

        return dict_list

    def write_result_file(self, run_context: AutoMLAbstractRunContext,
                          remote_path: str = '', working_directory: Optional[str] = None) -> None:
        try:
            with open(self.REFERENCE_FILE_PATH, 'r') as f:
                friendly_desc = json.load(f)

            data_faults = self.get_elaborate_dicts(friendly_desc)

            self.ret_dict = {"schema_type": AutoMLJson.SCHEMA_TYPE_FAULT_VERIFIER,
                             "schema_version": friendly_desc['version'],
                             "faults": data_faults}

            ret_str = json.dumps(self.ret_dict)

            with run_context.get_run():
                try:
                    file_path = os.path.join(remote_path, constants.VERIFIER_RESULTS_PATH)
                    run_context.save_str_output(
                        ret_str, file_path, overwrite_mode=True, working_directory=working_directory)
                except Exception:
                    logger.warning("Failed uploading version files to artifact services.")

        except FileNotFoundError:
            logger.debug("Reference file, `faults_verifier_message.json` does not exist.")

    def update_data_verifier_for_cv(self, number_of_folds: int) -> None:
        """
        Update VerifierManager object data fault with number of folds in Cross Validation.

        :param number_of_folds: Number of folds in cross validation.
        :return: None
        """
        self.add_data_fault(
            VerifiedFaultsTypes.CROSS_VALIDATION,
            result=VerifierResults.DONE,
            parameters=[{ValidParameterKeys.NUMBER_OF_FOLDS: str(number_of_folds)}]
        )

    def update_data_verifier_for_train_test_validation(self, train_row_count: int, test_row_count: int) -> None:
        """
        Update VerifierManager object data faults with the train/test sample ratio.

        :param train_row_count: Sample count in training set.
        :param test_row_count: Sample count in verification set.
        :return: None
        """
        self.add_data_fault(
            VerifiedFaultsTypes.TRAIN_TEST_SPLIT,
            result=VerifierResults.DONE,
            parameters=[
                {
                    ValidParameterKeys.DATASET: ValidParameterValues.TRAIN,
                    ValidParameterKeys.ROW_COUNTS: str(train_row_count),
                    ValidParameterKeys.PERCENTAGE: str(100. * train_row_count / (train_row_count + test_row_count))
                },
                {
                    ValidParameterKeys.DATASET: ValidParameterValues.TEST,
                    ValidParameterKeys.ROW_COUNTS: str(test_row_count),
                    ValidParameterKeys.PERCENTAGE: str(100. * test_row_count / (train_row_count + test_row_count))
                }
            ]
        )

    def update_data_verifier_for_missing_values(
            self,
            data_transformer: Optional[DataTransformer] = None,
            verifier_result: Optional[str] = None
    ) -> None:
        """
        Detect missing value imputation in DataTransformer and
        update missing values strategy of VerifierManager object.

        :param data_transformer: DataTransformer object.
        :param verifier_result: result for missing value verification
        and is handled by being converted into sparse matrix
        :return: None
        """
        if verifier_result:
            self.add_data_fault(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, verifier_result)
            return

        if data_transformer is None or data_transformer.stats_and_column_purposes is None or \
                not data_transformer.transformer_and_mapper_list:
            return

        # Go through each column and see if missing value is detected
        for purpose in data_transformer.stats_and_column_purposes:
            self._update_data_verifier_for_missing_value(purpose)

        if self.has_fault_member(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION):
            column_fault_verifier_mapping = {
                p[ValidParameterKeys.COLUMN_NAME]: p
                for p in self.data_faults_dict[VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION].parameters
            }
        else:
            # No missing value is detected, PASSED the fault test
            self.add_data_fault(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, VerifierResults.PASSED)
            return

        for transformer_mapper in data_transformer.transformer_and_mapper_list:
            # Add imputation strategy info for the columns with missing value imputation
            for f in transformer_mapper.mapper.features:
                col_name = str(_get_columnName(f))
                if col_name in column_fault_verifier_mapping.keys() and _is_imputer(f[1]):
                    column_fault_verifier_mapping[col_name][ValidParameterKeys.IMPUTATION_TYPE] = f[1][0].strategy

    def update_data_verifier_for_high_cardinal_features(
            self, stats_and_column_purpose: Optional[List[StatsAndColumnPurposeType]]
    ) -> None:
        """
        Detect high cardinality features from DataTransformer and update VerifierManager object with fault.

        :param stats_and_column_purpose: Statistics and other info about columns from a data transformer.
        :return: None
        """
        if stats_and_column_purpose is None:
            stats_and_column_purpose = []

        for col in stats_and_column_purpose:
            column_purpose = col[1]
            if column_purpose == _FeatureType.Hashes:
                if not self.has_fault_member(VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES):
                    self.add_data_fault(
                        VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES, VerifierResults.DONE
                    )
                self.add_data_fault_parameter(
                    VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES, {
                        ValidParameterKeys.COLUMN_NAME: str(col[2]),
                        ValidParameterKeys.CONTENT_TYPE: ValidParameterValues.HASHES
                    }
                )

        if not self.has_fault_member(VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES):
            self.add_data_fault(VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES, VerifierResults.PASSED)

    def update_data_verifier_for_class_balancing_validation(self, enable_class_balancing: bool,
                                                            class_balancing_fixed: bool,
                                                            size_of_smallest_class: int,
                                                            name_of_smallest_class: str, num_of_samples: int) -> None:
        """
        Detect class imbalance and update VerifierManager object with fault.

        :param enable_class_balancing: Boolean shows whether resampling happens or not
        :param min_size_of_class: number of samples in the smallest class
        :return: None
        """
        if enable_class_balancing:
            class_balancing_params = [{ValidParameterKeys.SIZE_OF_SMALLEST_CLASS: str(size_of_smallest_class),
                                       ValidParameterKeys.NAME_OF_SMALLEST_CLASS: str(name_of_smallest_class),
                                       ValidParameterKeys.NUM_OF_SAMPLES: str(num_of_samples)}]
            # if class balancing has been applied, send the Done/Fixed message
            result = VerifierResults.DONE if class_balancing_fixed else VerifierResults.ALERTED
            # if a fault value already exists for fault type class balancing, then overwrite it
            if self.has_fault_member(VerifiedFaultsTypes.CLASS_BALANCING):
                self.change_data_fault_result(
                    VerifiedFaultsTypes.CLASS_BALANCING,
                    to_result=result)
            # if no member exists for fault type class balancing, then add it
            else:
                self.add_data_fault(VerifiedFaultsTypes.CLASS_BALANCING,
                                    result=result,
                                    parameters=class_balancing_params)
        else:
            self.add_data_fault(VerifiedFaultsTypes.CLASS_BALANCING, VerifierResults.PASSED)

    def _update_data_verifier_for_missing_value(
            self,
            purpose: StatsAndColumnPurposeType
    ) -> None:
        """
        Detect missing value data and update missing values of VerifierManager object.

        :param purpose: Column stats and names.
        :return: None
        """
        raw_data_stats, feature_type, col_name = purpose[0], purpose[1], purpose[2]
        if raw_data_stats.num_na > 0 and feature_type not in _FeatureType.DROP_SET and \
                feature_type != _FeatureType.CategoricalHash and feature_type != _FeatureType.Text:
            if not self.has_fault_member(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION):
                self.add_data_fault(
                    VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, VerifierResults.DONE)
            self.add_data_fault_parameter(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, {
                ValidParameterKeys.COLUMN_NAME: str(col_name),
                ValidParameterKeys.NUM_OF_MISSING_VALUES: str(raw_data_stats.num_na)
            })

    def update_data_verifier_lookback_feature(self,
                                              lags: bool,
                                              rw: bool,
                                              passed: bool) -> None:
        """
        Detect if the lookback features were removed due to memory limitations.

        :param lags: If true the lag features were desired.
        :param rw: If true the rolling window features were desired.
        :param passed:
        :return: None
        """
        # The lags and rolling windows are all or nothing, if there is a
        # threat of memory error, they are removed together.
        result = VerifierResults.PASSED if passed else VerifierResults.DONE

        if lags and rw:
            self.add_data_fault(VerifiedFaultsTypes.LOOKBACK_FEATURES, result)
        elif lags:
            self.add_data_fault(VerifiedFaultsTypes.LAGS_FEATURE, result)
        elif rw:
            self.add_data_fault(VerifiedFaultsTypes.ROLLING_WINDOW_FEATURES, result)
        else:
            # We should not add any guard rails if there is no lookback features.
            pass

    def update_data_verifier_frequency_inference(self, inference_failed: bool, data_corrected: bool) -> None:
        """
        Detect if the frequency of data was inferred and if the data were corrected according to it.

        :param inference_failed: If True no guard rails needs to be printed.
        :param data_corrected: If True the data were corrected according to detected frequency.
        """
        if not inference_failed:
            result = VerifierResults.DONE if data_corrected else VerifierResults.PASSED
            self.add_data_fault(VerifiedFaultsTypes.TIMESERIES_REGULARITY, result)

    def update_data_verifier_aggregation(self, data_corrected: bool,
                                         aggregation_function: str,
                                         freqstr: str) -> None:
        """
        Add the data aggregation guard rail.

        :param data_corrected: The flag, showing, if data were corrected.
        :param aggregation_function: The function, used for aggregation.
        :param freqstr: The forecast frequency used to aggregate the time series.
        """
        if data_corrected:
            self.add_data_fault(VerifiedFaultsTypes.TIMESERIES_AGGREGATION, VerifierResults.FIXED)
            self.add_data_fault_parameter(
                VerifiedFaultsTypes.TIMESERIES_AGGREGATION,
                {ValidParameterKeys.SERIES_FREQ: freqstr,
                 ValidParameterKeys.TIME_SERIES_AGG_FUN: aggregation_function})
        else:
            self.add_data_fault(VerifiedFaultsTypes.TIMESERIES_AGGREGATION, VerifierResults.PASSED)

    def update_data_verifier_time_series_id_detection_handling(self,
                                                               time_series_id_column_names: List[str],
                                                               duplicate_num: int,
                                                               is_time_series_id_column_names_detected: bool) -> None:
        """
        Detect if the data set has time series identifiers.

        :param time_series_id_column_names:
            List of the time_series_id_column_names. It is either user defined or automatically detected.
        :param duplicate_num:
            Number of duplicate time index rows in the data.
        :param is_time_series_id_column_names_detected:
            True if time_series_id_column_names is detected automatically in dataset.
        """
        if is_time_series_id_column_names_detected:
            self.add_data_fault(VerifiedFaultsTypes.TIMESERIES_ID_DETECTION_UTILITIES, VerifierResults.FIXED)
            self.add_data_fault_parameter(
                VerifiedFaultsTypes.TIMESERIES_ID_DETECTION_UTILITIES,
                {ValidParameterKeys.NUM_OF_DUPLICATE_TIME_INDEX: str(duplicate_num),
                 ValidParameterKeys.DETECTED_TIME_SERIES_ID_COLUMN_NAMES: ', '.join(time_series_id_column_names)})

        # In this case, there is no duplicate time index in dataset, w/o user defined time series id column names.
        elif duplicate_num == 0:
            self.add_data_fault(VerifiedFaultsTypes.TIMESERIES_ID_DETECTION_UTILITIES, VerifierResults.PASSED)

    def update_data_verifier_short_grain_handling(self, padded: List[GrainType],
                                                  dropped: List[GrainType]) -> None:
        """
        Detect if the data set contains the short grains and was corrected.

        :param padded: The list of short series fixed by padding.
        :param dropped: The list of short series dropped.
        :param grain_names: The name of processed grains.
        """

        if not padded and not dropped:
            self.add_data_fault(VerifiedFaultsTypes.TIMESERIES_SHORT_SERIES_HANDLING, VerifierResults.PASSED)
        else:
            self.add_data_fault(VerifiedFaultsTypes.TIMESERIES_SHORT_SERIES_HANDLING, VerifierResults.FIXED)
            if dropped:
                self.add_data_fault_parameter(
                    VerifiedFaultsTypes.TIMESERIES_SHORT_SERIES_HANDLING,
                    self._get_short_grain_dict(ValidParameterKeys.SERIES_DROPPED,
                                               ValidParameterKeys.SERIES_DROPPED_NAMES, dropped))
            if padded:
                self.add_data_fault_parameter(
                    VerifiedFaultsTypes.TIMESERIES_SHORT_SERIES_HANDLING,
                    self._get_short_grain_dict(ValidParameterKeys.SERIES_PADDED,
                                               ValidParameterKeys.SERIES_PADDED_NAMES, padded))

    def _get_short_grain_dict(self,
                              grain_number_key: str, grain_names_key: str,
                              grain_names: List[GrainType]
                              ) -> Dict[str, str]:
        """
        Populate the dictionary with parameters for short grains.

        :param grain_number_key: The key in the fault parameters dictionary for the number of processed grains.
        :param grain_name_key: The key in the fault parameters dictionary for the names of processed grains.
        :param grain_names: The series, which were dropped or padded.
        :return: The populated dictionary with parameters.
        """
        return {
            grain_number_key: str(len(grain_names)),
            grain_names_key: ', '.join(list(map(str, grain_names)))
        }

    def update_data_verifier_for_missing_values_dataframe(
            self,
            input_df: pd.DataFrame,
            numerical_columns: List[str],
            featurization_config: Optional[FeaturizationConfig] = None,
            drop_column_names: Optional[List[str]] = None
    ) -> None:
        """
        Update data verifier with missing values from dataframe and featurization configs..

        :param input_df: Input dataframe.
        :param numerical_columns: All the column names that would be included in the fault verifier.
        :param featurization_config: Featurization config containing all customized featurizers.
        :param drop_column_names: All the column names that won't be considered in the training.
        """
        col_missing_value_dict = {}
        drop_columns = self._get_forecasting_drop_column_names(featurization_config, drop_column_names)

        for col in numerical_columns:
            raw_stats = RawFeatureStats(input_df[col])
            if raw_stats.num_na > 0 and col not in drop_columns:
                col_missing_value_dict[col] = raw_stats.num_na

        if len(col_missing_value_dict) == 0:
            self.add_data_fault(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, VerifierResults.PASSED)
            return
        else:
            self.add_data_fault(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, VerifierResults.DONE)
            transformer_params = None
            if featurization_config is not None and featurization_config.transformer_params is not None:
                transformer_params = featurization_config.transformer_params

            for col, n_missing_values in col_missing_value_dict.items():
                strategy = _TransformerParams.Imputer.Median
                if transformer_params is not None:
                    for cols, params in transformer_params.get(_SupportedTransformers.Imputer):
                        if col in cols:
                            strategy = params.get(_TransformerParams.Imputer.Strategy)
                self.add_data_fault_parameter(
                    VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION,
                    {
                        ValidParameterKeys.COLUMN_NAME: str(col),
                        ValidParameterKeys.NUM_OF_MISSING_VALUES: str(n_missing_values),
                        ValidParameterKeys.IMPUTATION_TYPE: strategy
                    })

    def _get_forecasting_drop_column_names(
            self,
            featurization_config: Optional[FeaturizationConfig] = None,
            drop_column_names: Optional[List[str]] = None
    ) -> Set[str]:
        """
        Get all the forecasting drop columns.

        :param featurization_config: Featurization config which contiains all the customized featurizers.
        :param drop_column_names: All the column names that won't consider for training.
        """
        drop_column_set = set()  # type: Set[str]
        if featurization_config is not None and featurization_config.drop_columns is not None:
            drop_column_set = drop_column_set.union(featurization_config.drop_columns)
        if drop_column_names is not None:
            drop_column_set = drop_column_set.union(drop_column_names)
        return drop_column_set


def _get_columnName(features: List[Any]) -> Any:
    """
    Returns column name from features list of a transformer.
    :param features: List of features obtained from a transformer.
    :return: Any: Column name, same type as input dataset.
    """
    if isinstance(features[0], List):
        col_name = features[0][0]     # When input dataset is pandas dataframe.
    else:
        col_name = features[0]       # When input dataset is numpy array.
    return col_name


def _is_imputer(f: Any) -> bool:
    """Check if Transformer is Imputer Type."""
    if isinstance(f, List):
        return isinstance(f[0], SimpleImputer)
    elif isinstance(f, Pipeline):
        return any([_is_imputer(elem[1]) for elem in f.steps])
    else:
        return False


def print_fault_misconfiguration_detection_results(Run: int) -> None:
    """Print the results of fault/misconfiguration detection results."""
    try:
        pass
    except Exception:
        print("Cannot find the fault/misconfiguration detection results file.")
