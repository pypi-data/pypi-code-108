# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains granularity definitions for time and location.

The granularities are organized as follows:

* :class:`azureml.opendatasets.granularities.granularity.LocationGranularity`
    * :class:`azureml.opendatasets.granularities.granularity.LocationClosestGranularity`
* :class:`azureml.opendatasets.granularities.granularity.TimeGranularity`
    * :class:`azureml.opendatasets.granularities.granularity.HourGranularity`
    * :class:`azureml.opendatasets.granularities.granularity.DayGranularity`
    * :class:`azureml.opendatasets.granularities.granularity.MonthGranularity`

You work with a granularity by specifying it in an enricher function. For example, when using
the :class:`azureml.opendatasets.enrichers.holiday_enricher.HolidayEnricher` class
methods to enrich data, specify the
:class:`azureml.opendatasets.granularities.granularity.TimeGranularity` as an input parameter
to the method.
"""


class Granularity:
    """Defines the base granularity class."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None


class LocationGranularity(Granularity):
    """Defines the base location granularity."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None


class LocationClosestGranularity(LocationGranularity):
    """Defines a closest location granularity.

    ``_cord_count`` is the count of customer data after duplicates are dropped. If it's bigger
    than ``_cord_limit``, the ``_lower_fuzzy_boundary`` is used to do the rough
    filtering, otherwise, ``_upper_fuzzy_boundary`` is used.

    All possible locations will be ranked by spherical distance of two
    locations, the ``_closest_top_n`` are selected to do further joins.

    :param _cord_limit: The count of customer data after dropping duplicates. The default is 5.
    :type _cord_limit: int
    :param _lower_fuzzy_boundary: Lower bound for filtering. The default is 2
    :type _lower_fuzzy_boundary: int
    :param _upper_fuzzy_boundary: Upper bound for filtering. The default is 5
    :type _upper_fuzzy_boundary: int
    :param _closest_top_n: How many of the top matches to consider closest. The default is 1.
        The bigger the value, the more time cost.
    :type _closest_top_n: int
    """

    def __init__(
            self,
            _cord_limit=5,
            _lower_fuzzy_boundary=2,
            _upper_fuzzy_boundary=5,
            _closest_top_n=1):
        """
        Initialize with various configs.

        cord_count is the count of customer_data after dropDuplicates(), if it's
        bigger than _cord_limit, we'll use _lower_fuzzy_boundary to do the rough
        filtering, otherwise, use _upper_fuzzy_boundary.
        all possible locations will be ranked by spherical distance of two
        locations, we'll select _closest_top_n to do further join.

        :param _cord_limit: default is 5
        :param _lower_fuzzy_boundary: default is 2
        :param _upper_fuzzy_boundary: default is 5
        :param _closest_top_n: default is 1, the bigger, the more time cost.
        """
        self.cord_limit = _cord_limit
        self.lower_fuzzy_boundary = _lower_fuzzy_boundary
        self.upper_fuzzy_boundary = _upper_fuzzy_boundary
        self.closest_top_n = _closest_top_n

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('ClosestN', self.closest_top_n)


class TimeGranularity(Granularity):
    """Defines the base class for time granularity."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None


class HourGranularity(TimeGranularity):
    """Defines a time granularity of hour."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('TimeGran', 'hour')


class DayGranularity(TimeGranularity):
    """Defines a time granularity of day."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('TimeGran', 'day')


class MonthGranularity(TimeGranularity):
    """Defines a time granularity of month."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('TimeGran', 'month')
