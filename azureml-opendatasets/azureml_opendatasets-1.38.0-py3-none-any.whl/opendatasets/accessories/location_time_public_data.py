# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for wrapping public data with location and time columns."""

from .location_data import LocationData
from .public_data import PublicData
from .time_data import TimePublicData

from typing import List, Optional


class LocationTimePublicData(LocationData, TimePublicData):
    """Defines a class wrapper for public data which contains both location column and time column."""

    def __init__(self, cols: Optional[List[str]], enable_telemetry: bool = True):
        """
        Initialize with columns.

        :param cols: The column name list which the user wants to enrich from public data.
        :type cols: builtin.list
        :param enable_telemetry: Indicates whether to send telemetry.
        :type enable_telemetry: bool
        """
        PublicData.__init__(self, cols, enable_telemetry=enable_telemetry)
