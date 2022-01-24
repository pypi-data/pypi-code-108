# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""City crime."""

from datetime import datetime
from typing import List, Optional

from dateutil import parser

from .accessories.open_dataset_base import OpenDatasetBase


class CitySafety(OpenDatasetBase):
    """City safety class - this is a parent class that can be inherited by each individual city."""

    default_start_date = parser.parse('2001-01-01')
    default_end_date = datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0)

    def __init__(
            self,
            start_date: datetime = default_start_date,
            end_date: datetime = default_end_date,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: Optional[List[str]]
        :param enable_telemetry: whether to send telemetry
        :type enable_telemetry: bool
        """
        super(CitySafety, self).__init__(
            cols,
            enable_telemetry,
            start_date=start_date,
            end_date=end_date
        )
