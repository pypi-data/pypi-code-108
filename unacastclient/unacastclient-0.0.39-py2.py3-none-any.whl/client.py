from typing import List
from grpclib.exceptions import GRPCError
from grpclib.client import Channel
from halo import Halo
from syncer import sync

from unacastclient.unacast.catalog.v1 import CatalogServiceStub, SearchMetricValuesResponse, \
    SearchAddressComponentValuesResponse, SearchLayerFeaturesResponse, SearchDimensionValuesResponse
from unacastclient.unacast.catalog.v1 import QueryServiceStub
from unacastclient.unacast.subscription.v1 import SubscriptionServiceStub
from unacastclient.unacast.maps.v1 import Feature, AddressComponentValue, MapServiceStub
from unacastclient.unacast.metric.v1 import MetricValue
from unacastclient.unacast.operator.v1 import IndexMetricResponse
from .catalog import Catalog
from .filter import Filter

IndexMetricResponse()
SERVER_ADDRESS = 'unacat-api-grpc-server-snr3asztcq-uk.a.run.app'
PORT = 443

UNACAST_BILLING_ACCOUNT = 'bvcel5223akg00a0m0og'
MAX_NUMBER_OF_VALUES = 100_000
ABSOLUTE_MAX_NUMBER_OF_VALUES = 100_000
PAGE_SIZE = 100
PAGE_SIZE_METRIC_VALUE_SEARCH = 3000
REQUEST_TAGS = {'source': 'unacat-py'}


class _Client(object):
    def __init__(self, token="", billing_account='', host=SERVER_ADDRESS, port=443, enable_tls=True):

        metadata = [("authorization", "Bearer " + token)]

        self.channel = Channel(host=host, port=port, ssl=enable_tls)
        self.catalog_service = CatalogServiceStub(self.channel, metadata=metadata)
        self.subscription_service = SubscriptionServiceStub(self.channel, metadata=metadata)
        self.map_service = MapServiceStub(self.channel, metadata=metadata)
        self.query_service = QueryServiceStub(self.channel, metadata=metadata)
        self._disable_pagination = False

        if billing_account == '':
            billing_accounts = sync(self.subscription_service.list_billing_accounts(page_size=100, limit_to_current_user=True,
                                                                       filter_out_baccs_with_no_access_to_catalog="rwg")).billing_accounts

            if len(billing_accounts) == 0:
                raise RuntimeError('You do not have access to a Unacast account, please contact your Unacast touch point')

            if len(billing_accounts) == 1:
                self.billing_account = billing_accounts[0].id
            else:
                for b in billing_accounts:
                    if b.id == UNACAST_BILLING_ACCOUNT:
                        self.billing_account = b.id

            if self.billing_account == '':
                self.billing_account = billing_accounts[0].id
        else:
            self.billing_account = billing_account

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
        return res

    def get_layer(self, catalog_id: str, layer_id: str):
        res = sync(self.catalog_service.get_layer(catalog_id=catalog_id, layer_id=layer_id))
        return res.layer

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

    @Halo(text='Querying for metric report', spinner='dots')
    def metric_report(self, catalog_id: str, metric_id: str):
        return sync(
            self.query_service.search_metric_report(
                catalog_id=catalog_id,
                metric_id=metric_id,
                billing_context=self.billing_account,
                track_total_hits=True,
                disable_cardinalities=False,
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


class Client(object):
    def __new__(self, token="", billing_account="", catalog='rwg', port=443, enable_tls=True):
        try:
            client = _Client(billing_account=billing_account,
                             token=token,
                             port=port,
                             enable_tls=enable_tls).catalog(catalog)
            return client

        except GRPCError:
            raise Exception("ERROR: API-key timeout or invalid API-key. Please try to retrieve a new API key!")

        except Exception as e:
            raise Exception(f"Something went wrong: {e}")