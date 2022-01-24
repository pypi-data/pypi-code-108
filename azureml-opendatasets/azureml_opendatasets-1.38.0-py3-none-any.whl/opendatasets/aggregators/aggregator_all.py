# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the the aggregator for including all columns, that is, when no aggregation is performed."""

from .aggregator import Aggregator


class AggregatorAll(Aggregator):
    """Define an aggregator that returns all columns.

    Use this aggregator when you want to include all columns with no aggregation.
    """

    def __init__(self):
        """Initialize with should_direct_join as False."""
        self.should_direct_join = False

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('Aggregator', 'all')
