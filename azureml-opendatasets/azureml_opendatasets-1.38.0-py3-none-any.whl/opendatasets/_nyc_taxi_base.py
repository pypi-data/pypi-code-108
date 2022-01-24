# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""City crime."""

from datetime import datetime
from typing import List, Optional

from dateutil import parser

from .accessories.open_dataset_base import OpenDatasetBase


class NycTaxiBase(OpenDatasetBase):
    """New York Taxi class - this is a parent class that can be inherited."""

    default_start_date = parser.parse('2015-01-01')
    default_end_date = datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0)

    def __init__(
            self,
            start_date: datetime = default_start_date,
            end_date: datetime = default_end_date,
            cols: Optional[List[str]] = None,
            limit: Optional[int] = -1,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param start_date: The start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: The end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: A list of column names you'd like to retrieve. None will get all columns.
        :type cols: Optional[List[str]]
        :param limit: to_pandas_dataframe() will load only "limit" months of data. -1 means no limit.
        :type limit: int
        :param enable_telemetry: Indicates whether to send telemetry.
        :type enable_telemetry: bool
        """
        super(NycTaxiBase, self).__init__(
            cols,
            enable_telemetry,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
