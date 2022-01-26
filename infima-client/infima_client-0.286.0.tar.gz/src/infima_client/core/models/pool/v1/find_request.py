from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from attr import define, field

from infima_client.core.models.core.date_range import CoreDateRange
from infima_client.core.models.core.factor_date import CoreFactorDate
from infima_client.core.models.core.positive_range import CorePositiveRange
from infima_client.core.models.core.year_range import CoreYearRange
from infima_client.core.models.mbs.agency import MbsAgency
from infima_client.core.models.mbs.agency_ticker import MbsAgencyTicker
from infima_client.core.models.mbs.collateral_type import MbsCollateralType
from infima_client.core.models.mbs.coupon_type import MbsCouponType
from infima_client.core.models.mbs.product import MbsProduct
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1FindRequest")


@define(auto_attribs=True)
class PoolV1FindRequest:
    """
    Attributes:
        actual_cpr_range (Union[Unset, CorePositiveRange]):
        agency (Union[Unset, MbsAgency]):  Default: MbsAgency.NULL_AGENCY.
        agency_ticker (Union[Unset, MbsAgencyTicker]):  Default: MbsAgencyTicker.NULL_AGENCY_TICKER.
        collateral_type (Union[Unset, MbsCollateralType]):  Default: MbsCollateralType.NULL_COLLATERAL_TYPE.
        coupon_range (Union[Unset, CorePositiveRange]):
        coupon_type (Union[Unset, MbsCouponType]):  Default: MbsCouponType.NULL_COUPON_TYPE.
        eligible_tba_only (Union[Unset, bool]):
        factor_date (Union[Unset, CoreFactorDate]):
        issue_date_range (Union[Unset, CoreDateRange]):
        issue_upb_range (Union[Unset, CorePositiveRange]):
        limit (Union[Unset, int]):
        maturity_date_range (Union[Unset, CoreDateRange]):
        max_cs_range (Union[Unset, CorePositiveRange]):
        max_ols_range (Union[Unset, CorePositiveRange]):
        min_cs_range (Union[Unset, CorePositiveRange]):
        min_ols_range (Union[Unset, CorePositiveRange]):
        products (Union[Unset, List[MbsProduct]]):
        standard_coupon_only (Union[Unset, bool]):
        standard_product (Union[Unset, bool]):
        upb_range (Union[Unset, CorePositiveRange]):
        vintage_range (Union[Unset, CoreYearRange]):
        wac_range (Union[Unset, CorePositiveRange]):
        waocs_range (Union[Unset, CorePositiveRange]):
        waols_range (Union[Unset, CorePositiveRange]):
        waoltv_range (Union[Unset, CorePositiveRange]):
    """

    actual_cpr_range: Union[Unset, CorePositiveRange] = UNSET
    agency: Union[Unset, MbsAgency] = MbsAgency.NULL_AGENCY
    agency_ticker: Union[Unset, MbsAgencyTicker] = MbsAgencyTicker.NULL_AGENCY_TICKER
    collateral_type: Union[
        Unset, MbsCollateralType
    ] = MbsCollateralType.NULL_COLLATERAL_TYPE
    coupon_range: Union[Unset, CorePositiveRange] = UNSET
    coupon_type: Union[Unset, MbsCouponType] = MbsCouponType.NULL_COUPON_TYPE
    eligible_tba_only: Union[Unset, bool] = UNSET
    factor_date: Union[Unset, CoreFactorDate] = UNSET
    issue_date_range: Union[Unset, CoreDateRange] = UNSET
    issue_upb_range: Union[Unset, CorePositiveRange] = UNSET
    limit: Union[Unset, int] = UNSET
    maturity_date_range: Union[Unset, CoreDateRange] = UNSET
    max_cs_range: Union[Unset, CorePositiveRange] = UNSET
    max_ols_range: Union[Unset, CorePositiveRange] = UNSET
    min_cs_range: Union[Unset, CorePositiveRange] = UNSET
    min_ols_range: Union[Unset, CorePositiveRange] = UNSET
    products: Union[Unset, List[MbsProduct]] = UNSET
    standard_coupon_only: Union[Unset, bool] = UNSET
    standard_product: Union[Unset, bool] = UNSET
    upb_range: Union[Unset, CorePositiveRange] = UNSET
    vintage_range: Union[Unset, CoreYearRange] = UNSET
    wac_range: Union[Unset, CorePositiveRange] = UNSET
    waocs_range: Union[Unset, CorePositiveRange] = UNSET
    waols_range: Union[Unset, CorePositiveRange] = UNSET
    waoltv_range: Union[Unset, CorePositiveRange] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        actual_cpr_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.actual_cpr_range, Unset):
            actual_cpr_range = self.actual_cpr_range.to_dict()

        agency: Union[Unset, str] = UNSET
        if not isinstance(self.agency, Unset):
            agency = self.agency.value

        agency_ticker: Union[Unset, str] = UNSET
        if not isinstance(self.agency_ticker, Unset):
            agency_ticker = self.agency_ticker.value

        collateral_type: Union[Unset, str] = UNSET
        if not isinstance(self.collateral_type, Unset):
            collateral_type = self.collateral_type.value

        coupon_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.coupon_range, Unset):
            coupon_range = self.coupon_range.to_dict()

        coupon_type: Union[Unset, str] = UNSET
        if not isinstance(self.coupon_type, Unset):
            coupon_type = self.coupon_type.value

        eligible_tba_only = self.eligible_tba_only
        factor_date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.factor_date, Unset):
            factor_date = self.factor_date.to_dict()

        issue_date_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.issue_date_range, Unset):
            issue_date_range = self.issue_date_range.to_dict()

        issue_upb_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.issue_upb_range, Unset):
            issue_upb_range = self.issue_upb_range.to_dict()

        limit = self.limit
        maturity_date_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.maturity_date_range, Unset):
            maturity_date_range = self.maturity_date_range.to_dict()

        max_cs_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.max_cs_range, Unset):
            max_cs_range = self.max_cs_range.to_dict()

        max_ols_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.max_ols_range, Unset):
            max_ols_range = self.max_ols_range.to_dict()

        min_cs_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.min_cs_range, Unset):
            min_cs_range = self.min_cs_range.to_dict()

        min_ols_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.min_ols_range, Unset):
            min_ols_range = self.min_ols_range.to_dict()

        products: Union[Unset, List[str]] = UNSET
        if not isinstance(self.products, Unset):
            products = []
            for products_item_data in self.products:
                products_item = products_item_data.value

                products.append(products_item)

        standard_coupon_only = self.standard_coupon_only
        standard_product = self.standard_product
        upb_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.upb_range, Unset):
            upb_range = self.upb_range.to_dict()

        vintage_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.vintage_range, Unset):
            vintage_range = self.vintage_range.to_dict()

        wac_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.wac_range, Unset):
            wac_range = self.wac_range.to_dict()

        waocs_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.waocs_range, Unset):
            waocs_range = self.waocs_range.to_dict()

        waols_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.waols_range, Unset):
            waols_range = self.waols_range.to_dict()

        waoltv_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.waoltv_range, Unset):
            waoltv_range = self.waoltv_range.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actual_cpr_range is not UNSET:
            field_dict["actualCprRange"] = actual_cpr_range
        if agency is not UNSET:
            field_dict["agency"] = agency
        if agency_ticker is not UNSET:
            field_dict["agencyTicker"] = agency_ticker
        if collateral_type is not UNSET:
            field_dict["collateralType"] = collateral_type
        if coupon_range is not UNSET:
            field_dict["couponRange"] = coupon_range
        if coupon_type is not UNSET:
            field_dict["couponType"] = coupon_type
        if eligible_tba_only is not UNSET:
            field_dict["eligibleTbaOnly"] = eligible_tba_only
        if factor_date is not UNSET:
            field_dict["factorDate"] = factor_date
        if issue_date_range is not UNSET:
            field_dict["issueDateRange"] = issue_date_range
        if issue_upb_range is not UNSET:
            field_dict["issueUpbRange"] = issue_upb_range
        if limit is not UNSET:
            field_dict["limit"] = limit
        if maturity_date_range is not UNSET:
            field_dict["maturityDateRange"] = maturity_date_range
        if max_cs_range is not UNSET:
            field_dict["maxCsRange"] = max_cs_range
        if max_ols_range is not UNSET:
            field_dict["maxOlsRange"] = max_ols_range
        if min_cs_range is not UNSET:
            field_dict["minCsRange"] = min_cs_range
        if min_ols_range is not UNSET:
            field_dict["minOlsRange"] = min_ols_range
        if products is not UNSET:
            field_dict["products"] = products
        if standard_coupon_only is not UNSET:
            field_dict["standardCouponOnly"] = standard_coupon_only
        if standard_product is not UNSET:
            field_dict["standardProduct"] = standard_product
        if upb_range is not UNSET:
            field_dict["upbRange"] = upb_range
        if vintage_range is not UNSET:
            field_dict["vintageRange"] = vintage_range
        if wac_range is not UNSET:
            field_dict["wacRange"] = wac_range
        if waocs_range is not UNSET:
            field_dict["waocsRange"] = waocs_range
        if waols_range is not UNSET:
            field_dict["waolsRange"] = waols_range
        if waoltv_range is not UNSET:
            field_dict["waoltvRange"] = waoltv_range

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _actual_cpr_range = d.pop("actualCprRange", UNSET)
        actual_cpr_range: Union[Unset, CorePositiveRange]
        if isinstance(_actual_cpr_range, Unset):
            actual_cpr_range = UNSET
        else:
            actual_cpr_range = CorePositiveRange.from_dict(_actual_cpr_range)

        _agency = d.pop("agency", UNSET)
        agency: Union[Unset, MbsAgency]
        if isinstance(_agency, Unset):
            agency = UNSET
        else:
            agency = MbsAgency(_agency)

        _agency_ticker = d.pop("agencyTicker", UNSET)
        agency_ticker: Union[Unset, MbsAgencyTicker]
        if isinstance(_agency_ticker, Unset):
            agency_ticker = UNSET
        else:
            agency_ticker = MbsAgencyTicker(_agency_ticker)

        _collateral_type = d.pop("collateralType", UNSET)
        collateral_type: Union[Unset, MbsCollateralType]
        if isinstance(_collateral_type, Unset):
            collateral_type = UNSET
        else:
            collateral_type = MbsCollateralType(_collateral_type)

        _coupon_range = d.pop("couponRange", UNSET)
        coupon_range: Union[Unset, CorePositiveRange]
        if isinstance(_coupon_range, Unset):
            coupon_range = UNSET
        else:
            coupon_range = CorePositiveRange.from_dict(_coupon_range)

        _coupon_type = d.pop("couponType", UNSET)
        coupon_type: Union[Unset, MbsCouponType]
        if isinstance(_coupon_type, Unset):
            coupon_type = UNSET
        else:
            coupon_type = MbsCouponType(_coupon_type)

        eligible_tba_only = d.pop("eligibleTbaOnly", UNSET)

        _factor_date = d.pop("factorDate", UNSET)
        factor_date: Union[Unset, CoreFactorDate]
        if isinstance(_factor_date, Unset):
            factor_date = UNSET
        else:
            factor_date = CoreFactorDate.from_dict(_factor_date)

        _issue_date_range = d.pop("issueDateRange", UNSET)
        issue_date_range: Union[Unset, CoreDateRange]
        if isinstance(_issue_date_range, Unset):
            issue_date_range = UNSET
        else:
            issue_date_range = CoreDateRange.from_dict(_issue_date_range)

        _issue_upb_range = d.pop("issueUpbRange", UNSET)
        issue_upb_range: Union[Unset, CorePositiveRange]
        if isinstance(_issue_upb_range, Unset):
            issue_upb_range = UNSET
        else:
            issue_upb_range = CorePositiveRange.from_dict(_issue_upb_range)

        limit = d.pop("limit", UNSET)

        _maturity_date_range = d.pop("maturityDateRange", UNSET)
        maturity_date_range: Union[Unset, CoreDateRange]
        if isinstance(_maturity_date_range, Unset):
            maturity_date_range = UNSET
        else:
            maturity_date_range = CoreDateRange.from_dict(_maturity_date_range)

        _max_cs_range = d.pop("maxCsRange", UNSET)
        max_cs_range: Union[Unset, CorePositiveRange]
        if isinstance(_max_cs_range, Unset):
            max_cs_range = UNSET
        else:
            max_cs_range = CorePositiveRange.from_dict(_max_cs_range)

        _max_ols_range = d.pop("maxOlsRange", UNSET)
        max_ols_range: Union[Unset, CorePositiveRange]
        if isinstance(_max_ols_range, Unset):
            max_ols_range = UNSET
        else:
            max_ols_range = CorePositiveRange.from_dict(_max_ols_range)

        _min_cs_range = d.pop("minCsRange", UNSET)
        min_cs_range: Union[Unset, CorePositiveRange]
        if isinstance(_min_cs_range, Unset):
            min_cs_range = UNSET
        else:
            min_cs_range = CorePositiveRange.from_dict(_min_cs_range)

        _min_ols_range = d.pop("minOlsRange", UNSET)
        min_ols_range: Union[Unset, CorePositiveRange]
        if isinstance(_min_ols_range, Unset):
            min_ols_range = UNSET
        else:
            min_ols_range = CorePositiveRange.from_dict(_min_ols_range)

        products = []
        _products = d.pop("products", UNSET)
        for products_item_data in _products or []:
            products_item = MbsProduct(products_item_data)

            products.append(products_item)

        standard_coupon_only = d.pop("standardCouponOnly", UNSET)

        standard_product = d.pop("standardProduct", UNSET)

        _upb_range = d.pop("upbRange", UNSET)
        upb_range: Union[Unset, CorePositiveRange]
        if isinstance(_upb_range, Unset):
            upb_range = UNSET
        else:
            upb_range = CorePositiveRange.from_dict(_upb_range)

        _vintage_range = d.pop("vintageRange", UNSET)
        vintage_range: Union[Unset, CoreYearRange]
        if isinstance(_vintage_range, Unset):
            vintage_range = UNSET
        else:
            vintage_range = CoreYearRange.from_dict(_vintage_range)

        _wac_range = d.pop("wacRange", UNSET)
        wac_range: Union[Unset, CorePositiveRange]
        if isinstance(_wac_range, Unset):
            wac_range = UNSET
        else:
            wac_range = CorePositiveRange.from_dict(_wac_range)

        _waocs_range = d.pop("waocsRange", UNSET)
        waocs_range: Union[Unset, CorePositiveRange]
        if isinstance(_waocs_range, Unset):
            waocs_range = UNSET
        else:
            waocs_range = CorePositiveRange.from_dict(_waocs_range)

        _waols_range = d.pop("waolsRange", UNSET)
        waols_range: Union[Unset, CorePositiveRange]
        if isinstance(_waols_range, Unset):
            waols_range = UNSET
        else:
            waols_range = CorePositiveRange.from_dict(_waols_range)

        _waoltv_range = d.pop("waoltvRange", UNSET)
        waoltv_range: Union[Unset, CorePositiveRange]
        if isinstance(_waoltv_range, Unset):
            waoltv_range = UNSET
        else:
            waoltv_range = CorePositiveRange.from_dict(_waoltv_range)

        pool_v1_find_request = cls(
            actual_cpr_range=actual_cpr_range,
            agency=agency,
            agency_ticker=agency_ticker,
            collateral_type=collateral_type,
            coupon_range=coupon_range,
            coupon_type=coupon_type,
            eligible_tba_only=eligible_tba_only,
            factor_date=factor_date,
            issue_date_range=issue_date_range,
            issue_upb_range=issue_upb_range,
            limit=limit,
            maturity_date_range=maturity_date_range,
            max_cs_range=max_cs_range,
            max_ols_range=max_ols_range,
            min_cs_range=min_cs_range,
            min_ols_range=min_ols_range,
            products=products,
            standard_coupon_only=standard_coupon_only,
            standard_product=standard_product,
            upb_range=upb_range,
            vintage_range=vintage_range,
            wac_range=wac_range,
            waocs_range=waocs_range,
            waols_range=waols_range,
            waoltv_range=waoltv_range,
        )

        pool_v1_find_request.additional_properties = d
        return pool_v1_find_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
