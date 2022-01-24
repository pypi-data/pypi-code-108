#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import csv
import os

import pandas as pd
import six

from .. import errors


def dataframe_to_buffer(df):
    """Convert a dataframe to a serialized form in a buffer

    Parameters
    ----------
    df : pandas.DataFrame
        The data to serialize

    Returns
    -------
    buff : StringIO()
        The data. The descriptor will be reset before being returned (seek(0))
    """
    buff = six.StringIO()
    df.to_csv(buff, encoding="utf-8", index=False, quoting=csv.QUOTE_ALL)
    buff.seek(0)
    return buff


def list_of_records_to_buffer(list_of_records):
    """

    Parameters
    ----------
    list_of_records: list(dict)
        A list of records to serialize. Each row should be a dict with the same keys as the first
        row.

    Returns
    -------
    buffer: six.StringIO
        The data. The descriptor will be reset before being returned (seek(0))
    """
    buff = six.StringIO()
    headers = [key for key in list_of_records[0]]
    csv_writer = csv.DictWriter(buff, fieldnames=headers)
    csv_writer.writeheader()
    csv_writer.writerows(list_of_records)
    buff.seek(0)
    return buff


def is_urlsource(sourcedata):
    """ Whether sourcedata is of url kind
    """
    return isinstance(sourcedata, six.string_types) and (
        sourcedata.startswith("http")
        or sourcedata.startswith("file:")
        or sourcedata.startswith("s3:")
    )


def recognize_sourcedata(sourcedata, default_fname):
    """Given a sourcedata figure out if it is a filepath, dataframe, or
    filehandle, and then return the correct kwargs for the upload process
    """
    if isinstance(sourcedata, pd.DataFrame):
        buff = dataframe_to_buffer(sourcedata)
        return {"filelike": buff, "fname": default_fname}
    elif hasattr(sourcedata, "read") and hasattr(sourcedata, "seek"):
        return {"filelike": sourcedata, "fname": default_fname}
    elif isinstance(sourcedata, six.string_types) and os.path.isfile(sourcedata):
        return {"file_path": sourcedata, "fname": os.path.split(sourcedata)[1]}
    elif isinstance(sourcedata, six.binary_type) and not is_urlsource(sourcedata):
        assert_modelable(sourcedata)
        return {"content": sourcedata, "fname": default_fname}
    else:
        # Checking if string representation of an object can be used as a file path.
        # The main reason for this is supporting Python's pathlib.Path without having extra
        # dependency for python lower than 3.4.
        try:
            if os.path.isfile(str(sourcedata)):
                return {"file_path": str(sourcedata), "fname": os.path.split(str(sourcedata))[1]}
        except Exception:
            pass

    err_msg = (
        "sourcedata parameter not understood. Use pandas "
        "DataFrame, file object or string that is either a "
        "path to file or raw file content to specify data "
        "to upload"
    )
    raise errors.InputNotUnderstoodError(err_msg)


def assert_modelable(sourcedata):
    """
    Uses a heuristic to assert that the given argument is not a
    filepath.

    Some users have mistyped filepaths before, which
    the function `recognize_sourcedata` interpreted as being
    the actual data to use for modeling. This would lead to other
    problems later on.

    Parameters
    ----------
    sourcedata : six.binary_type
        The data which we are trying to assert is not a mistyped
        file path.

    Raises
    ------
    InputNotUnderstoodError
        If this does look like a filepath (it should not)
    """
    if len(sourcedata) < 500 and len(sourcedata.splitlines()) == 1:
        raise errors.InputNotUnderstoodError(
            "The source appears to contain only a single line of data. "
            "Did you mistype a file path?"
        )
