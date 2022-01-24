# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for enriching custom data with holiday public data."""

from typing import List, Tuple

from azureml.telemetry.activity import ActivityType

from ..accessories._loggerfactory import _LoggerFactory
from ..accessories.customer_data import CustomerData
from ..accessories.public_data import PublicData
from ..aggregators.aggregator import Aggregator
from ..aggregators.aggregator_all import AggregatorAll
from ..environ import PandasEnv
from ..selectors.country_region_selector import EnricherCountryRegionSelector
from ..selectors.enricher_selector import (EnricherLocationSelector,
                                           EnricherTimeSelector)
from ..selectors.time_nearest_selector import TimeNearestSelector
from .enricher import Enricher


class HolidayEnricher(Enricher):
    """Defines a common holiday enricher.

    The HolidayEnricher class can be used to join holiday public data with your data. For example, see
    the `Public Holidays <https://azure.microsoft.com/services/open-datasets/catalog/public-holidays/>`__
    dataset in the Open Datasets catalog.

    :param public_data_object: A public dataset.
    :type public_data_object: azureml.opendatasets.accessories.public_data.PublicData
    :param enable_telemetry: Indicates whether to send telemetry.
    :type enable_telemetry: bool
    """

    def __init__(self, public_data_object: PublicData, enable_telemetry: bool = False):
        """Intialize with public data object."""
        self.public_data = public_data_object
        super(HolidayEnricher, self).__init__(
            enable_telemetry=enable_telemetry)

    def enrich_customer_data_with_agg(
        self,
        customer_data_object: CustomerData,
        agg: str,
        time_round_granularity: str = 'day')\
            -> Tuple[
                CustomerData,
                List[Tuple[str, str]]]:
        """
        Enrich customer data with specified aggregator.

        :param customer_data_object: An instance of a customer data class.
        :type customer_data_object: azureml.opendatasets.accessories.customer_data.CustomerData
        :param agg: An aggregator.
        :type agg: azureml.opendatasets.aggregators.aggregator.Aggregator
        :param time_round_granularity: A time granularity, 'hour', 'day', or 'month'. The default is 'day'.
        :type time_round_granularity: str
        :return: A tuple of enriched customer data (joined_data).
        :rtype: tuple
        """
        if self.enable_telemetry:
            self.log_properties['parameters'] = \
                'agg: %s, time_gran: %s' % (agg, time_round_granularity)
            self.log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'enrich_customer_data_with_agg', **self.log_properties)
            _, _, joined_data, _ = self._enrich_customer_data(
                customer_data_object, time_round_granularity, agg)
            return joined_data
        else:
            _, _, joined_data, _ = self._enrich_customer_data(
                customer_data_object, time_round_granularity, agg)
            return joined_data

    def enrich_customer_data_no_agg(
        self,
        customer_data_object: CustomerData,
        time_round_granularity: str = 'day')\
            -> Tuple[
                CustomerData,
                PublicData,
                List[Tuple[str, str]]]:
        """
        Enrich customer data with default aggregator_all.

        :param customer_data_object: An instance of a customer data class.
        :type customer_data_object: azureml.opendatasets.accessories.customer_data.CustomerData
        :param time_round_granularity: The time granularity, 'day', 'hour', or 'month'. The default is 'day'.
        :type time_round_granularity: str
        :return: A tuple of enriched customer data (new_customer_data) and processed_public_data.
        :rtype: tuple
        """
        if self.enable_telemetry:
            self.log_properties['parameters'] = \
                'time_gran: %s' % (time_round_granularity)
            new_customer_data, processed_public_data, _, _ = \
                self._enrich_customer_data(
                    customer_data_object, time_round_granularity, 'all')
            self.log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'enrich_customer_data_no_agg', **self.log_properties)
            return new_customer_data, processed_public_data
        else:
            new_customer_data, processed_public_data, _, _ = \
                self._enrich_customer_data(
                    customer_data_object, time_round_granularity, 'all')
            return new_customer_data, processed_public_data

    def _enrich_customer_data(
            self,
            customer_data_object: CustomerData,
            time_round_granularity: str = 'day',
            agg_strategy: str = 'all'):
        """
        Enrich customer data with a specified aggregator.

        :param customer_data_object: An instance of a customer data class.
        :type customer_data_object: azureml.opendatasets.accessories.customer_data.CustomerData
        :param time_round_granularity: The time granularity, 'day', 'hour', or 'month'.
        :type time_round_granularity: str
        :return: A tuple of: a new instance of class customer_data, unchanged instance of public_data,
            a new joined instance of class customer_data, and join keys (list of tuple)).
        :rtype: tuple
        """
        self.public_data.env = customer_data_object.env
        if type(self.public_data.env) == PandasEnv:
            error_msg = 'Unsupported Dataframe in CustomerData.data: PandasDataframe, ' + \
                'only spark Dataframe is supported in PublicHolidays enricher for now.'
            raise ValueError(error_msg)
        self.time_granularity = self._get_time_granularity(
            time_round_granularity)
        if self.time_granularity is None:
            raise ValueError('Unsupported time granularity' + time_round_granularity)
        self.time_selector = TimeNearestSelector(self.time_granularity)

        self.countryregion_selector = EnricherCountryRegionSelector()

        self.aggregator = self._get_aggregator(agg_strategy)
        if self.aggregator is None or agg_strategy == 'avg':
            raise ValueError('Unsupported aggregator ' + agg_strategy + ' for PublicHolidays enricher.')

        return self.enrich(
            customer_data=customer_data_object,
            public_data=self.public_data,
            location_selector=self.countryregion_selector,
            time_selector=self.time_selector,
            aggregator=self.aggregator)

    def _process(
            self,
            customer_data: CustomerData,
            public_data: PublicData,
            location_selector: EnricherLocationSelector,
            time_selector: EnricherTimeSelector,
            aggregator: Aggregator)\
            -> Tuple[
                CustomerData,
                PublicData,
                CustomerData,
                List[Tuple[str, str]]]:
        """Process based on wrapped customer and public data objects."""
        all_aggregator = AggregatorAll()
        local_customer_data, location_filtered_public_data, join_keys =\
            location_selector.process(
                public_data.env,
                customer_data,
                public_data,
                all_aggregator,
                [],
                self.debug)

        if self.debug:
            self.location_filtered_customer_dataset = local_customer_data.data
            self.location_filtered_public_dataset = location_filtered_public_data.data

        location_filtered_public_data.data.cache()

        local_customer_data, time_filtered_public_data, join_keys =\
            time_selector.process(
                public_data.env,
                local_customer_data,
                location_filtered_public_data,
                aggregator,
                join_keys,
                self.debug)

        if self.debug:
            self.time_filtered_customer_dataset = local_customer_data.data
            self.time_filtered_public_dataset = time_filtered_public_data.data

        return aggregator.process(
            public_data.env,
            local_customer_data,
            time_filtered_public_data,
            join_keys,
            self.debug)
