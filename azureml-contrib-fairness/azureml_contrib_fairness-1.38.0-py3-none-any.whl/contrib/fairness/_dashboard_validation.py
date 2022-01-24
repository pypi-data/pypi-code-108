# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import os
import sys

import jsonschema

from ._exceptions import DashboardValidationException

from ._constants import FairlearnDashboardKeys as FDK
from ._constants import FairlearnDashboardPredictionTypes as FDPT

_logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)

_DASHBOARD_ERROR = "Dashboard"
_DASHBOARD_UPLOAD_TOO_LARGE = "Upload size too large ({0} > {1} bytes). " \
    "Reduce number of samples, predictions or sensitive features"
_SCHEMA_TYPE_INVALID = "'schemaType' of '{0}' is invalid"
_SCHEMA_VERSION_INVALID = "'schemaVersion' of {0} is invalid"
_PREDICTION_TYPE_INVALID = "'predictionType' of '{0}' is invalid"
_BAD_Y_PRED = "Found 'predictedY' of length {0} instead of expected {1}"
_BAD_MODEL_NAMES = "Found {0} 'modelNames' but expected {1}"
_BAD_SF_LENGTH = "Sensitive feature '{0}' had 'binVector' of length {1} instead of expected {2}"
_BAD_SF_GROUPS = "Sensitive feature '{0}' had {1} 'binLabels' but expected {2}"
_BAD_METRICS_DIM1 = "First dimension of 'precomputedMetrics' had length {0} but expected {1}"
_BAD_METRICS_DIM2 = "Second dimension of 'precomputedMetrics' had length {0} but expected {1}"

_JSON_SCHEMA_FILE = "dashboardDictionary-0.json"


def _build_message(fmt, *args):
    """Format an exception message."""
    mesg = fmt.format(*args)

    return "{0}: {1}".format(_DASHBOARD_ERROR, mesg)


def _check_serialisation_size(dash_dict, max_bytes):
    """Ensure an object isn't too large when serialized."""
    dash_str = json.dumps(dash_dict)
    dash_str_bytes = sys.getsizeof(dash_str)
    if dash_str_bytes > max_bytes:
        msg = _build_message(_DASHBOARD_UPLOAD_TOO_LARGE,
                             dash_str_bytes,
                             max_bytes)
        raise DashboardValidationException(msg)


def _check_against_json_schema(dashboard_dict):
    schema_path = os.path.join(os.path.dirname(__file__), _JSON_SCHEMA_FILE)
    with open(schema_path, 'r') as schema_file:
        schema = json.load(schema_file)

    jsonschema.validate(dashboard_dict, schema)


def validate_dashboard_dictionary(dashboard_dict, max_serialization_bytes):
    """Ensure dictionary is a valid Dashboard.

    This does not look inside any of the metrics dictionaries, so
    it is not a complete validation. However, it does check the
    basic structure and consistency. The `max_serialization_bytes` parameter
    is an imperfect limit on the size of the uploaded objects. It
    looks at the size of the dictionary when put into a single JSON file,
    but in reality we split the dictionary up. However, the error induced
    by this should be small.

    :param dashboard_dict: The dictionary to be validated
    :type dashboard_dict: dict
    :param max_serialization_bytes: Limit on size of uploaded objects
    :type max_serialization_bytes: int
    """
    _logger.info("Starting validation of dashboard dictionary")

    _check_serialisation_size(dashboard_dict, max_serialization_bytes)

    schema_type = dashboard_dict[FDK.SCHEMA_TYPE]
    if schema_type != 'dashboardDictionary':
        msg = _build_message(_SCHEMA_TYPE_INVALID, schema_type)
        raise DashboardValidationException(msg)
    schema_version = dashboard_dict[FDK.SCHEMA_VERSION]
    # Will want to update the following prior to release
    if schema_version != 0:
        msg = _build_message(_SCHEMA_VERSION_INVALID, schema_version)
        raise DashboardValidationException(msg)

    pred_type = dashboard_dict[FDK.PREDICTION_TYPE]
    if pred_type not in FDPT.VALID_TYPES:
        msg = _build_message(_PREDICTION_TYPE_INVALID, pred_type)
        raise DashboardValidationException(msg)

    len_y_true = len(dashboard_dict[FDK.Y_TRUE])
    num_y_pred = len(dashboard_dict[FDK.Y_PRED])
    for y_pred in dashboard_dict[FDK.Y_PRED]:
        if len(y_pred) != len_y_true:
            msg = _build_message(_BAD_Y_PRED, len(y_pred), len_y_true)
            raise DashboardValidationException(msg)

    len_model_names = len(dashboard_dict[FDK.MODEL_NAMES])
    if len_model_names != num_y_pred:
        msg = _build_message(_BAD_MODEL_NAMES, len_model_names, num_y_pred)
        raise DashboardValidationException(msg)

    num_sf = len(dashboard_dict[FDK.SENSITIVE_FEATURES])
    for sf in dashboard_dict[FDK.SENSITIVE_FEATURES]:
        sf_name = sf[FDK.SENSITIVE_FEATURE_NAME]
        sf_vector = sf[FDK.SENSITIVE_FEATURE_VALUES]

        if len(sf_vector) != len_y_true:
            msg = _build_message(_BAD_SF_LENGTH,
                                 sf_name,
                                 len(sf_vector),
                                 len_y_true)
            raise DashboardValidationException(msg)

        sf_classes = sf[FDK.SENSITIVE_FEATURE_CLASSES]
        num_classes = 1 + max(sf_vector)
        if len(sf_classes) != num_classes:
            msg = _build_message(_BAD_SF_GROUPS,
                                 sf_name,
                                 len(sf_classes),
                                 num_classes)
            raise DashboardValidationException(msg)

    len_metrics_d1 = len(dashboard_dict[FDK.METRICS])
    if len_metrics_d1 != num_sf:
        msg = _build_message(_BAD_METRICS_DIM1,
                             len_metrics_d1,
                             num_sf)
        raise DashboardValidationException(msg)

    for metrics_arr in dashboard_dict[FDK.METRICS]:
        if len(metrics_arr) != num_y_pred:
            msg = _build_message(_BAD_METRICS_DIM2,
                                 len(metrics_arr),
                                 num_y_pred)
            raise DashboardValidationException(msg)

    _check_against_json_schema(dashboard_dict)
    _logger.info("Validation of dashboard dictionary successful")
