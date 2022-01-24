# -*- encoding: utf-8 -*-

"""This module is not considered part of the public interface. As of 2.3, anything here
may change or be removed without warning."""
from collections import defaultdict
from datetime import date, datetime
import re

from dateutil import parser, tz
import numpy as np
import pandas as pd
import pytz
import six

from .deprecation import deprecated, deprecation_warning  # noqa
from .sourcedata import dataframe_to_buffer, is_urlsource, recognize_sourcedata  # noqa

ALL_CAPITAL = re.compile(r"(.)([A-Z][a-z]+)")
CASE_SWITCH = re.compile(r"([a-z0-9])([A-Z])")
UNDERSCORES = re.compile(r"([a-z]?)(_+)([a-z])")


class rawdict(dict):
    """
    Dictionaries returned from models will have their keys snakeCased.
    Wrapping them in rawdict will pass them through to the API verbatim.
    """

    pass


def underscorize(value):
    partial_result = ALL_CAPITAL.sub(r"\1_\2", value)
    return CASE_SWITCH.sub(r"\1_\2", partial_result).lower()


def underscoreToCamel(match):
    prefix, underscores, postfix = match.groups()
    if len(underscores) > 1:
        # underscoreToCamel('sample_pct__gte') -> 'samplePct__gte'
        return match.group()
    return prefix + postfix.upper()


def camelize(value):
    return UNDERSCORES.sub(underscoreToCamel, value)


def from_api(data, do_recursive=True, keep_attrs=None, keep_null_keys=False):
    if type(data) not in (dict, list):
        return data
    if isinstance(data, list):
        return _from_api_list(data, do_recursive=do_recursive, keep_null_keys=keep_null_keys)
    return _from_api_dict(
        data, do_recursive=do_recursive, keep_attrs=keep_attrs, keep_null_keys=keep_null_keys
    )


def _from_api_dict(data, do_recursive=True, keep_attrs=None, keep_null_keys=False):
    keep_attrs = keep_attrs or []
    # prepare attributes in format 'top.middle.bottom' for processing
    parsed_attrs = []
    for attr in keep_attrs:
        if isinstance(attr, six.string_types):
            parsed_attrs.append(attr.split("."))
        else:
            parsed_attrs.append(attr)
    # take index 0 since recursion goes from top to bottom
    current_level = [attr.pop(0) for attr in parsed_attrs if len(attr)]
    # filter out empty attrs to pass through recursive call
    next_level_attrs = [attr for attr in parsed_attrs if attr]

    app_data = {}
    for k, v in six.iteritems(data):
        k_under = underscorize(k)
        if v is None and k_under not in current_level and not keep_null_keys:
            continue
        if do_recursive:
            data_val = from_api(
                v,
                do_recursive=do_recursive,
                keep_attrs=next_level_attrs,
                keep_null_keys=keep_null_keys,
            )
        else:
            data_val = v
        app_data[k_under] = data_val
    return app_data


def _from_api_list(data, do_recursive=True, keep_null_keys=False):
    return [
        from_api(datum, do_recursive=do_recursive, keep_null_keys=keep_null_keys) for datum in data
    ]


def remove_empty_keys(metadata, keep_attrs=None):
    keep_attrs = keep_attrs or []
    return {k: v for k, v in metadata.items() if v is not None or k in keep_attrs}


def parse_time(time_str):
    try:
        return parser.parse(time_str, tzinfos={"UTC": tz.tzutc()})
    except Exception:
        return time_str


def datetime_to_string(datetime_obj, ensure_rfc_3339=False):
    """ Converts to isoformat
    """
    if not isinstance(datetime_obj, datetime):
        msg = "expected to be passed a datetime.datetime, was passed {}".format(type(datetime_obj))
        raise ValueError(msg)
    if ensure_rfc_3339 and not datetime_obj.tzinfo:
        datetime_obj = datetime_obj.replace(tzinfo=pytz.utc)
    return datetime_obj.isoformat()


def _is_api_object(obj):
    # local import of APIObject is required due to circular imports between
    # utils.__init__.py, rest.py, client.py, and api_object.py if APIObject
    # is imported at the top of the file.
    from datarobot.models.api_object import APIObject

    return issubclass(type(obj), APIObject)


def to_api(data, keep_attrs=None):
    """
    :param data: dictionary {'max_digits': 1}
    :return: {'maxDigits': 1}
    """
    if not data:
        return {}
    assert isinstance(data, dict) or _is_api_object(data), "Wrong type"
    return _to_api_item(data, keep_attrs)


def _to_dict(item):
    return {k: v for k, v in item.__dict__.items() if not k.startswith("_") and not callable(v)}


def _to_api_item(item, keep_attrs=None):
    if isinstance(item, rawdict):
        return item
    if _is_api_object(item):
        return _to_api_item(_to_dict(item))
    elif isinstance(item, dict):
        dense_item = remove_empty_keys(item, keep_attrs)
        return {
            camelize(k): _to_api_item(v, keep_attrs=keep_attrs)
            for k, v in six.iteritems(dense_item)
        }
    elif isinstance(item, list):
        return [_to_api_item(subitem, keep_attrs=keep_attrs) for subitem in item]
    elif isinstance(item, datetime):
        return datetime_to_string(item)
    elif isinstance(item, date):
        return item.isoformat()
    else:
        return item


def get_id_from_response(response):
    location_string = response.headers["Location"]
    return get_id_from_location(location_string)


def get_id_from_location(location_string):
    return location_string.split("/")[-2]


def get_duplicate_features(features):
    duplicate_features = set()
    seen_features = set()
    for feature in features:
        if feature in seen_features:
            duplicate_features.add(feature)
        else:
            seen_features.add(feature)
    return list(duplicate_features)


def raw_prediction_response_to_dataframe(pred_response, class_prefix):
    """Raw predictions for classification come as nested json objects.

    This will extract it to be a single dataframe.

    Parameters
    ----------
    pred_response : dict
        The loaded json object returned from the prediction route.
    class_prefix : str
            The prefix to append to labels in the final dataframe (e.g., apple -> class_apple)

    Returns
    -------
    frame : pandas.DataFrame

    """
    # warning: we can't use the `from_api` function here due to the performance issues when
    # converting larger prediction responses
    predictions = pred_response["predictions"]
    task_type = pred_response["task"]

    frame = pd.DataFrame.from_records(predictions)
    frame = _underscorize_df_columns(frame)
    if task_type == "Multilabel":
        frame = _pivot_multilabel_predictions(frame, class_prefix)
    else:
        has_prediction_values = "prediction_values" in frame.columns
        if has_prediction_values:
            frame = _pivot_prediction_labels(frame, class_prefix)
        if "prediction_explanations" in frame.columns:
            frame = _pivot_prediction_explanations(frame, pred_response, has_prediction_values)

    # Remove some columns with all null values
    # (i.e. TS models return empty series_id for single-series projects)
    drop_cols = [
        col
        for col in ("positive_probability", "series_id")
        if col in frame and frame[col].isna().all()
    ]
    if drop_cols:
        frame = frame.drop(columns=drop_cols)

    return frame


def _underscorize_df_columns(frame):
    """ Rename the DataFrame columns from the camel case to underscore

    Parameters
    ----------
    frame : pandas.DataFrame

    Returns
    -------
    frame : pandas.DataFrame

    """
    original_columns = list(frame.columns)
    converted_columns = [underscorize(col) for col in original_columns]
    column_mapping = dict(zip(original_columns, converted_columns))
    return frame.rename(columns=column_mapping)


def _pivot_multilabel_predictions(frame, class_prefix):
    """
    Explodes the prediction_values column into multiple columns for prediction labels, thresholds,
    and predictions.

    Parameters
    ----------
    frame : pandas.DataFrame
        The initial dataframe obtained from prediction response.
    class_prefix : str
        The prefix to append to labels in the final dataframe (e.g., apple -> class_apple)

    Returns
    -------
    pandas.DataFrame
        The converted predictions
    """
    if "prediction_values" not in frame:
        return frame
    labels = [entry["label"] for entry in frame.prediction_values[0]]

    values = np.empty((frame.shape[0], len(labels)), np.float32)
    thresholds = np.empty((frame.shape[0], len(labels)), np.float32)
    predictions = np.empty((frame.shape[0], len(labels)), np.int8)
    for i, pair in enumerate(zip(frame.prediction_values, frame.prediction)):
        row, prediction = pair
        values[i] = np.array([[col["value"] for col in row]])
        thresholds[i] = np.array([[col["threshold"] for col in row]])
        predictions[i] = np.array([[1 if col["label"] in prediction else 0 for col in row]])

    values_df = pd.DataFrame(
        values, columns=[u"{}{}".format(class_prefix, label) for label in labels]
    )
    thresholds_df = pd.DataFrame(
        thresholds, columns=[u"threshold_{}".format(label) for label in labels]
    )
    predictions_df = pd.DataFrame(
        predictions, columns=[u"prediction_{}".format(label) for label in labels]
    )
    return pd.concat(
        [
            frame.drop(["prediction_values", "prediction"], axis=1),
            values_df,
            thresholds_df,
            predictions_df,
        ],
        axis=1,
    )


def _pivot_prediction_explanations(frame, pred_response, has_prediction_values):
    """ Pivot the prediction_explanations from the dictionary to columns

    frame : DataFrame
        the DataFrame build based on predictions response
    pred_response : dict
        the response that contains explanations details applicable to all predictions
    has_prediction_values : bool
        flag showing whether there are prediction values for multiple class
    Returns
    -------
    frame : DataFrame
         the dataframe with parsed prediction explanations
    """
    _FEATURE = "Explanation_{}_feature_name"
    _FEATURE_VAL = "Explanation_{}_feature_value"
    _STRENGTH = "Explanation_{}_strength"

    columns = ()
    if has_prediction_values:
        columns += ("explained_class",)
    first_row = frame["prediction_explanations"][0]
    for i in range(len(first_row)):
        idx = i + 1
        columns += (
            _FEATURE.format(idx),
            _FEATURE_VAL.format(idx),
            _STRENGTH.format(idx),
        )
    data = []
    for prediction_explanations in frame["prediction_explanations"]:
        data_row = ()
        if has_prediction_values:
            data_row += (prediction_explanations[0]["label"],)
        for prediction_explanation in prediction_explanations:
            data_row += (
                prediction_explanation["feature"],
                prediction_explanation["featureValue"],
                prediction_explanation["strength"],
            )
        data.append(data_row)
    prediction_explanation_df = pd.DataFrame.from_records(data, columns=columns)
    frame = pd.concat([frame, prediction_explanation_df], axis=1)
    frame = frame.drop("prediction_explanations", axis=1)

    frame["shap_remaining_total"] = frame["prediction_explanation_metadata"].apply(
        lambda x: x.get("shap_remaining_total", None)
    )
    frame = frame.drop("prediction_explanation_metadata", axis=1)

    # shapBaseValue is either list with single float item or scalar float
    shap_base_value = pred_response["shapBaseValue"]
    if isinstance(shap_base_value, list):
        shap_base_value = shap_base_value[0]
    frame["shap_base_value"] = shap_base_value
    return frame


def _pivot_prediction_labels(frame, class_prefix):
    """ Pivot the prediciton_values from the dictionary to columns

    Parameters
    ----------
    frame : pandas.DataFrame

    Returns
    -------
    frame : pandas.DataFrame

    """
    wrapper = defaultdict(list)
    for pred_row in frame["prediction_values"]:
        for pred_value in pred_row:
            col_name = u"".join((class_prefix, u"{}".format(pred_value["label"])))
            wrapper[col_name].append(pred_value["value"])
    pred_frame = pd.DataFrame.from_records(wrapper)
    frame = pd.concat([frame, pred_frame], axis=1)
    return frame.drop("prediction_values", axis=1)


def encode_utf8_if_py2(string):
    """__repr__ is supposed to return string (bytes) in 2 and string (unicode) in 3
    this function can be used to convert our unicode to strings in Python 2 but leave them alone
    in Python 3"""
    return string.encode("utf-8") if six.PY2 else string
