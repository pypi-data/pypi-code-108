from dataclasses import dataclass
from typing import Optional

import infima_client.core.api.search_v0.search_v0_delete_query as _delete_query
import infima_client.core.api.search_v0.search_v0_get_all_query_names as _get_all_query_names
import infima_client.core.api.search_v0.search_v0_get_query as _get_query
import infima_client.core.api.search_v0.search_v0_get_service_info as _get_service_info
import infima_client.core.api.search_v0.search_v0_save_query as _save_query
import infima_client.core.api.search_v0.search_v0_search_pools as _search_pools
from infima_client.api.utils import unwrap_or_unset
from infima_client.core.client import Client
from infima_client.core.models import (
    CoreBinaryInfo,
    GoogleRpcStatus,
    SearchV0AttributesCriterion,
    SearchV0CohortUniverse,
    SearchV0DeleteQueryRequest,
    SearchV0DeleteQueryResponse,
    SearchV0GetAllQueryNamesResponse,
    SearchV0GetQueryRequest,
    SearchV0GetQueryResponse,
    SearchV0PredictionCriterion,
    SearchV0SavedQuery,
    SearchV0SaveQueryRequest,
    SearchV0SaveQueryResponse,
    SearchV0SearchCriterion,
    SearchV0SearchPoolsRequest,
    SearchV0SearchPoolsResponse,
)
from infima_client.core.types import UNSET


@dataclass
class SearchV0:
    client: Client

    def delete_query(
        self, *, name: Optional[str] = None
    ) -> SearchV0DeleteQueryResponse:
        _name = unwrap_or_unset(name)
        json_body = SearchV0DeleteQueryRequest(name=_name)
        response = _delete_query.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_all_query_names(self) -> SearchV0GetAllQueryNamesResponse:
        response = _get_all_query_names.sync(client=self.client)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_query(self, *, name: Optional[str] = None) -> SearchV0GetQueryResponse:
        _name = unwrap_or_unset(name)
        json_body = SearchV0GetQueryRequest(name=_name)
        response = _get_query.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_service_info(self) -> CoreBinaryInfo:
        response = _get_service_info.sync(client=self.client)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def save_query(
        self, *, saved: Optional[SearchV0SavedQuery] = None
    ) -> SearchV0SaveQueryResponse:
        _saved = unwrap_or_unset(saved)
        json_body = SearchV0SaveQueryRequest(saved=_saved)
        response = _save_query.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def search_pools(
        self,
        *,
        attributes: Optional[SearchV0AttributesCriterion] = None,
        cohorts: Optional[SearchV0CohortUniverse] = None,
        criteria: Optional[SearchV0SearchCriterion] = None,
        predictions: Optional[SearchV0PredictionCriterion] = None,
    ) -> SearchV0SearchPoolsResponse:
        _attributes = unwrap_or_unset(attributes)
        _cohorts = unwrap_or_unset(cohorts)
        _criteria = unwrap_or_unset(criteria)
        _predictions = unwrap_or_unset(predictions)
        json_body = SearchV0SearchPoolsRequest(
            attributes=_attributes,
            cohorts=_cohorts,
            criteria=_criteria,
            predictions=_predictions,
        )
        response = _search_pools.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response
