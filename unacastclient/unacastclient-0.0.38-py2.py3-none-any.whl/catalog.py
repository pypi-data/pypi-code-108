from unacastclient.unacast.catalog.v1 import Catalog as v1_Catalog
from .address_component import AddressComponent
from .dimension import Dimension
from .layer import Layer
from .metric import Metric


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
        metrics = [Metric(self, metric) for metric in metrics]
        return [x.id for x in metrics]

    def search_metrics(self, query: str):
        metrics = self._client.list_metrics(catalog_id=self._catalog.id)

        result = []
        metrics = [Metric(self, metric) for metric in metrics]
        for m in metrics:
            if query.lower() in m.id.lower() or query.lower() in m.name.lower():
                result.append(m.to_dict()['id'])

        return result

    def list_address_components(self):
        address_components = self._client.list_address_components(self.id)
        return [AddressComponent(ac) for ac in address_components]

    def list_dimensions(self):
        dimensions = self._client.list_dimensions(self.id)
        return [Dimension(self, dimension) for dimension in dimensions]

    def metric(self, metric_id: str) -> Metric:
        metric_response = self._client.get_metric(catalog_id=self._catalog.id, metric_id=metric_id)
        return Metric(self, metric_response.metric, period=metric_response.complete_observation_period)

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
