# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for specifying dataset partition preparation.

Partition preparation occurs automatically, when you use a :mod:`azureml.opendatasets` classe that requires
a partition of data, such as the :class:`azureml.opendatasets.NycTlcGreen` class.
"""

from datetime import datetime
from functools import partial
from typing import List
import azureml.dataprep as dprep


def prep_partition_datetime(
        dflow: dprep.Dataflow,
        start_date: datetime,
        end_date: datetime,
        pattern: List[str]):
    r"""
    Prepare partition path 'year=\\d+/month=\\d+/'.

    :param dflow: An instance of dataprep.Dataflow.
    :type dflow: azureml.dataprep.Dataflow
    :param start_date: The start datetime of the Dataset.
    :type start_date: datetime
    :param end_date: The end datetime of the Dataset.
    :type end_date: datetime
    :param pattern: The datetime pattern.
    :type pattern: builtin.list
    """
    # Extract out Path to files from StreamInfo object in 'Path' column.
    filepath_dflow = dflow.add_column(
        expression=dprep.get_stream_name(dflow['Path']),
        new_column_name='FilePath',
        prior_column='Path')
    # Build datetime pattern.
    partition_pattern = ''
    for pat in pattern:
        partition_pattern += '%s=(?<%s>\\d+)\\/' % (pat, pat)
    # Use regex to extract out year/month/day info from 'FilePath' column
    regex = dprep.RegEx(partition_pattern)
    dflow_date_record = filepath_dflow.add_column(
        new_column_name='PathDateRecord',
        prior_column='FilePath',
        expression=regex.extract_record(filepath_dflow['FilePath']))

    # Convert PathDateRecord to actual Datetime value.
    pat_list = []
    for pat in pattern:
        pat_list.append(dprep.col(pat, dflow_date_record['PathDateRecord']))
    pat_list_length = len(pat_list)
    if (pat_list_length == 1):      # year only
        pat_list += ['1'] * 2 + ['0'] * 3
    elif (pat_list_length == 2):    # year, month
        pat_list += ['1'] + ['0'] * 3
    else:
        pat_list += ['0'] * 3
    dflow_datetime = dflow_date_record.add_column(
        new_column_name='PathDate',
        prior_column='PathDateRecord',
        expression=dprep.create_datetime(*pat_list))

    # OPTIONAL: Drop unneeded columns.
    dflow_datetime = dflow_datetime.drop_columns(['PathDateRecord', 'FilePath'])

    # Filter on PathDate column
    if start_date:
        dflow_datetime = dflow_datetime.filter(
            dflow_datetime['PathDate'] >= start_date.replace(second=0, microsecond=0, minute=0, hour=0, day=1))

    if end_date:
        dflow_datetime = dflow_datetime.filter(dflow_datetime['PathDate'] <= end_date)

    return dflow_datetime


prep_partition_year = partial(prep_partition_datetime, pattern=['year'])
prep_partition_year_month = partial(prep_partition_datetime, pattern=['year', 'month'])
prep_partition_year_month_day = partial(prep_partition_datetime, pattern=['year', 'month', 'day'])
prep_partition_puYear_puMonth = partial(prep_partition_datetime, pattern=['puYear', 'puMonth'])
