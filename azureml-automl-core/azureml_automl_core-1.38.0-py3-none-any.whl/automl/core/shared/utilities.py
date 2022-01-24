# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for validation and conversion."""
import json
import logging
import os
import re
import sys
from typing import Any, Dict, List, Optional, Union, cast

from msrest.exceptions import ClientRequestError

from azureml._common._error_definition import AzureMLError
from azureml._common._error_response.error_hierarchy import ErrorHierarchy
from azureml._common.exceptions import AzureMLException
from azureml.automl.core.constants import LanguageUnicodeRanges
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (AutoMLInternal, AutoMLInternalLogSafe,
                                                                              HttpConnectionFailure,
                                                                              InsufficientMemory, RunInterrupted,
                                                                              Service)
from azureml.automl.core.shared.constants import DatetimeDtype, NumericalDtype
from azureml.automl.core.shared.exceptions import ClientException, ErrorTypes, ResourceException, UserException, \
    AutoMLException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.exceptions import ServiceException as AzureMLServiceException

# For backward compatibility
SOURCE_WRAPPER_MODULE = "automl.client.core.runtime.model_wrappers"
MAPPED_WRAPPER_MODULE = "azureml.train.automl.model_wrappers"

logger = logging.getLogger(__name__)


def _check_if_column_data_type_is_numerical(data_type_as_string: str) -> bool:
    """
    Check if column data type is numerical.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        bool -- 'True' if the dtype returned is 'integer', 'floating', 'mixed-integer-float' or 'decimal'.
                     'False' otherwise.

    """
    if data_type_as_string in list(NumericalDtype.FULL_SET):
        return True

    return False


def _check_if_column_data_type_is_datetime(data_type_as_string: str) -> bool:
    """
    Check if column data type is datetime.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        bool -- 'True' if the dtype returned is 'date', 'datetime' or 'datetime64'. 'False' otherwise.

    """
    return data_type_as_string in DatetimeDtype.FULL_SET


def _check_if_column_data_type_is_int(data_type_as_string: str) -> bool:
    """
    Check if column data type is integer.

    Arguments:
        data_type_as_string {string} -- string carrying the type from infer_dtype().

    Returns:
        boolean -- 'True' if the dtype returned is 'integer'. 'False' otherwise.

    """
    if data_type_as_string == NumericalDtype.Integer:
        return True

    return False


def _check_if_column_data_is_nonspaced_language(unicode_median_value: int) -> bool:
    """
    Check if the median of unicode value belongs to a nonspaced language.

    Arguments:
        unicode_median_value {int} -- median of unicode values of the entire column.

    Returns:
        boolean -- 'True' if the unicode median value is within the unicode ranges of
        languages that has no spaces and supported by bert multilingual.
                        'False' otherwise.

    """
    for range_ in LanguageUnicodeRanges.nonspaced_language_unicode_ranges:
        if range_[0] <= unicode_median_value <= range_[1]:
            return True

    return False


def get_value_int(intstring: str) -> Optional[Union[int, str]]:
    """
    Convert string value to int.

    :param intstring: The input value to be converted.
    :type intstring: str
    :return: The converted value.
    :rtype: int
    """
    if intstring is not None and intstring != "":
        return int(intstring)
    return intstring


def get_value_float(floatstring: str) -> Optional[Union[float, str]]:
    """
    Convert string value to float.
    :param floatstring: The input value to be converted.
    :type floatstring: str
    :return: The converted value.
    :rtype: float
    """
    if floatstring is not None and floatstring != "":
        return float(floatstring)
    return floatstring


def get_value_from_dict(dictionary: Dict[str, Any], names: List[str], default_value: Any) -> Any:
    """
    Get the value of a configuration item that has a list of names.

    :param dictionary: Dictionary of settings with key value pair to look the data for.
    :type dictionary: dict
    :param names: The list of names for the item looking foi.
    :type names: list[str]
    :param default_value: Default value to return if no matching key found
    :return: Returns the first value from the list of names.
    """
    for key in names:
        if key in dictionary:
            return dictionary[key]
    return default_value


def _get_max_min_comparator(objective):
    """Return a comparator either maximizing or minimizing two values. Will not handle nans."""
    if objective == constants.OptimizerObjectives.MAXIMIZE:

        def maximize(x, y):
            if x >= y:
                return x
            else:
                return y

        return maximize
    elif objective == constants.OptimizerObjectives.MINIMIZE:

        def minimize(x, y):
            if x <= y:
                return x
            else:
                return y

        return minimize
    else:
        raise ClientException(
            "Maximization or Minimization could not be determined based on current metric.", has_pii=False
        )


def subsampling_recommended(num_samples):
    """

    :param num_samples: number of samples.
    :type num_samples: int
    :return: True if subsampling is recommended, else False.
    :rtype: bool
    """
    return num_samples >= 50000


def _log_raw_data_stat(raw_feature_stats, prefix_message=None):
    if prefix_message is None:
        prefix_message = ""
    raw_feature_stats_dict = dict()
    for name, stats in raw_feature_stats.__dict__.items():
        try:
            stats_json_str = json.dumps(stats)
        except (ValueError, TypeError):
            stats_json_str = json.dumps(dict())
        raw_feature_stats_dict[name] = stats_json_str
    logger.info("{}RawFeatureStats:{}".format(prefix_message, json.dumps(raw_feature_stats_dict)))


def _get_ts_params_dict(automl_settings: Any) -> Optional[Dict[str, str]]:
    """
    Get time series parameter data.

    Arguments:
        automl_settings {AutoMLSettings} -- automl settings object

    Returns:
        dict -- a dictionary of time series data info

    """
    if automl_settings.is_timeseries:
        dict_time_series = {
            constants.TimeSeries.TIME_COLUMN_NAME: automl_settings.time_column_name,
            constants.TimeSeries.GRAIN_COLUMN_NAMES: automl_settings.grain_column_names,
            constants.TimeSeries.DROP_COLUMN_NAMES: automl_settings.drop_column_names,
            constants.TimeSeriesInternal.OVERWRITE_COLUMNS: automl_settings.overwrite_columns,
            constants.TimeSeriesInternal.DROP_NA: automl_settings.dropna,
            constants.TimeSeriesInternal.TRANSFORM_DICT: automl_settings.transform_dictionary,
            constants.TimeSeries.MAX_HORIZON: automl_settings.max_horizon,
            constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME:
                constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT,
            constants.TimeSeries.COUNTRY_OR_REGION: automl_settings.country_or_region,
            constants.TimeSeriesInternal.CROSS_VALIDATIONS: automl_settings.n_cross_validations,
            constants.TimeSeries.SHORT_SERIES_HANDLING: automl_settings.short_series_handling,
            constants.TimeSeries.MAX_CORES_PER_ITERATION: automl_settings.max_cores_per_iteration,
            constants.TimeSeries.FEATURE_LAGS: automl_settings.feature_lags,
            constants.TimeSeries.TARGET_AGG_FUN: automl_settings.target_aggregation_function,
            constants.TimeSeries.CV_STEP_SIZE: automl_settings.cv_step_size
        }
        # Set window size and lags only if user did not switched it off by setting to None.
        if automl_settings.window_size is not None:
            dict_time_series[constants.TimeSeriesInternal.WINDOW_SIZE] = automl_settings.window_size
        if automl_settings.lags is not None:
            dict_time_series[constants.TimeSeriesInternal.LAGS_TO_CONSTRUCT] = automl_settings.lags
        if automl_settings.iteration_timeout_minutes is not None:
            dict_time_series[constants.TimeSeries.ITERATION_TIMEOUT_MINUTES] = \
                automl_settings.iteration_timeout_minutes
        if hasattr(automl_settings, constants.TimeSeries.SEASONALITY):
            dict_time_series[constants.TimeSeries.SEASONALITY] = getattr(
                automl_settings, constants.TimeSeries.SEASONALITY
            )
        if hasattr(automl_settings, constants.TimeSeries.USE_STL):
            dict_time_series[constants.TimeSeries.USE_STL] = getattr(automl_settings, constants.TimeSeries.USE_STL)
        if hasattr(automl_settings, constants.TimeSeries.FREQUENCY):
            dict_time_series[constants.TimeSeries.FREQUENCY] = getattr(
                automl_settings, constants.TimeSeries.FREQUENCY
            )
        if hasattr(automl_settings, constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG):
            dict_time_series[constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG] = getattr(
                automl_settings, constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG
            )
        return dict_time_series
    else:
        return None


def _get_gpu_training_params_dict(automl_settings: Any) -> Optional[Dict[str, str]]:
    """
    Get gpu training related parameter data.

    Arguments:
        automl_settings {AutoMLSettings} -- automl settings object

    Returns:
        dict -- a dictionary of gpu training info

    """
    if hasattr(automl_settings, "is_gpu") and automl_settings.is_gpu:
        dict_gpu_training = {"processing_unit_type": "gpu"}
        return dict_gpu_training
    else:
        return None


def get_primary_metrics(task: str) -> List[str]:
    """
    Get the primary metrics supported for a given task as a list.

    :param task: Task type supported by AutoML, as defined in azureml.automl.core.shared.constants.Tasks
    :type task: str
    :return: A list of the primary metrics supported for the task.
    """
    if task == constants.Tasks.CLASSIFICATION:
        return list(constants.Metric.CLASSIFICATION_PRIMARY_SET)
    elif task == constants.Tasks.REGRESSION:
        return list(constants.Metric.REGRESSION_PRIMARY_SET)
    elif task == constants.Tasks.FORECASTING:
        return list(constants.Metric.REGRESSION_PRIMARY_SET)
    elif task == constants.Tasks.IMAGE_CLASSIFICATION:
        return list(constants.Metric.IMAGE_CLASSIFICATION_PRIMARY_SET)
    elif task == constants.Tasks.IMAGE_CLASSIFICATION_MULTILABEL:
        return list(constants.Metric.IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET)
    elif task == constants.Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION:
        return list(constants.Metric.IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET)
    elif task in [constants.Tasks.IMAGE_OBJECT_DETECTION, constants.Tasks.IMAGE_INSTANCE_SEGMENTATION]:
        return list(constants.Metric.IMAGE_OBJECT_DETECTION_PRIMARY_SET)
    elif task == constants.Tasks.TEXT_CLASSIFICATION:
        return list(constants.Metric.TEXT_CLASSIFICATION_PRIMARY_SET)
    elif task == constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL:
        return list(constants.Metric.TEXT_CLASSIFICATION_MULTILABEL_PRIMARY_SET)
    elif task == constants.Tasks.TEXT_NER:
        return list(constants.Metric.TEXT_NER_PRIMARY_SET)
    else:
        raise NotImplementedError("Unsupported task.")


def convert_dict_values_to_str(input_dict: Dict[Any, Any]) -> Dict[str, str]:
    """
    Convert a dictionary's values so that every value is a string.

    :param input_dict: the dictionary that should be converted
    :return: a dictionary with all values converted to strings
    """
    fit_output_str = {}
    for key in input_dict:
        if input_dict[key] is None:
            fit_output_str[str(key)] = ""
        else:
            # Cast to string to avoid warnings (PR 143137)
            fit_output_str[str(key)] = str(input_dict[key])
    return fit_output_str


def to_ordinal_string(integer: int) -> str:
    """
    Convert an integer to an ordinal string.

    :param integer:
    :return:
    """
    return "%d%s" % (integer, "tsnrhtdd"[(integer / 10 % 10 != 1) * (integer % 10 < 4) * integer % 10:: 4])


# Regular expressions for date time detection
date_regex1 = re.compile(r"(\d+/\d+/\d+)")
date_regex2 = re.compile(r"(\d+-\d+-\d+)")


def is_known_date_time_format(datetime_str: str) -> bool:
    """
    Check if a given string matches the known date time regular expressions.

    :param datetime_str: Input string to check if it's a date or not
    :return: Whether the given string is in a known date time format or not
    """
    if date_regex1.search(datetime_str) is None and date_regex2.search(datetime_str) is None:
        return False

    return True


def _exception_with_default_error(exception: AzureMLException) -> AzureMLException:
    """Adds a default system error - AutoMLInternal - to the exception, if one doesn't already exist."""
    # AutoMLExceptions will by default have an internal system error
    if isinstance(exception, AutoMLException) or exception._azureml_error is not None:
        if exception._azureml_error and exception._azureml_error.message_parameters:
            for k, v in exception._azureml_error.message_parameters.items():
                exception._azureml_error.message_parameters[k] = _to_str_recursive(v)
        return exception

    exception._azureml_error = AzureMLError.create(
        AutoMLInternalLogSafe, error_message=exception.__class__.__name__, error_details=str(exception)
    )
    return exception


def _to_str_recursive(value: Any) -> Any:
    """
    Convert the value to JSON serializable form.

    :param value: The value to be converted to the JSON-serializable form.
    :return: the value in the python serializable form.
    """
    if isinstance(value, list):
        return [_to_str_recursive(val) for val in value]
    elif isinstance(value, tuple):
        return tuple(_to_str_recursive(val) for val in value)
    elif isinstance(value, dict):
        # We convert key to string, because otherwise it will not be JSON
        # serializable.
        return {str(k): _to_str_recursive(v) for k, v in value.items()}
    else:
        return str(value)


def interpret_exception(exception: BaseException, is_aml_compute: bool = True,
                        **kwargs: Any) -> Union[AzureMLException, AzureMLServiceException]:
    """
    Translate an exception to an AzureMLException.

    If the exception is already one of the known types (e.g. ServiceException, AzureMLException), return the exception
    as-is.

    Dev note: If we see adding more exceptions, or new interpretations for remote vs. local runs, consider converting
    this functionality into its own class

    :param exception: The exception object that needs to be interpreted
    :param is_aml_compute: If the context is an execution service managed run on an AML Compute
                           (e.g. OSErrors, networking errors may need to be interpreted
                           differently based on the run type)
    :param kwargs: Any run-time properties that the ErrorDefinition expects (such as reference_code)
    :return: exception interpreted as an AzureMLException with error code
    """
    # "__traceback__" may not always be available for some of the exceptions
    safe_traceback = exception.__traceback__ if hasattr(exception, "__traceback__") else sys.exc_info()[2]
    # Exceptions coming from the service contain error responses
    if isinstance(exception, AzureMLServiceException):
        return exception

    # If this is an AzureMLException, and is not classified already (i.e. doesn't contain an AzureMLError), add a
    # default system error to the exception and return it.
    if isinstance(exception, AzureMLException):
        exception = _exception_with_default_error(exception)
        return exception

    result = exception
    if isinstance(exception, MemoryError):
        result = ResourceException._with_error(
            AzureMLError.create(InsufficientMemory, **kwargs), inner_exception=exception
        ).with_traceback(safe_traceback)
    elif isinstance(exception, KeyboardInterrupt):
        result = ResourceException._with_error(
            AzureMLError.create(RunInterrupted, **kwargs), inner_exception=exception
        ).with_traceback(safe_traceback)
    elif isinstance(exception, ClientRequestError):
        # These are HTTP connection errors, encountered when the client is overwhelmed with network traffic, preventing
        # it from opening new connections or reaching out to services.
        ref_code = ReferenceCodes._CLIENT_REQUEST_ERROR
        if is_aml_compute:
            # Surface these as Service errors for AML hosted computes
            result = ClientException._with_error(
                AzureMLError.create(Service, error_details=str(exception), reference_code=ref_code, **kwargs),
                inner_exception=exception,
            ).with_traceback(safe_traceback)
        else:
            result = UserException._with_error(
                AzureMLError.create(HttpConnectionFailure, error_details=str(exception),
                                    reference_code=ref_code, **kwargs),
                inner_exception=exception,
            ).with_traceback(safe_traceback)
    else:
        # This was an unhandled exception, interpreting it as a system error
        result = ClientException.from_exception(exception).with_traceback(safe_traceback)

    error_code = ".".join(cast(AzureMLException, result)._azureml_error.error_definition.code_hierarchy)
    logger.warning(
        "Encountered an exception of type: '{}', interpreted as exception of type: '{}', "
        "and error code '{}'.".format(type(exception), type(result), error_code)
    )

    return result


def get_error_code(exception: BaseException, as_hierarchy: bool = False) -> str:
    """
    Build the error code from an exception.

    :param exception: The exception that fails the run.
    :param as_hierarchy: If the complete error hierarchy should be returned
    :return: Return the str containing error_code. If as_hierarchy is True, the hierarchy returned is joined by a '.'
    """
    error_code = ErrorTypes.Unclassified
    try:
        if isinstance(exception, AzureMLException):
            error_code = _get_error_code_from_exception(exception, as_hierarchy)
        elif isinstance(exception, AzureMLServiceException):
            error_code = _get_error_code_from_service_exception(exception, as_hierarchy)
        else:
            # This is a non-azureml exception (e.g. Python's inbuilt exceptions). Use the code after converting
            # the exception to an internal type
            logger.info("Interpreting exception of type {} to get the error code.".format(type(exception)))
            interpreted_exception = interpret_exception(exception)
            error_code = _get_error_code_from_exception(interpreted_exception, as_hierarchy)
    except ValueError:
        logger.warning(
            "Failed to extract error code from the exception of type '{}'. "
            "Setting error_code as {}".format(type(exception), error_code)
        )

    logger.warning(
        "Encountered an exception of type: {}, interpreted as error code {}.".format(type(exception), error_code)
    )

    return str(error_code)


def _get_error_code_from_service_exception(exception: AzureMLServiceException, as_hierarchy: bool) -> str:
    try:
        # ServiceExceptions are expected to contain a 'RootError' field
        if hasattr(exception, "error"):
            # Extract the ErrorResponse from the root error
            error_response = exception.error
            error_hierarchy = ErrorHierarchy(error_response)
            return _get_code_from_hierarchy(error_hierarchy, as_hierarchy)
    except ValueError:
        # This would mean that the service is non-compliant in their error response, keeping the error code
        # as System on our end so that we are tracking it
        logger.warning(
            "An service error was raised with an HTTP code {}. Error details unavailable.".format(
                exception.status_code
            )
        )

    # We couldn't parse the service exception. Create an empty ServiceException to get the right hierarchy
    error_code = Service().code
    if as_hierarchy:
        error_code = ".".join(Service().code_hierarchy)
    return cast(str, error_code)


def _get_code_from_hierarchy(hierarchy: ErrorHierarchy, as_hierarchy: bool) -> str:
    if as_hierarchy:
        return str(hierarchy)
    else:
        return hierarchy.get_leaf() or ErrorTypes.Unclassified


def _get_error_code_from_exception(ex: AzureMLException, as_hierarchy: bool) -> str:
    # For exceptions using the new error contracts, extract the error code from the contained AzureMLError object
    if getattr(ex, "_azureml_error", None) is not None:
        if as_hierarchy:
            return ".".join(ex._azureml_error.error_definition.code_hierarchy)
        return cast(str, ex._azureml_error.error_definition.code)

    # For exceptions that haven't been ported to the new error contracts, get the error code using older semantics
    return _get_error_code_legacy(ex, as_hierarchy)


def _get_error_code_legacy(ex: AzureMLException, as_hierarchy: bool) -> str:
    """
    Attempts to extract an error code from known exceptions that are not be on-boarded to the new error framework.

    For exceptions that aren't even on-boarded to the old error framework, wrap them into an internal system error
    """
    try:
        error_response = ex._serialize_json()
        error_hierarchy = ErrorHierarchy(error_response)
        return _get_code_from_hierarchy(error_hierarchy, as_hierarchy)
    except ValueError:
        # This could be encountered when exceptions haven't even been on-boarded to the legacy error code framework
        # Converting it into a system error
        error_code = AutoMLInternal().code
        if as_hierarchy:
            error_code = ".".join(AutoMLInternal().code_hierarchy)
        logger.warning(
            "Failed to extract legacy error code from the exception of type '{}'. Setting error_code as {}".format(
                type(ex), error_code
            )
        )
        return cast(str, error_code)


def get_min_points(window_size: int,
                   lags: List[int],
                   max_horizon: int,
                   cv: Optional[int],
                   n_step: Optional[int] = None
                   ) -> int:
    """
    Return the minimum number of data points needed for training.

    :param window_size: the rolling window size.
    :param lags: The lag size.
    :param max_horizon: the desired length of forecasting.
    :param cv: the number of cross validations.
    :param n_step:
        Number of periods between the origin_time of one CV fold and the next fold. For
        example, if `n_step` = 3 for daily data, the origin time for each fold will be
        three days apart.
    :return: the minimum number of data points.
    """
    min_points = max_horizon + max(window_size, max(lags)) + 1
    if n_step is None:
        n_step = 1
    if cv is not None:
        min_points = min_points + (cv - 1) * n_step + 1 + max_horizon
    return min_points


# from https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions


class suppress_stdout_stderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr.

    Will suppress all print, even if the print originates in a compiled
    C/Fortran sub-function. Will not suppress raised exceptions,
    since exceptions are printed to stderr just before a script exits,
    and after the context manager has exited.
    """

    def __init__(self):
        """Create the context manager."""
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        """Assign the null pointers to stdout and stderr."""
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        """Re-assign the real stdout/stderr back to (1) and (2)."""
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


def get_default_metric_with_objective(task):
    """Get the dictionary of metric -> objective for the given task.

    :param task: string "classification" or "regression"
    :return: dictionary of metric -> objective
    """
    if task == constants.Tasks.CLASSIFICATION:
        return constants.MetricObjective.Classification
    elif task == constants.Tasks.REGRESSION:
        return constants.MetricObjective.Regression
    elif task == constants.Tasks.IMAGE_CLASSIFICATION:
        return constants.MetricObjective.ImageClassification
    elif task == constants.Tasks.IMAGE_CLASSIFICATION_MULTILABEL:
        return constants.MetricObjective.ImageClassificationMultiLabel
    elif task == constants.Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION:
        return constants.MetricObjective.ImageClassificationMultiLabel
    elif task in [constants.Tasks.IMAGE_OBJECT_DETECTION, constants.Tasks.IMAGE_INSTANCE_SEGMENTATION]:
        return constants.MetricObjective.ImageObjectDetection
    elif task == constants.Subtasks.FORECASTING:
        return constants.MetricObjective.Forecast
    elif task == constants.Tasks.TEXT_CLASSIFICATION:
        return constants.MetricObjective.TextClassification
    elif task == constants.Tasks.TEXT_CLASSIFICATION_MULTILABEL:
        return constants.MetricObjective.TextClassificationMultilabel
    elif task == constants.Tasks.TEXT_NER:
        return constants.MetricObjective.TextNer
    else:
        raise NotImplementedError


def minimize_or_maximize(metric, task=None):
    """Select the objective given a metric.

    Some metrics should be minimized and some should be maximized
    :param metric: the name of the metric to look up
    :param task: one of constants.Tasks.
    :return: returns one of constants.OptimizerObjectives.
    """
    if task is None:
        reg_metrics = get_default_metric_with_objective(constants.Tasks.REGRESSION)
        class_metrics = get_default_metric_with_objective(constants.Tasks.CLASSIFICATION)
        if metric in reg_metrics:
            task = constants.Tasks.REGRESSION
        elif metric in class_metrics:
            task = constants.Tasks.CLASSIFICATION
        else:
            msg = 'Could not find objective for metric "{0}"'
            raise ClientException(msg.format(metric)).with_generic_msg(msg.format("[MASKED]"))
    return get_default_metric_with_objective(task)[metric]
