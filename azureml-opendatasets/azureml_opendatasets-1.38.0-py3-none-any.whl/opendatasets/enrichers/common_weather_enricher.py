# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for enriching custom data with weather public data."""

from typing import List, Tuple

from azureml.telemetry.activity import ActivityType

from ..accessories._loggerfactory import _LoggerFactory
from ..accessories.customer_data import CustomerData
from ..accessories.public_data import PublicData
from ..granularities.granularity import (LocationClosestGranularity,
                                         LocationGranularity)
from ..selectors.location_closest_selector import LocationClosestSelector
from ..selectors.time_nearest_selector import TimeNearestSelector
from .enricher import Enricher


class CommonWeatherEnricher(Enricher):
    """Defines a common weather enricher, for GFS forecast and ISD history data.

    `NOAA Global Forecast System (GFS) <https://azure.microsoft.com/services/open-datasets/catalog/
    noaa-global-forecast-system/>`_ weather data and
    `NOAA Integrated Surface Data (ISD) <https://azure.microsoft.com/services/open-datasets/catalog/
    noaa-integrated-surface-data/>`_ historical data are available in the Open Datasets catalog.
    These public datasets can be used to enrich your data.

    :param public_data_object: A public dataset.
    :type public_data_object: azureml.opendatasets.accessories.public_data.PublicData
    :param enable_telemetry: Indicates whether to send telemetry.
    :type enable_telemetry: bool
    """

    def __init__(self, public_data_object: PublicData, enable_telemetry: bool = False):
        """Initialize with public data object.

        :param public_data_object: A public dataset.
        :type public_data_object: azureml.opendatasets.accessories.public_data.PublicData
        :param enable_telemetry: Indicates whether to send telemetry.
        :type enable_telemetry: bool
        """
        self.public_data = public_data_object
        super(CommonWeatherEnricher, self).__init__(
            enable_telemetry=enable_telemetry)

    def _get_location_granularity(self, _granularity: str)\
            -> LocationGranularity:
        """Get location granularity instance."""
        return LocationClosestGranularity(_closest_top_n=_granularity)

    def enrich_customer_data_with_agg(
        self,
        customer_data_object: CustomerData,
        agg: str,
        location_match_granularity: int = 1,
        time_round_granularity: str = 'hour')\
            -> Tuple[
                CustomerData,
                List[Tuple[str, str]]]:
        """
        Enrich customer data with a specified aggregator.

        :param customer_data_object: An instance of a customer data class.
        :type customer_data_object: azureml.opendatasets.accessories.customer_data.CustomerData
        :param agg: An aggregator.
        :type agg: azureml.opendatasets.aggregators.aggregator.Aggregator
        :param location_match_granularity: location_granularity.closest_top_n
        :type location_match_granularity: int
        :param time_round_granularity: time_granularity
        :type time_round_granularity: str
        :return: A tuple of enriched customer data (joined_data)
        :rtype: tuple
        """
        if self.enable_telemetry:
            self.log_properties['runtimeEnv'] = type(
                customer_data_object.env).__name__
            self.log_properties['parameters'] = \
                'agg: %s, location_gran: %d, time_gran: %s' % (
                    agg, location_match_granularity, time_round_granularity)
            self.log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _, _, joined_data, _ = self._enrich_customer_data(
                customer_data_object, location_match_granularity, time_round_granularity, agg)
            _LoggerFactory.log_event(
                'enrich_customer_data_with_agg', **self.log_properties)
            return joined_data
        else:
            _, _, joined_data, _ = self._enrich_customer_data(
                customer_data_object, location_match_granularity, time_round_granularity, agg)
            return joined_data

    def enrich_customer_data_no_agg(
        self,
        customer_data_object: CustomerData,
        location_match_granularity: int = 1,
        time_round_granularity: str = 'hour')\
            -> Tuple[
                CustomerData,
                PublicData,
                List[Tuple[str, str]]]:
        """
        Enrich customer data using the default aggregator_all.

        :param customer_data_object: An instance of a customer data class.
        :type customer_data_object: azureml.opendatasets.accessories.customer_data.CustomerData
        :param location_match_granularity: location_granularity.closest_top_n
        :type location_match_granularity: int
        :param time_round_granularity: Time granularity, 'day', 'hour', or 'month'.
        :type time_round_granularity: str
        :return: A tuple of enriched customer data (new_customer_data), processed_public_data.
        :rtype: tuple
        """
        if self.enable_telemetry:
            self.log_properties['runtimeEnv'] = type(
                customer_data_object.env).__name__
            self.log_properties['parameters'] = \
                'location_gran: %d, time_gran: %s' % (
                    location_match_granularity, time_round_granularity)
            new_customer_data, processed_public_data, _, _ = \
                self._enrich_customer_data(
                    customer_data_object, location_match_granularity, time_round_granularity, 'all')
            self.log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'enrich_customer_data_no_agg', **self.log_properties)
            return new_customer_data, processed_public_data
        else:
            new_customer_data, processed_public_data, _, _ = \
                self._enrich_customer_data(
                    customer_data_object, location_match_granularity, time_round_granularity, 'all')
            return new_customer_data, processed_public_data

    def _enrich_customer_data(
            self,
            customer_data_object: CustomerData,
            location_match_granularity: int = 1,
            time_round_granularity: str = 'hour',
            agg_strategy: str = 'all'):
        """
        Enrich customer data with specified aggregator.

        :param customer_data_object: an instance of customer_data class
        :param location_match_granularity: location_granularity.closest_top_n
        :param time_round_granularity: time_granularity
        :return: a tuple of:
            a new instance of class customer_data,
            unchanged instance of public_data,
            a new joined instance of class customer_data,
            join keys (list of tuple))
        """
        self.public_data.env = customer_data_object.env
        self.time_granularity = self._get_time_granularity(
            time_round_granularity)
        if self.time_granularity is None:
            raise ValueError('Unsupported time granularity' + time_round_granularity)
        self.time_selector = TimeNearestSelector(
            self.time_granularity, enable_telemetry=self.enable_telemetry)

        self.location_granularity = self._get_location_granularity(
            location_match_granularity)
        self.location_selector = LocationClosestSelector(
            self.location_granularity,
            enable_telemetry=self.enable_telemetry)

        self.aggregator = self._get_aggregator(agg_strategy)
        if self.aggregator is None:
            raise ValueError('Unsupported aggregator' + agg_strategy)

        return self.enrich(
            customer_data=customer_data_object,
            public_data=self.public_data,
            location_selector=self.location_selector,
            time_selector=self.time_selector,
            aggregator=self.aggregator)
