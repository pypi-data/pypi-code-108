from collections import defaultdict

from betterproto import Casing
from pandas import DataFrame

from unacastclient.unacast.maps.v1 import AddressComponent as v1_AddressComponent, \
    AddressComponentValue as v1_AddressComponentValue


class AddressComponent(object):

    def __init__(self, catalog, address_comp_value: v1_AddressComponent):
        self._catalog = catalog
        self._address_component = address_comp_value

    @property
    def component(self):
        return self._address_component.component

    @property
    def name(self):
        return self._address_component.short_name

    @property
    def kind(self):
        return self._address_component.kind

    def __str__(self):
        ac_dict = self._address_component.to_dict(casing=Casing.SNAKE)
        d = {key: ac_dict.get(key) for key in ['component', 'short_name', 'display_name']}
        return str(d)

    def search(self, query: str) -> DataFrame:
        ac_values = self._catalog.client.search_address_component_values(self._catalog.id, self.component, query)

        dataframe_dict = defaultdict(list)
        acv: v1_AddressComponentValue
        for acv in ac_values:
            dataframe_dict['component'].append(acv.component)
            dataframe_dict['value'].append(acv.value)
            dataframe_dict['short_name'].append(acv.short_name)
            dataframe_dict['display_name'].append(acv.display_name)

        return DataFrame.from_dict(dataframe_dict)