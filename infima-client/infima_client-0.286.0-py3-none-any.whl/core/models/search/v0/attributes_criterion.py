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
from infima_client.core.models.core.positive_range import CorePositiveRange
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="SearchV0AttributesCriterion")


@define(auto_attribs=True)
class SearchV0AttributesCriterion:
    """
    Attributes:
        coupon_range (Union[Unset, CorePositiveRange]):
        cpr_range (Union[Unset, CorePositiveRange]):
        investor_occ_range (Union[Unset, CorePositiveRange]):
        iss_upb_range (Union[Unset, CorePositiveRange]):
        issue_date_range (Union[Unset, CoreDateRange]):
        maturity_date_range (Union[Unset, CoreDateRange]):
        max_cs_range (Union[Unset, CorePositiveRange]):
        max_iss_loan_balance_range (Union[Unset, CorePositiveRange]):
        min_cs_range (Union[Unset, CorePositiveRange]):
        min_iss_loan_balance_range (Union[Unset, CorePositiveRange]):
        upb_range (Union[Unset, CorePositiveRange]):
        wac_range (Union[Unset, CorePositiveRange]):
        waocs_range (Union[Unset, CorePositiveRange]):
        waols_range (Union[Unset, CorePositiveRange]):
        waoltv_range (Union[Unset, CorePositiveRange]):
    """

    coupon_range: Union[Unset, CorePositiveRange] = UNSET
    cpr_range: Union[Unset, CorePositiveRange] = UNSET
    investor_occ_range: Union[Unset, CorePositiveRange] = UNSET
    iss_upb_range: Union[Unset, CorePositiveRange] = UNSET
    issue_date_range: Union[Unset, CoreDateRange] = UNSET
    maturity_date_range: Union[Unset, CoreDateRange] = UNSET
    max_cs_range: Union[Unset, CorePositiveRange] = UNSET
    max_iss_loan_balance_range: Union[Unset, CorePositiveRange] = UNSET
    min_cs_range: Union[Unset, CorePositiveRange] = UNSET
    min_iss_loan_balance_range: Union[Unset, CorePositiveRange] = UNSET
    upb_range: Union[Unset, CorePositiveRange] = UNSET
    wac_range: Union[Unset, CorePositiveRange] = UNSET
    waocs_range: Union[Unset, CorePositiveRange] = UNSET
    waols_range: Union[Unset, CorePositiveRange] = UNSET
    waoltv_range: Union[Unset, CorePositiveRange] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        coupon_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.coupon_range, Unset):
            coupon_range = self.coupon_range.to_dict()

        cpr_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cpr_range, Unset):
            cpr_range = self.cpr_range.to_dict()

        investor_occ_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.investor_occ_range, Unset):
            investor_occ_range = self.investor_occ_range.to_dict()

        iss_upb_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.iss_upb_range, Unset):
            iss_upb_range = self.iss_upb_range.to_dict()

        issue_date_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.issue_date_range, Unset):
            issue_date_range = self.issue_date_range.to_dict()

        maturity_date_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.maturity_date_range, Unset):
            maturity_date_range = self.maturity_date_range.to_dict()

        max_cs_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.max_cs_range, Unset):
            max_cs_range = self.max_cs_range.to_dict()

        max_iss_loan_balance_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.max_iss_loan_balance_range, Unset):
            max_iss_loan_balance_range = self.max_iss_loan_balance_range.to_dict()

        min_cs_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.min_cs_range, Unset):
            min_cs_range = self.min_cs_range.to_dict()

        min_iss_loan_balance_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.min_iss_loan_balance_range, Unset):
            min_iss_loan_balance_range = self.min_iss_loan_balance_range.to_dict()

        upb_range: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.upb_range, Unset):
            upb_range = self.upb_range.to_dict()

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
        if coupon_range is not UNSET:
            field_dict["couponRange"] = coupon_range
        if cpr_range is not UNSET:
            field_dict["cprRange"] = cpr_range
        if investor_occ_range is not UNSET:
            field_dict["investorOccRange"] = investor_occ_range
        if iss_upb_range is not UNSET:
            field_dict["issUpbRange"] = iss_upb_range
        if issue_date_range is not UNSET:
            field_dict["issueDateRange"] = issue_date_range
        if maturity_date_range is not UNSET:
            field_dict["maturityDateRange"] = maturity_date_range
        if max_cs_range is not UNSET:
            field_dict["maxCsRange"] = max_cs_range
        if max_iss_loan_balance_range is not UNSET:
            field_dict["maxIssLoanBalanceRange"] = max_iss_loan_balance_range
        if min_cs_range is not UNSET:
            field_dict["minCsRange"] = min_cs_range
        if min_iss_loan_balance_range is not UNSET:
            field_dict["minIssLoanBalanceRange"] = min_iss_loan_balance_range
        if upb_range is not UNSET:
            field_dict["upbRange"] = upb_range
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
        _coupon_range = d.pop("couponRange", UNSET)
        coupon_range: Union[Unset, CorePositiveRange]
        if isinstance(_coupon_range, Unset):
            coupon_range = UNSET
        else:
            coupon_range = CorePositiveRange.from_dict(_coupon_range)

        _cpr_range = d.pop("cprRange", UNSET)
        cpr_range: Union[Unset, CorePositiveRange]
        if isinstance(_cpr_range, Unset):
            cpr_range = UNSET
        else:
            cpr_range = CorePositiveRange.from_dict(_cpr_range)

        _investor_occ_range = d.pop("investorOccRange", UNSET)
        investor_occ_range: Union[Unset, CorePositiveRange]
        if isinstance(_investor_occ_range, Unset):
            investor_occ_range = UNSET
        else:
            investor_occ_range = CorePositiveRange.from_dict(_investor_occ_range)

        _iss_upb_range = d.pop("issUpbRange", UNSET)
        iss_upb_range: Union[Unset, CorePositiveRange]
        if isinstance(_iss_upb_range, Unset):
            iss_upb_range = UNSET
        else:
            iss_upb_range = CorePositiveRange.from_dict(_iss_upb_range)

        _issue_date_range = d.pop("issueDateRange", UNSET)
        issue_date_range: Union[Unset, CoreDateRange]
        if isinstance(_issue_date_range, Unset):
            issue_date_range = UNSET
        else:
            issue_date_range = CoreDateRange.from_dict(_issue_date_range)

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

        _max_iss_loan_balance_range = d.pop("maxIssLoanBalanceRange", UNSET)
        max_iss_loan_balance_range: Union[Unset, CorePositiveRange]
        if isinstance(_max_iss_loan_balance_range, Unset):
            max_iss_loan_balance_range = UNSET
        else:
            max_iss_loan_balance_range = CorePositiveRange.from_dict(
                _max_iss_loan_balance_range
            )

        _min_cs_range = d.pop("minCsRange", UNSET)
        min_cs_range: Union[Unset, CorePositiveRange]
        if isinstance(_min_cs_range, Unset):
            min_cs_range = UNSET
        else:
            min_cs_range = CorePositiveRange.from_dict(_min_cs_range)

        _min_iss_loan_balance_range = d.pop("minIssLoanBalanceRange", UNSET)
        min_iss_loan_balance_range: Union[Unset, CorePositiveRange]
        if isinstance(_min_iss_loan_balance_range, Unset):
            min_iss_loan_balance_range = UNSET
        else:
            min_iss_loan_balance_range = CorePositiveRange.from_dict(
                _min_iss_loan_balance_range
            )

        _upb_range = d.pop("upbRange", UNSET)
        upb_range: Union[Unset, CorePositiveRange]
        if isinstance(_upb_range, Unset):
            upb_range = UNSET
        else:
            upb_range = CorePositiveRange.from_dict(_upb_range)

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

        search_v0_attributes_criterion = cls(
            coupon_range=coupon_range,
            cpr_range=cpr_range,
            investor_occ_range=investor_occ_range,
            iss_upb_range=iss_upb_range,
            issue_date_range=issue_date_range,
            maturity_date_range=maturity_date_range,
            max_cs_range=max_cs_range,
            max_iss_loan_balance_range=max_iss_loan_balance_range,
            min_cs_range=min_cs_range,
            min_iss_loan_balance_range=min_iss_loan_balance_range,
            upb_range=upb_range,
            wac_range=wac_range,
            waocs_range=waocs_range,
            waols_range=waols_range,
            waoltv_range=waoltv_range,
        )

        search_v0_attributes_criterion.additional_properties = d
        return search_v0_attributes_criterion

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
