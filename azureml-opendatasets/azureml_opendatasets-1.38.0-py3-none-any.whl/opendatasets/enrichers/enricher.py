# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the generic enricher class for joining together data with different granularity and aggregators.

This module contains static function overloads: ``get_max_date_by_granularity(max_date, granularity)``
where granularity is one of :class:`azureml.opendatasets.granularities.granularity.MonthGranularity`,
:class:`azureml.opendatasets.granularities.granularity.DayGranularity`, or
:class:`azureml.opendatasets.granularities.granularity.HourGranularity`. These static methods
return the max data based on the specified granularity.
"""

from typing import List, Optional, Tuple, Union

from azureml.telemetry.activity import ActivityType
from dateutil.relativedelta import relativedelta

from .._utils.telemetry_utils import get_run_common_properties
from ..accessories._loggerfactory import _LoggerFactory
from ..accessories.customer_data import CustomerData
from ..accessories.public_data import PublicData
from ..aggregators.aggregator import Aggregator
from ..aggregators.aggregator_all import AggregatorAll
from ..aggregators.aggregator_avg import AggregatorAvg
from ..aggregators.aggregator_max import AggregatorMax
from ..aggregators.aggregator_min import AggregatorMin
from ..aggregators.aggregator_top import AggregatorTop
from ..granularities.granularity import (DayGranularity, HourGranularity,
                                         MonthGranularity, TimeGranularity)
from ..selectors.enricher_selector import (EnricherLocationSelector,
                                           EnricherTimeSelector)


def get_max_date_by_granularity(max_date, _granularity: Union[HourGranularity, DayGranularity, MonthGranularity]):
    """Get the max date based on hour granularity."""
    if isinstance(_granularity, HourGranularity):
        return max_date + relativedelta(hours=1)
    elif isinstance(_granularity, DayGranularity):
        return max_date + relativedelta(days=1)
    elif isinstance(_granularity, MonthGranularity):
        return max_date + relativedelta(months=1)


class Enricher:
    """Defines the base enricher class.

    :param enable_telemetry: Indicates whether to send telemetry.
    :type enable_telemetry: bool
    """

    debug = False

    def __init__(self, enable_telemetry: bool = False):
        """Initialize a new instance.

        :param enable_telemetry: Indicates whether to send telemetry.
        :type enable_telemetry: bool
        """
        self.enable_telemetry = enable_telemetry
        if self.enable_telemetry:
            self.log_properties = self._get_common_log_properties()

    def _get_time_granularity(self, _granularity: str)\
            -> Optional[TimeGranularity]:
        """Get time granularity instance."""
        if _granularity.lower() == 'hour':
            return HourGranularity()
        elif _granularity.lower() == 'day':
            return DayGranularity()
        elif _granularity.lower() == 'month':
            return MonthGranularity()
        return None

    def _get_aggregator(self, name: str) -> Optional[Aggregator]:
        """Get aggregator instance."""
        if name.lower() == 'all':
            return AggregatorAll()
        elif name.lower() == 'avg':
            return AggregatorAvg()
        elif name.lower() == 'max':
            return AggregatorMax()
        elif name.lower() == 'min':
            return AggregatorMin()
        elif name.lower() == 'top':
            return AggregatorTop()
        return None

    def enrich(
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
        """
        Enrich customer data with public data by applying selectors and an aggregator.

        :param customer_data: An instance of a customer data derived class.
        :type customer_data: azureml.opendatasets.accessories.customer_data.CustomerData
        :param public_data: An instance of a public data derived class.
        :type public_data: azureml.opendatasets.accessories.public_data.PublicData
        :param location_selector: An instance of an enricher location selector derived class.
        :type location_selector: azureml.opendatasets.selectors.enricher_selector.EnricherLocationSelector
        :param time_selector: An instance of an enricher time selector derived class.
        :type time_selector: azureml.opendatasets.selectors.enricher_selector.EnricherTimeSelector
        :param aggregator: An instance of an aggregator derived class.
        :type aggregator: azureml.opendatasets.aggregators.aggregator.Aggregator
        :return: A tuple of: (
            a new instance of class ``customer_data``,
            unchanged instance of ``public_data``,
            a new joined instance of class ``customer_data``,
            join keys (list of tuple))
        :rtype: tuple
        """
        if self.enable_telemetry:
            self.log_properties['RegistryId'] = public_data.registry_id
            location_gran_log_property = location_selector.granularity.get_log_property()
            if location_gran_log_property is not None and len(location_gran_log_property) == 2:
                self.log_properties[location_gran_log_property[0]] = \
                    location_gran_log_property[1]
            time_gran_log_property = time_selector.granularity.get_log_property()
            if time_gran_log_property is not None and len(time_gran_log_property) == 2:
                self.log_properties[time_gran_log_property[0]] = \
                    time_gran_log_property[1]
            agg_log_property = aggregator.get_log_property()
            if agg_log_property is not None and len(agg_log_property) == 2:
                self.log_properties[agg_log_property[0]] = \
                    agg_log_property[1]
            self.log_properties['ActivityType'] = ActivityType.INTERNALCALL
            _LoggerFactory.log_event('enrich', **self.log_properties)
            return self._enrich(
                customer_data,
                public_data,
                location_selector,
                time_selector,
                aggregator,
                None)
        else:
            return self._enrich(
                customer_data,
                public_data,
                location_selector,
                time_selector,
                aggregator,
                None)

    def _enrich(
            self,
            customer_data: CustomerData,
            public_data: PublicData,
            location_selector: EnricherLocationSelector,
            time_selector: EnricherTimeSelector,
            aggregator: Aggregator,
            activity_logger):
        """Enrich method, internal to override."""
        max_date = get_max_date_by_granularity(
            customer_data.max_date, time_selector.granularity)
        public_data.data = public_data.filter(
            public_data.env, customer_data.min_date, max_date)
        customer_data.add_row_id(customer_data.env)
        return self._process(customer_data, public_data, location_selector, time_selector, aggregator)

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

    def _get_common_log_properties(self):
        """Get common log properties."""
        return get_run_common_properties()
