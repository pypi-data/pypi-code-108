# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The class to hold the column types, used for aggregation."""
from typing import Any, Set


class ColumnTypeAggDetectionResult(object):
    """
    The class to held the column types for the purpose of frequency aggregation.

    :param numeric_columns: The numeric columns.
    :param date_columns: The date columns.
    :param categoric_columns: The categorical columns.
    :param detection_failed: If true, the columns were not aggregated by frequency aggregator.
    """

    def __init__(self,
                 numeric_columns: Set[Any],
                 date_columns: Set[Any],
                 categoric_columns: Set[Any],
                 detection_failed: bool
                 ) -> None:
        """
        Constructor.

        :param numeric_columns: The numeric columns.
        :param date_columns: The date columns.
        :param categoric_columns: The categorical columns.
        :param detection_failed: If true, the columns were not aggregated by frequency aggregator.
        """
        self._numeric_columns = numeric_columns
        self._date_columns = date_columns
        self._categoric_columns = categoric_columns
        self._detection_failed = detection_failed

    @property
    def numeric_columns(self) -> Set[Any]:
        """Return the numeric columns if any."""
        return self._numeric_columns

    @property
    def date_columns(self) -> Set[Any]:
        """Return date columns if any."""
        return self._date_columns

    @property
    def categoric_columns(self) -> Set[Any]:
        """Return categorical columns if any."""
        return self._categoric_columns

    @property
    def detection_failed(self) -> bool:
        """Return True if the data were not aggregated by the frequency aggregator."""
        return self._detection_failed
