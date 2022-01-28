import datetime
import typing

from unacastclient.unacast.maps.v1 import AddressComponentFilter, AddressComponent
from unacastclient.unacast.metric.v1 import Period, DimensionFilter
from unacastclient.unacast.unatype import Date
from unacastclient.unacast.catalog.v1 import Catalog as v1_Catalog

from unacastclient.address_component import AddressComponent as AC
class Filter(object):

    def __init__(self, catalog: v1_Catalog = None):
        self._catalog = catalog
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


    def with_address_component_search(self, filter: str, query: str):
        """
        Return a Filter

        Fuzzy search for an AddressComponent Value with a maximum of 50 returned results

        """
        component: AC = AC(catalog=self._catalog, address_comp_value=AddressComponent(filter))
        search_result = component.search(query)
        
        # checks for matches against short_name and display_name 
        matches = search_result[ (search_result['display_name'].str.lower().str.strip().str.contains(query.lower().strip())) \
                                | (search_result['short_name'].str.lower().str.strip().str.contains(query.lower().strip())) ] 

        if len(matches) > 50:
            raise ValueError(f"The search returned more than 50 matches for query: {query} \nUse a more spefic search keyword!")
        
        elif not matches.empty:
            component_filter: AddressComponentFilter = AddressComponentFilter(component=matches["component"].tolist()[0], 
                                                                              values=matches["value"].tolist())
            self._address_component_filters.append(component_filter)
            return self
        else:
            raise ValueError(f"No results found for query: {query}")

    def with_address_component_name(self, filter: str, name: str):
        """
        Return a Filter

        Looks for an exact match and returns the AddressComponent which has the exact value match
        """
        component: AC = AC(catalog=self._catalog, address_comp_value=AddressComponent(filter))
        search_result = component.search(name)
        
        # checks for match against short_name and display_name 
        match = search_result[(search_result['display_name'].str.lower().str.strip() == name.lower().strip()) \
                              | (search_result['short_name'].str.lower().str.strip() == name.lower().strip() )] #use strip because of trailing spaces

        if len(match) > 1:
            raise ValueError(f"The search returned {len(match)} matches. Only 1 match is allowed with this method. \nUse the search method to get the correct search filters")
        
        elif match.empty:
            raise ValueError(f"No results found for query: {name}")
        
        else:
            component_filter: AddressComponentFilter = AddressComponentFilter(component=match["component"].tolist()[0], 
                                                                              values=match["value"].tolist())
            self._address_component_filters.append(component_filter)
            return self

    def with_period_filter(self, start: str, end: str):
        try:
            start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end, '%Y-%m-%d').date()
        except ValueError:
            print("Incorrect data format, should be YYYY-MM-DD")
            raise

        period_filter = Period(
            start=Date(year=start_date.year, month=start_date.month, day=start_date.day),
            end=Date(year=end_date.year, month=end_date.month, day=end_date.day),
        )
        self._period_filter = period_filter
        return self

    def with_feature_filter(self, feature_id: str):
        self._feature_filters = [feature_id]
        return self

    def with_dimension_filter(self, dimension: str, value: str):
        dimension_filter: DimensionFilter = DimensionFilter(dimension_id=dimension, values=[value])
        self._dimension_filters.append(dimension_filter)
        return self