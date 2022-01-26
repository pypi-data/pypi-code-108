from collections import defaultdict
from typing import List
from syncer import sync

from betterproto import Casing
from pandas import DataFrame
from unacatlib.unacast.maps.v1 import Feature as v1_Feature, Layer as v1_Layer, \
    AddressComponent as v1_AddressComponent, AddressComponentValue as v1_AddressComponentValue

from .address_component import AddressComponent
from .filter import Filter
from .index_job import IndexJob

class Layer(object):

    def __init__(self, catalog, layer_value: v1_Layer, f: Filter = Filter()):
        self._catalog = catalog
        self._layer = layer_value
        self._filter = f
        self._map_operator_service = catalog._client.map_operator_service

    @property
    def name(self):
        return self._layer.display_name

    @property
    def id(self):
        return self._layer.id

    def __str__(self):
        return str(self._layer.to_dict(casing=Casing.SNAKE))

    def to_dict(self):
        return self._layer.to_dict()

    def with_filter(self, f: Filter) -> 'Layer':
        return Layer(self._catalog, self._layer, f)

    def features(self) -> DataFrame:
        layer_features: List[v1_Feature] = self._catalog.client.query_layer(self._catalog.id, self.id, self._filter)

        address_component_column_names = {}
        ad: v1_AddressComponent
        for ad in self._layer.address_components:
            address_component_column_names[ad.component] = ad.short_name.lower().strip().replace(" ", "")

        dataframe_dict = defaultdict(list)
        for lf in layer_features:
            components: List[v1_AddressComponentValue] = lf.address_components
            dataframe_dict['feature_id'].append(lf.feature_id)
            dataframe_dict['name'].append(lf.name)
            dataframe_dict['geo'].append(lf.geo)
            for c in components:
                dataframe_dict[address_component_column_names[c.component]].append(c.value)

        return DataFrame.from_dict(dataframe_dict)

    def list_address_components(self) -> List[AddressComponent]:
        return [AddressComponent(self._catalog, ac) for ac in self._layer.address_components]

    def address_component(self, component: str) -> AddressComponent:
        components = [c for c in self.list_address_components() if c.component == component]
        if len(components) != 1:
            raise RuntimeError('AddressComponent {} not found'.format(component))
        return components[0]

    def as_address_component(self) -> AddressComponent:
        return self.address_component(self.id)

    def index(self, big_query_table_id: str) -> 'Layer': 

        res = sync(self._map_operator_service.index_layer(layer_id=self.id, big_query_table_id=big_query_table_id))

        return IndexJob(self._catalog, res.job_id)
