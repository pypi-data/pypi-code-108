# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Contains the base classes for location and time selectors.

There are two subclasses of EnricherSelector:

* :class:`azureml.opendatasets.selectors.enricher_selector.EnricherLocationSelector` - provides basic
  calculations of spherical distance.

* :class:`azureml.opendatasets.selectors.enricher_selector.EnricherTimeSelector` - provides ``round_to``
  wrapper functions.

The :class:`azureml.opendatasets.selectors.enricher_selector.EnricherSelector` is the root class of
:class:`azureml.opendatasets.selectors.location_closest_selector.LocationClosestSelector` and
:class:`azureml.opendatasets.selectors.time_nearest_selector.TimeNearestSelector`.
"""

from math import atan2, cos, radians, sin, sqrt
from typing import List, Tuple, Union

from dateutil.relativedelta import relativedelta

from .._utils.telemetry_utils import get_run_common_properties
from ..accessories.time_data import TimeData
from ..aggregators.aggregator import Aggregator
from ..granularities.granularity import (DayGranularity, Granularity,
                                         HourGranularity, MonthGranularity)


class EnricherSelector:
    """Defines the base class of all enricher selectors.

    .. remarks::

        Use the ``granularity`` property to set the granularity of an enricher.

        .. code-block:: python

            EnricherSelector.granularity = DayGranularity()

    """

    @property
    def granularity(self) -> Granularity:
        """Get granularity."""
        return self.__granularity

    @granularity.setter
    def granularity(self, value: Granularity):
        """Set granularity."""
        self.__granularity = value

    def process(
            self,
            customer_data: TimeData,
            public_data: TimeData,
            aggregator: Aggregator,
            join_keys: List[Tuple[str, str]] = None,
            debug: bool = False):
        """Process the enricher selector.

        :param customer_data: An instance of a TimeData dervived class.
        :type customer_data: azureml.opendatasets.accessories.time_data.TimeData
        :param public_data: An instance of a TimeData derived class.
        :type public_data: azureml.opendatasets.accessories.time_data.TimeData
        :param aggregator: An aggregator.
        :type aggregator: azureml.opendatasets.aggregators.aggregator.Aggregator
        :param join_keys: A list of join key pairs.
        :type join_keys: builtin.list
        :param debug: Indicates whether to print debug logs.
        :type debug: bool
        :return: A tuple of altered customer data class instance, altered public data class instance, and
            a list of join key pairs.
        :rtype: tuple
        """
        pass

    def _get_common_log_properties(self):
        """Get common log properties."""
        return get_run_common_properties()


class EnricherLocationSelector(EnricherSelector):
    """Defines base location calculations for location enricher selectors.

    Location calculation methods are static member functions.
    """

    # get distance between two lat long pairs
    @staticmethod
    def get_distance(lon1, lat1, lon2, lat2) -> float:
        """
        Calculate the spherical distance between two points specified by a longitude and latitude.

        :param lon1: Longitude of point 1.
        :type lon1: float
        :param lat1: Latitude of point 1.
        :type lat1: float
        :param lon2: Longitude of point 2.
        :type lon2: float
        :param lat2: Latitude of point 2.
        :type lat2: float
        :return: The spherical distance between the two points.
        :rtype: float
        """
        # Constants
        R = 6373.0

        if (lon1 is None or lat1 is None or lon2 is None or lat2 is None):
            return R

        lat1 = radians(float(lat1))
        lon1 = radians(float(lon1))
        lat2 = radians(float(lat2))
        lon2 = radians(float(lon2))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    # find if 2 latlong pair is within 10 lat/long of each other
    @staticmethod
    def close_to(lon1, lat1, lon2, lat2) -> bool:
        """
        Check whether given two points are close enough.

        Differences of latitude and longitude both less than 10 degrees return True.

        :param lon1: Longitude of point 1.
        :type long1: float
        :param lat1: Latitude of point 1.
        :type lat1: float
        :param lon2: Longitude of point 2.
        :type lon2: float
        :param lat2: Latitude of point 2.
        :type lat2: float
        :return: Return True if the two points are close.
        :rtype: float
        """
        if (lon1 is None or lat1 is None or lon2 is None or lat2 is None):
            return False

        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

        if abs(lat2 - lat1) > 10:
            return False

        if 10 < abs(lon1 - lon2) < 350:
            return False

        return True


class EnricherTimeSelector(EnricherSelector):
    """Defines time-related base calculations for time enricher selectors.

    .. remarks::

        Time calculation methods are static member functions: ``round_to(granularity)`` where granularity is
        one of :class:`azureml.opendatasets.granularities.granularity.MonthGranularity`,
        :class:`azureml.opendatasets.granularities.granularity.DayGranularity`, or
        :class:`azureml.opendatasets.granularities.granularity.HourGranularity`.
    """

    def round_to(self, g: Union[HourGranularity, DayGranularity, MonthGranularity]):
        """Round to granularity."""
        if isinstance(g, HourGranularity):
            def round_to_hour(time):
                try:
                    t = time + relativedelta(minutes=30)
                    return t.replace(second=0, microsecond=0, minute=0)
                except Exception:
                    return time
            return round_to_hour
        elif isinstance(g, DayGranularity):
            def round_to_day(time):
                try:
                    return time.replace(second=0, microsecond=0, minute=0, hour=0)
                except Exception:
                    return time
            return round_to_day
        elif isinstance(g, MonthGranularity):
            def round_to_month(time):
                try:
                    return time.replace(second=0, microsecond=0, minute=0, hour=0, day=1)
                except Exception:
                    return time
            return round_to_month
