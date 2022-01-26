from typing import Dict, Tuple, Union, List, Optional
from autoai_ts_libs.utils.messages.messages import Messages

import pandas as pd
import numpy as np
from numpy import array
import logging

tslogger = logging.getLogger(__name__)


def make_holdout_split(
        dataset: pd.DataFrame,
        target_columns: Union[list, int, str],
        learning_type: str = "forecasting",
        test_size: Union[float, int] = 20,
        feature_columns: Union[list, int, str] = -1,
        timestamp_column: Union[int, float, str] = -1,
        lookback_window: int = 0,
        return_only_holdout: bool = False,
) -> Union[Tuple[array, array, array, array], Tuple[array, array, array, array, array, array, array, array]]:
    """
        This function is dedicated to split data into both training and holdout for time series
    Parameters
    ----------
    dataset: DataFrame, required
        A pandas dataframe
    target_columns: int or str, required
        Index or names of target time series in df
    learning_type: str
        Default "forecasting". Only "forecasting" is supported currently.
    test_size: float or int, optional
        Default 20. If float, between 0 and 1, indicates the radio of houldout dataset to the entire data. If int, represents the
        absolute number of houldout samples.
    feature_columns: int or str, optional
        Index or names of features in df
    timestamp_column: int or str, optional
        Index or name of timestamp column in df
    lookback_window: int, optional
        Default 0. The past date/time range to train the model and generate pipelines.
    return_only_holdout: bool, optional
        Default False. If set to True it will return only holdout dataset and indices but without training dataset and indices.
    Returns
    -------
    Numpy arrays:
        x_train, x_holdout,
        y_train, y_holdout,
        x_train_indices, x_holdout_indices,
        y_train_indices, y_holdout_indices
        if return_only_holdout:
            x_holdout, y_holdout,
            x_holdout_indices, y_holdout_indices
    """
    if dataset is None:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0069E'))

    if learning_type not in ("forecasting", ):
        raise Exception(Messages.get_message(learning_type, message_id='AUTOAITSLIBS0068E'))

    n_samples = len(dataset)
    test_size_type = np.asarray(test_size).dtype.kind
    if (test_size_type == 'i' and (test_size >= n_samples or test_size <= 0)
            or test_size_type == 'f' and (test_size <= 0 or test_size >= 1)):
        raise Exception(Messages.get_message(test_size, n_samples, message_id='AUTOAITSLIBS0070E'))
    holdout_size = int(n_samples * test_size) if (test_size_type == 'f') else test_size

    if not isinstance(target_columns, list):
        target_columns = [target_columns]

    if not isinstance(feature_columns, list):
        if feature_columns != -1:
            feature_columns = [feature_columns]
        else:
            feature_columns = []

    warn_msg = []
    df = dataset
    data_cols, time_col, used_cols = None, None, None
    fet_cols = []

    # Support string targets
    df_columns = df.columns.to_list()
    target_column_indexs = []
    for target in target_columns:
        if isinstance(target, int):
            target_column_indexs.append(target)
        elif isinstance(target, str):
            if target in df_columns:
                target_column_indexs.append(df_columns.index(target))
            else:
                # Warning
                print("target: %s is invalid" % (target))
        elif isinstance(target, float):
            target_column_indexs.append(int(target))

    target_columns = target_column_indexs

    if len(target_columns) == 0:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0072E'))

    # Support string features
    feature_column_indexs = []
    for feature in feature_columns:
        if isinstance(feature, int):
            feature_column_indexs.append(feature)
        elif isinstance(feature, str):
            if feature in df_columns:
                feature_column_indexs.append(df_columns.index(feature))
            else:
                # Warning
                print("feature: %s is invalid" % (feature))
        elif isinstance(feature, float):
            feature_column_indexs.append(int(feature))

    feature_columns = feature_column_indexs

    # Support string timestamp
    timestamp_column_index = -1
    if isinstance(timestamp_column, int):
        timestamp_column_index = timestamp_column
    elif isinstance(timestamp_column, str):
        if timestamp_column in df_columns:
            timestamp_column_index = df_columns.index(timestamp_column)
        else:
            # Warning
            print("timestamp_column: %s is invalid" % (timestamp_column))
    elif isinstance(timestamp_column, float):
        timestamp_column_index = int(timestamp_column)

    timestamp_column = timestamp_column_index


    if timestamp_column != -1:
        time_col = df.columns[timestamp_column]

    for i in target_columns:
        if i < 0 or i > (len(df.columns) - 1):
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0072E'))
        if pd.api.types.is_string_dtype(df.dtypes[i]):
            try:
                target_name = df.columns[i]
                df[target_name] = df[target_name].map(
                    lambda tar: str(tar).strip('\"')
                )
                df[target_name] = df[target_name].map(
                    lambda x: float(x) if len(x) != 0 else float('nan')
                )
            except Exception as ex:
                raise Exception(Messages.get_message(target_name, str(ex), message_id='AUTOAITSLIBS0073E'))
    tgt_cols = [df.columns.to_list()[i] for i in target_columns]

    if time_col is not None and time_col in tgt_cols:
        raise Exception(Messages.get_message(time_col, message_id='AUTOAITSLIBS0074E'))

    if time_col is not None:
        if (True in df.duplicated(subset=[time_col]).to_list()):
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0075E'))

        if pd.api.types.is_numeric_dtype(df[time_col]):
            # nothing to do, assuming unix timestamp
            pass
        elif pd.api.types.is_string_dtype(df[time_col]):
            # check string format, and convert to unix timestamp
            try:
                from dateutil.parser import parse

                df[time_col] = df[time_col].map(
                    lambda ts: parse((str(ts)).strip('\"'), fuzzy=False)
                )
            except Exception as e:
                try:
                    from dateutil.parser import isoparser, isoparse
                    df[time_col] = df[time_col].map(
                        lambda ts: isoparse((str(ts)).strip('\"'))
                    )
                except Exception as ex:
                    raise Exception(Messages.get_message(time_col, message_id='AUTOAITSLIBS0076E'))
        else:
            # don't know how to handle, raise error
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0077E'))

        # ensure data sorted by time
        df = df.sort_values(by=time_col)

        # calculate relative standard deviation (in seconds) of successive timestamp deltas
        timestamps = df[time_col].to_list()
        timedeltas = []
        for i in range(1, len(timestamps)):
            diff = timestamps[i] - timestamps[i - 1]
            if type(diff) == pd._libs.tslibs.timedeltas.Timedelta:
                timedeltas.append(diff.total_seconds())
            else:
                timedeltas.append(diff)
        import statistics

        m = statistics.mean(timedeltas)
        s = statistics.stdev(timedeltas)
        if m == 0:
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0071E'))
        r = 100.0 * s / m
        # Warning
        if r > 20.0:
            print(Messages.get_message(message_id='AUTOAITSLIBS0004W'))

    if len(feature_columns) > 0:
        fet_cols = [df.columns.to_list()[i] for i in feature_columns]

    # prepare data_cols and all_cols (= data_cols + time)
    data_cols = []
    for item in fet_cols:
        data_cols.append(item)
    for item in tgt_cols:
        if item not in data_cols:
            data_cols.append(item)

    if time_col is not None:
        used_cols = [time_col] + data_cols
    else:
        used_cols = data_cols

    # prepare data for training and testing
    loaded_data = df[used_cols]
    X_ = loaded_data[data_cols].to_numpy()
    y_ = loaded_data[data_cols].to_numpy()

    X, y = (
        X_.astype(float).reshape(-1, max(1, len(data_cols))),
        y_.astype(float).reshape(-1, max(1, len(data_cols))),
    )

    training_size = len(X_) - holdout_size
    data = {}
    data["X_train"], data["y_train"] = (
        X[: training_size, :],
        y[: training_size, :],
    )
    data["X_train_indices"], data["y_train_indices"] = (
        np.array(range(0, training_size)),
        np.array(range(0, training_size))
    )

    data["X_test"], data["y_test"] = (
        X[training_size - lookback_window:, :],
        y[training_size:, :],
    )
    data["X_test_indices"], data["y_test_indices"] = (
        np.array(range(training_size - lookback_window, len(X))),
        np.array(range(training_size, len(y)))
    )

    if return_only_holdout:
        return data["X_test"], data["y_test"], \
               data["X_test_indices"], data["y_test_indices"]
    else:
        return data["X_train"], data["X_test"], \
               data["y_train"], data["y_test"], \
               data["X_train_indices"], data["X_test_indices"], \
               data["y_train_indices"], data["y_test_indices"]



