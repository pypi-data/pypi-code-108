from unacatlib.unacast.catalog.v1 import Catalog as v1_Catalog

from .metric import Metric
from .layer import Layer
from .layer_builder import LayerBuilder
from .address_component_builder import AddressComponentBuilder
from .metric_builder import MetricBuilder
from .address_component import AddressComponent
from .dimension_builder import DimensionBuilder
from .dimension import Dimension

class Catalog(object):

    def __init__(self, client, catalog_value: v1_Catalog):
        self._client = client
        self._catalog = catalog_value

    @property
    def id(self):
        return self._catalog.id

    @property
    def client(self):
        return self._client

    def __str__(self):
        return self.id

    def list_metrics(self):
        metrics = self._client.list_metrics(catalog_id=self._catalog.id)

        return [Metric(self, metric) for metric in metrics]

    def list_address_components(self):
        address_components = self._client.list_address_components(self.id)
        return [AddressComponent(ac) for ac in address_components]

    
    def list_dimensions(self):
        dimensions = self._client.list_dimensions(self.id)
        return [Dimension(self, dimension) for dimension in dimensions]

    def metric(self, metric_id: str) -> Metric:
        metric = self._client.get_metric(catalog_id=self._catalog.id, metric_id=metric_id)
        return Metric(self, metric)

    def layer(self, layer_id: str) -> Layer:
        layer = self._client.get_layer(catalog_id=self._catalog.id, layer_id=layer_id)
        return Layer(self, layer)

    def dimension(self, dimension_id: str) -> Dimension:
        dimension = self._client.get_dimension(catalog_id=self._catalog.id, dimension_id=dimension_id)
        return Dimension(self, dimension)

    def address_component(self, component: str) -> AddressComponent:
        address_components = self._client.list_address_components(self.id)

        for ac in address_components:
            if ac.component == component:
                return AddressComponent(self, ac)

    def build_layer(self, given_id: str) -> LayerBuilder:
        return LayerBuilder(self, given_id)

    def build_address_component(self, component: str) -> AddressComponentBuilder:
        return AddressComponentBuilder(self, component)
    
    def build_metric(self, given_id: str) -> MetricBuilder:
        return MetricBuilder(self, given_id)
    
    def build_dimension(self, dimension_id: str) -> DimensionBuilder:
        return DimensionBuilder(self, dimension_id)
