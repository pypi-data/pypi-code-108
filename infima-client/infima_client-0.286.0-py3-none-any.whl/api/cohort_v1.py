from dataclasses import dataclass
from typing import List, Optional

import infima_client.core.api.cohort_v1.cohort_v1_check_coverage as _check_coverage
import infima_client.core.api.cohort_v1.cohort_v1_check_exists as _check_exists
import infima_client.core.api.cohort_v1.cohort_v1_find as _find
import infima_client.core.api.cohort_v1.cohort_v1_get_actual_prepayments as _get_actual_prepayments
import infima_client.core.api.cohort_v1.cohort_v1_get_cohort_summary as _get_cohort_summary
import infima_client.core.api.cohort_v1.cohort_v1_get_member_lists as _get_member_lists
import infima_client.core.api.cohort_v1.cohort_v1_get_member_pools as _get_member_pools
import infima_client.core.api.cohort_v1.cohort_v1_get_pool_memberships as _get_pool_memberships
import infima_client.core.api.cohort_v1.cohort_v1_get_service_info as _get_service_info
from infima_client.api.utils import unwrap_or_unset
from infima_client.core.client import Client
from infima_client.core.models import (
    CohortV1CheckCoverageRequest,
    CohortV1CheckCoverageResponse,
    CohortV1CheckExistsRequest,
    CohortV1CheckExistsResponse,
    CohortV1FindRequest,
    CohortV1FindResponse,
    CohortV1GetActualPrepaymentsRequest,
    CohortV1GetActualPrepaymentsResponse,
    CohortV1GetCohortSummaryRequest,
    CohortV1GetCohortSummaryResponse,
    CohortV1GetMemberListsRequest,
    CohortV1GetMemberListsResponse,
    CohortV1GetMemberPoolsRequest,
    CohortV1GetMemberPoolsResponse,
    CohortV1GetPoolMembershipsRequest,
    CohortV1GetPoolMembershipsResponse,
    CoreBinaryInfo,
    CoreFactorDate,
    CoreFactorDateRange,
    GoogleRpcStatus,
    MbsCohortStory,
)
from infima_client.core.types import UNSET


@dataclass
class CohortV1:
    client: Client

    def check_coverage(self, *, cohorts: List[str]) -> CohortV1CheckCoverageResponse:
        _cohorts = cohorts
        json_body = CohortV1CheckCoverageRequest(cohorts=_cohorts)
        response = _check_coverage.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def check_exists(self, *, cohort: str) -> CohortV1CheckExistsResponse:
        _cohort = cohort
        json_body = CohortV1CheckExistsRequest(cohort=_cohort)
        response = _check_exists.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def find(
        self,
        *,
        coupon: Optional[float] = None,
        story: Optional[MbsCohortStory] = None,
        ticker: Optional[str] = None,
        vintage: Optional[int] = None,
    ) -> CohortV1FindResponse:
        _coupon = unwrap_or_unset(coupon)
        _story = unwrap_or_unset(story)
        _ticker = unwrap_or_unset(ticker)
        _vintage = unwrap_or_unset(vintage)
        json_body = CohortV1FindRequest(
            coupon=_coupon, story=_story, ticker=_ticker, vintage=_vintage
        )
        response = _find.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_actual_prepayments(
        self,
        *,
        cohorts: List[str],
        factor_date_range: Optional[CoreFactorDateRange] = None,
    ) -> CohortV1GetActualPrepaymentsResponse:
        _cohorts = cohorts
        _factor_date_range = unwrap_or_unset(factor_date_range)
        json_body = CohortV1GetActualPrepaymentsRequest(
            cohorts=_cohorts, factor_date_range=_factor_date_range
        )
        response = _get_actual_prepayments.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_cohort_summary(
        self, *, cohorts: List[str], factor_date: Optional[CoreFactorDate] = None
    ) -> CohortV1GetCohortSummaryResponse:
        _cohorts = cohorts
        _factor_date = unwrap_or_unset(factor_date)
        json_body = CohortV1GetCohortSummaryRequest(
            cohorts=_cohorts, factor_date=_factor_date
        )
        response = _get_cohort_summary.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_member_lists(
        self, *, cohorts: List[str], factor_date: Optional[CoreFactorDate] = None
    ) -> CohortV1GetMemberListsResponse:
        _cohorts = cohorts
        _factor_date = unwrap_or_unset(factor_date)
        json_body = CohortV1GetMemberListsRequest(
            cohorts=_cohorts, factor_date=_factor_date
        )
        response = _get_member_lists.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_member_pools(self, *, cohorts: List[str]) -> CohortV1GetMemberPoolsResponse:
        _cohorts = cohorts
        json_body = CohortV1GetMemberPoolsRequest(cohorts=_cohorts)
        response = _get_member_pools.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_pool_memberships(
        self, *, cusips: List[str], factor_date: Optional[CoreFactorDate] = None
    ) -> CohortV1GetPoolMembershipsResponse:
        _cusips = cusips
        _factor_date = unwrap_or_unset(factor_date)
        json_body = CohortV1GetPoolMembershipsRequest(
            cusips=_cusips, factor_date=_factor_date
        )
        response = _get_pool_memberships.sync(client=self.client, json_body=json_body)
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
