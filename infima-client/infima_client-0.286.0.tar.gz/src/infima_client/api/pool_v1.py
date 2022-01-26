from dataclasses import dataclass
from typing import List, Optional

import infima_client.core.api.pool_v1.pool_v1_check_coverage as _check_coverage
import infima_client.core.api.pool_v1.pool_v1_find as _find
import infima_client.core.api.pool_v1.pool_v1_get as _get
import infima_client.core.api.pool_v1.pool_v1_get_actual_prepayments as _get_actual_prepayments
import infima_client.core.api.pool_v1.pool_v1_get_all_servicers as _get_all_servicers
import infima_client.core.api.pool_v1.pool_v1_get_characteristics as _get_characteristics
import infima_client.core.api.pool_v1.pool_v1_get_current_factor_date as _get_current_factor_date
import infima_client.core.api.pool_v1.pool_v1_get_cusip_from_pool_number as _get_cusip_from_pool_number
import infima_client.core.api.pool_v1.pool_v1_get_general_distributions as _get_general_distributions
import infima_client.core.api.pool_v1.pool_v1_get_geographic_distribution as _get_geographic_distribution
import infima_client.core.api.pool_v1.pool_v1_get_quartiles as _get_quartiles
import infima_client.core.api.pool_v1.pool_v1_get_service_info as _get_service_info
import infima_client.core.api.pool_v1.pool_v1_get_servicers as _get_servicers
import infima_client.core.api.pool_v1.pool_v1_get_summary as _get_summary
from infima_client.api.utils import unwrap_or_unset
from infima_client.core.client import Client
from infima_client.core.models import (
    CoreBinaryInfo,
    CoreDateRange,
    CoreFactorDate,
    CoreFactorDateRange,
    CorePositiveRange,
    CoreYearRange,
    GoogleRpcStatus,
    MbsAgency,
    MbsAgencyTicker,
    MbsCollateralType,
    MbsCouponType,
    MbsProduct,
    PoolV1CheckCoverageRequest,
    PoolV1CheckCoverageResponse,
    PoolV1FindRequest,
    PoolV1FindResponse,
    PoolV1GetActualPrepaymentsRequest,
    PoolV1GetActualPrepaymentsResponse,
    PoolV1GetAllServicersResponse,
    PoolV1GetCharacteristicsRequest,
    PoolV1GetCharacteristicsResponse,
    PoolV1GetCurrentFactorDateResponse,
    PoolV1GetCusipFromPoolNumberRequest,
    PoolV1GetCusipFromPoolNumberResponse,
    PoolV1GetGeneralDistributionsRequest,
    PoolV1GetGeneralDistributionsResponse,
    PoolV1GetGeographicDistributionRequest,
    PoolV1GetGeographicDistributionResponse,
    PoolV1GetQuartilesRequest,
    PoolV1GetQuartilesResponse,
    PoolV1GetRequest,
    PoolV1GetResponse,
    PoolV1GetServicersRequest,
    PoolV1GetServicersResponse,
    PoolV1GetSummaryRequest,
    PoolV1GetSummaryResponse,
)
from infima_client.core.types import UNSET


@dataclass
class PoolV1:
    client: Client

    def check_coverage(self, *, cusips: List[str]) -> PoolV1CheckCoverageResponse:
        _cusips = cusips
        json_body = PoolV1CheckCoverageRequest(cusips=_cusips)
        response = _check_coverage.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def find(
        self,
        *,
        actual_cpr_range: Optional[CorePositiveRange] = None,
        agency: Optional[MbsAgency] = None,
        agency_ticker: Optional[MbsAgencyTicker] = None,
        collateral_type: Optional[MbsCollateralType] = None,
        coupon_range: Optional[CorePositiveRange] = None,
        coupon_type: Optional[MbsCouponType] = None,
        eligible_tba_only: Optional[bool] = None,
        factor_date: Optional[CoreFactorDate] = None,
        issue_date_range: Optional[CoreDateRange] = None,
        issue_upb_range: Optional[CorePositiveRange] = None,
        limit: Optional[int] = None,
        maturity_date_range: Optional[CoreDateRange] = None,
        max_cs_range: Optional[CorePositiveRange] = None,
        max_ols_range: Optional[CorePositiveRange] = None,
        min_cs_range: Optional[CorePositiveRange] = None,
        min_ols_range: Optional[CorePositiveRange] = None,
        products: Optional[List[MbsProduct]] = None,
        standard_coupon_only: Optional[bool] = None,
        standard_product: Optional[bool] = None,
        upb_range: Optional[CorePositiveRange] = None,
        vintage_range: Optional[CoreYearRange] = None,
        wac_range: Optional[CorePositiveRange] = None,
        waocs_range: Optional[CorePositiveRange] = None,
        waols_range: Optional[CorePositiveRange] = None,
        waoltv_range: Optional[CorePositiveRange] = None,
    ) -> PoolV1FindResponse:
        _actual_cpr_range = unwrap_or_unset(actual_cpr_range)
        _agency = unwrap_or_unset(agency)
        _agency_ticker = unwrap_or_unset(agency_ticker)
        _collateral_type = unwrap_or_unset(collateral_type)
        _coupon_range = unwrap_or_unset(coupon_range)
        _coupon_type = unwrap_or_unset(coupon_type)
        _eligible_tba_only = unwrap_or_unset(eligible_tba_only)
        _factor_date = unwrap_or_unset(factor_date)
        _issue_date_range = unwrap_or_unset(issue_date_range)
        _issue_upb_range = unwrap_or_unset(issue_upb_range)
        _limit = unwrap_or_unset(limit)
        _maturity_date_range = unwrap_or_unset(maturity_date_range)
        _max_cs_range = unwrap_or_unset(max_cs_range)
        _max_ols_range = unwrap_or_unset(max_ols_range)
        _min_cs_range = unwrap_or_unset(min_cs_range)
        _min_ols_range = unwrap_or_unset(min_ols_range)
        _products = unwrap_or_unset(products)
        _standard_coupon_only = unwrap_or_unset(standard_coupon_only)
        _standard_product = unwrap_or_unset(standard_product)
        _upb_range = unwrap_or_unset(upb_range)
        _vintage_range = unwrap_or_unset(vintage_range)
        _wac_range = unwrap_or_unset(wac_range)
        _waocs_range = unwrap_or_unset(waocs_range)
        _waols_range = unwrap_or_unset(waols_range)
        _waoltv_range = unwrap_or_unset(waoltv_range)
        json_body = PoolV1FindRequest(
            actual_cpr_range=_actual_cpr_range,
            agency=_agency,
            agency_ticker=_agency_ticker,
            collateral_type=_collateral_type,
            coupon_range=_coupon_range,
            coupon_type=_coupon_type,
            eligible_tba_only=_eligible_tba_only,
            factor_date=_factor_date,
            issue_date_range=_issue_date_range,
            issue_upb_range=_issue_upb_range,
            limit=_limit,
            maturity_date_range=_maturity_date_range,
            max_cs_range=_max_cs_range,
            max_ols_range=_max_ols_range,
            min_cs_range=_min_cs_range,
            min_ols_range=_min_ols_range,
            products=_products,
            standard_coupon_only=_standard_coupon_only,
            standard_product=_standard_product,
            upb_range=_upb_range,
            vintage_range=_vintage_range,
            wac_range=_wac_range,
            waocs_range=_waocs_range,
            waols_range=_waols_range,
            waoltv_range=_waoltv_range,
        )
        response = _find.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get(
        self, *, cusips: List[str], factor_date: Optional[CoreFactorDate] = None
    ) -> PoolV1GetResponse:
        _cusips = cusips
        _factor_date = unwrap_or_unset(factor_date)
        json_body = PoolV1GetRequest(cusips=_cusips, factor_date=_factor_date)
        response = _get.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_actual_prepayments(
        self,
        *,
        cusips: List[str],
        factor_date_range: Optional[CoreFactorDateRange] = None,
    ) -> PoolV1GetActualPrepaymentsResponse:
        _cusips = cusips
        _factor_date_range = unwrap_or_unset(factor_date_range)
        json_body = PoolV1GetActualPrepaymentsRequest(
            cusips=_cusips, factor_date_range=_factor_date_range
        )
        response = _get_actual_prepayments.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_all_servicers(self) -> PoolV1GetAllServicersResponse:
        response = _get_all_servicers.sync(client=self.client)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_characteristics(
        self, *, cusips: List[str], factor_date: Optional[CoreFactorDate] = None
    ) -> PoolV1GetCharacteristicsResponse:
        _cusips = cusips
        _factor_date = unwrap_or_unset(factor_date)
        json_body = PoolV1GetCharacteristicsRequest(
            cusips=_cusips, factor_date=_factor_date
        )
        response = _get_characteristics.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_current_factor_date(self) -> PoolV1GetCurrentFactorDateResponse:
        response = _get_current_factor_date.sync(client=self.client)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_cusip_from_pool_number(
        self, *, pool_numbers: List[str]
    ) -> PoolV1GetCusipFromPoolNumberResponse:
        _pool_numbers = pool_numbers
        json_body = PoolV1GetCusipFromPoolNumberRequest(pool_numbers=_pool_numbers)
        response = _get_cusip_from_pool_number.sync(
            client=self.client, json_body=json_body
        )
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_general_distributions(
        self, *, cusips: List[str]
    ) -> PoolV1GetGeneralDistributionsResponse:
        _cusips = cusips
        json_body = PoolV1GetGeneralDistributionsRequest(cusips=_cusips)
        response = _get_general_distributions.sync(
            client=self.client, json_body=json_body
        )
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_geographic_distribution(
        self, *, cusips: List[str]
    ) -> PoolV1GetGeographicDistributionResponse:
        _cusips = cusips
        json_body = PoolV1GetGeographicDistributionRequest(cusips=_cusips)
        response = _get_geographic_distribution.sync(
            client=self.client, json_body=json_body
        )
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_quartiles(self, *, cusips: List[str]) -> PoolV1GetQuartilesResponse:
        _cusips = cusips
        json_body = PoolV1GetQuartilesRequest(cusips=_cusips)
        response = _get_quartiles.sync(client=self.client, json_body=json_body)
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

    def get_servicers(self, *, cusips: List[str]) -> PoolV1GetServicersResponse:
        _cusips = cusips
        json_body = PoolV1GetServicersRequest(cusips=_cusips)
        response = _get_servicers.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response

    def get_summary(self, *, cusips: List[str]) -> PoolV1GetSummaryResponse:
        _cusips = cusips
        json_body = PoolV1GetSummaryRequest(cusips=_cusips)
        response = _get_summary.sync(client=self.client, json_body=json_body)
        if isinstance(response, GoogleRpcStatus):
            raise ValueError(response.message)
        if response is None:
            raise ValueError("no data returned from the service")
        return response
