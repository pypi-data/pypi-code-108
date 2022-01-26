import datetime
import typing
from pandas import DataFrame

from unacatlib.unacast.maps.v1 import AddressComponentFilter
from unacatlib.unacast.metric.v1 import Period, DimensionFilter
from unacatlib.unacast.unatype import Date


class Filter(object):

    def __init__(self):
        self._address_component_filters: [AddressComponentFilter] = []
        self._feature_filters: [str] = []
        self._period_filter: typing.Optional[Period] = None
        self._dimension_filters: [DimensionFilter] = []

    @property
    def address_component_filters(self):
        return self._address_component_filters

    @property
    def feature_filters(self):
        return self._feature_filters

    @property
    def period_filter(self):
        return self._period_filter

    @property
    def dimension_filters(self):
        return self._dimension_filters

    def with_address_component(self, component: str, filter_values: list):
        component_filter: AddressComponentFilter = AddressComponentFilter(component=component, values=filter_values)
        self._address_component_filters.append(component_filter)
        return self

    def with_address_component_search(self, address_component: 'AddressComponent', query: str, print_result: bool = False):
        """Return a Filter

        Take the first result of a AddressComponent Value Search where query is the input.

        print_result let's you inspect what the first result is
        """
        
        search_result = address_component.search(query)
        first_hit = search_result.iloc[0]
        if print_result:
            print(first_hit)
        component_filter: AddressComponentFilter = AddressComponentFilter(component=first_hit["component"], values=[first_hit["value"]])
        self._address_component_filters.append(component_filter)
        return self

    def with_period_filter(self, start: datetime.date, end: datetime.date):
        period_filter = Period(
            start=Date(year=start.year, month=start.month, day=start.day),
            end=Date(year=end.year, month=end.month, day=end.day),
        )
        self._period_filter = period_filter
        return self

    def with_point_in_time(self, point_in_time: datetime.date):
        return self.with_period_filter(start=point_in_time, end=point_in_time)

    def with_feature_filter(self, feature_id: str):
        self._feature_filters = [feature_id]
        return self

    def with_dimension_filter(self, dimension: str, value: str):
        dimension_filter: DimensionFilter = DimensionFilter(dimension_id=dimension, values=[value])
        self._dimension_filters.append(dimension_filter)
        return self
