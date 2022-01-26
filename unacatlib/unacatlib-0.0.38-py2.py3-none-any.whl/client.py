from typing import List

from grpclib.client import Channel
from halo import Halo
from syncer import sync
from unacatlib.unacast.catalog.v1 import CatalogServiceStub, SearchMetricValuesResponse, \
    SearchAddressComponentValuesResponse, SearchLayerFeaturesResponse, SearchDimensionValuesResponse
from unacatlib.unacast.catalog.v1 import QueryServiceStub
from unacatlib.unacast.operator.v1 import MapOperatorServiceStub, AddressComponentOperatorServiceStub, \
    MetricOperatorServiceStub, DimensionOperatorServiceStub, IndexJobOperatorServiceStub, IndexMetricResponse
from unacatlib.unacast.maps.v1 import Feature, AddressComponentValue, MapServiceStub
from unacatlib.unacast.metric.v1 import MetricValue

from .catalog import Catalog
from .filter import Filter

IndexMetricResponse()
SERVER_ADDRESS = 'dataops-api-server-snr3asztcq-uk.a.run.app'
PORT = 443

HARDCODED_BILLING_ACCOUNT = 'bvcel5223akg00a0m0og'
MAX_NUMBER_OF_VALUES = 100_000
ABSOLUTE_MAX_NUMBER_OF_VALUES = 100_000
PAGE_SIZE = 100
PAGE_SIZE_METRIC_VALUE_SEARCH = 3000
REQUEST_TAGS = {'source': 'unacat-py'}


class Client(object):
    def __init__(self, server_address=SERVER_ADDRESS, port=PORT, token="", billing_account=HARDCODED_BILLING_ACCOUNT,
                 disable_pagination: bool = False):

        metadata = [("authorization", "Bearer " + token)]
        ssl = False
        if server_address.endswith("run.app"):
            ssl = True
            port = 443

        self.channel = Channel(host=server_address, port=port, ssl=ssl)
        self.catalog_service = CatalogServiceStub(self.channel, metadata=metadata)
        self.map_service = MapServiceStub(self.channel, metadata=metadata)
        self.query_service = QueryServiceStub(self.channel, metadata=metadata)
        self.map_operator_service = MapOperatorServiceStub(self.channel, metadata=metadata)
        self.metric_operator_service = MetricOperatorServiceStub(self.channel, metadata=metadata)
        self.address_component_operator_service = AddressComponentOperatorServiceStub(self.channel, metadata=metadata)
        self.dimension_operator_service = DimensionOperatorServiceStub(self.channel, metadata=metadata)
        self.index_job_operator_service = IndexJobOperatorServiceStub(self.channel, metadata=metadata)
        self.billing_account = billing_account
        self._disable_pagination = disable_pagination

    def list_catalogs(self) -> [Catalog]:
        res = sync(self.catalog_service.list_catalogs())
        return [Catalog(self, catalog) for catalog in res.catalogs]

    def catalog(self, catalog_id: str):
        catalogs = [c for c in self.list_catalogs() if c.id == catalog_id]
        if len(catalogs) != 1:
            raise RuntimeError('Catalog {} not found'.format(catalog_id))
        return catalogs[0]

    def list_metrics(self, catalog_id: str):
        res = sync(self.catalog_service.list_metrics(catalog_id=catalog_id, billing_context=self.billing_account,
                                                     page_size=PAGE_SIZE))
        return res.metrics

    def list_address_components(self, catalog_id: str):
        res = sync(self.map_service.list_address_components())

        return [ac for ac in res.address_components if ac.catalog_id == catalog_id]

    def get_metric(self, catalog_id: str, metric_id: str):
        res = sync(self.catalog_service.get_metric(catalog_id=catalog_id, metric_id=metric_id,
                                                   billing_context=self.billing_account))
        return res.metric

    def get_layer(self, catalog_id: str, layer_id: str):
        res = sync(self.catalog_service.get_layer(catalog_id=catalog_id, layer_id=layer_id))
        return res.layer

    def list_dimensions(self, catalog_id: str):
        res = sync(self.dimension_operator_service.list_dimension(catalog_id=catalog_id))

        return [dim for dim in res.dimensions if dim.catalog_id == catalog_id]

    def get_dimension(self, catalog_id: str, dimension_id: str):
        res = sync(self.dimension_operator_service.list_dimension(catalog_id=catalog_id))
        dimensions = [dimension for dimension in res.dimensions if dimension.dimension_id == dimension_id]

        if len(dimensions) != 1:
            raise RuntimeError('Dimension {} not found'.format(dimension_id))
        return dimensions[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()

    # QUERY functions
    @Halo(text='Searching for metric values', spinner='dots')
    def search_metric_values(self, catalog_id: str, metric_id: str, f: Filter,
                             max_nof_values=MAX_NUMBER_OF_VALUES) -> List[MetricValue]:

        return self._search_mv(catalog_id, metric_id, f, max_nof_values)

    def _search_mv(self, catalog_id: str, metric_id: str, f: Filter,
                   max_nof_values: int, page_token: str = None):
        res: SearchMetricValuesResponse = sync(
            self.query_service.search_metric_values(catalog_id=catalog_id,
                                                    metric_id=metric_id,
                                                    billing_context=self.billing_account,
                                                    address_component_filter=f.address_component_filters,
                                                    observation_period_filter=f.period_filter,
                                                    feature_filter=f.feature_filters,
                                                    dimension_filter=f.dimension_filters,
                                                    page_size=PAGE_SIZE_METRIC_VALUE_SEARCH,
                                                    page_token=page_token,
                                                    request_tags=REQUEST_TAGS))
        if self._disable_pagination or res.next_page_token == "":
            return res.values
        self._check_max_nof_values(res, max_nof_values)
        return res.values + self._search_mv(catalog_id, metric_id, f, max_nof_values=max_nof_values,
                                            page_token=res.next_page_token)

    def metric_report(self, catalog_id: str, metric_id: str):
        return sync(
            self.query_service.search_metric_report(
                catalog_id=catalog_id,
                metric_id=metric_id,
                billing_context=self.billing_account,
                track_total_hits=True,
                disable_cardinalities=True,
                disable_percentiles=True
            )
        ).report

    @Halo(text='Querying layer', spinner='dots')
    def query_layer(self, catalog_id: str, layer_id: str, f: Filter, max_nof_values: int = MAX_NUMBER_OF_VALUES) -> \
            List[Feature]:
        return self._query_layer(catalog_id, layer_id, f, max_nof_values)

    def _query_layer(self, catalog_id: str, layer_id: str, f: Filter, max_nof_values: int = MAX_NUMBER_OF_VALUES,
                     page_token: str = None, counter: int = 0) -> List[Feature]:

        # if f.feature_filters or f.period_filter:
        #    print("WARNING! Feature and Period filters don't have any effect when fetching features.")
        res: SearchLayerFeaturesResponse = sync(self.query_service.search_layer_features(catalog_id=catalog_id,
                                                                                         layer_id=layer_id,
                                                                                         address_component_filter=f.
                                                                                         address_component_filters,
                                                                                         page_size=PAGE_SIZE,
                                                                                         page_token=page_token))
        if self._disable_pagination or res.next_page_token == "":
            return res.features
        self._check_max_nof_values(res, max_nof_values)
        return res.features + self._query_layer(catalog_id, layer_id, f, max_nof_values, res.next_page_token,
                                                counter + 1)

    def search_address_component_values(self, catalog_id: str, component: str, query: str,
                                        max_nof_values: int = MAX_NUMBER_OF_VALUES) -> List[AddressComponentValue]:
        return self._search_address_component_values(catalog_id, component, query, max_nof_values)

    def _search_address_component_values(self, catalog_id: str, component: str, query: str,
                                         max_nof_values: int = MAX_NUMBER_OF_VALUES,
                                         page_token: str = None):
        res: SearchAddressComponentValuesResponse = sync(
            self.query_service.search_address_component_values(catalog_id=catalog_id,
                                                               query=query,
                                                               component=component,
                                                               page_size=PAGE_SIZE,
                                                               page_token=page_token))
        if self._disable_pagination or res.next_page_token == "":
            return res.address_component_values
        self._check_max_nof_values(res, max_nof_values)
        return res.address_component_values + self._search_address_component_values(catalog_id, component, query,
                                                                                    max_nof_values,
                                                                                    page_token=res.next_page_token)

    def search_dimension_values(self, catalog_id: str, dimension_id: str, query: str,
                                max_nof_values: int = MAX_NUMBER_OF_VALUES) -> List[AddressComponentValue]:
        return self._search_dimension_values(catalog_id, dimension_id, query, max_nof_values)

    def _search_dimension_values(self, catalog_id: str, dimension_id: str, query: str,
                                 max_nof_values: int = MAX_NUMBER_OF_VALUES,
                                 page_token: str = None):
        res: SearchDimensionValuesResponse = sync(
            self.query_service.search_dimension_values(catalog_id=catalog_id,
                                                       query=query,
                                                       dimension_id=dimension_id,
                                                       page_size=PAGE_SIZE,
                                                       page_token=page_token))
        if self._disable_pagination or res.next_page_token == "":
            return res.dimension_values
        self._check_max_nof_values(res, max_nof_values)
        return res.dimension_values + self._search_dimension_values(catalog_id, dimension_id, query,
                                                                    max_nof_values,
                                                                    page_token=res.next_page_token)

    @staticmethod
    def _check_max_nof_values(res, max_nof_values):
        max_values = min(max_nof_values, ABSOLUTE_MAX_NUMBER_OF_VALUES)
        if res.total_size > max_values:
            raise RuntimeError("The result set is larger than max_nof_values ({} > {}). Adjust filter to reduce "
                               "result size or increase max_nof_values. OBS! Result sets without filtering "
                               "can become very large! The absoulte max is set to {} "
                               "as larger result sets require other integration mechanisms that "
                               "support streaming or multi tenant. Contact Unacast directly "
                               "about options for this.".format(res.total_size, max_values, max_values))
