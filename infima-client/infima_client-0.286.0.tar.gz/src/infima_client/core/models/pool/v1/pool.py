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

from infima_client.core.models.core.factor_date import CoreFactorDate
from infima_client.core.models.mbs.agency import MbsAgency
from infima_client.core.models.mbs.agency_ticker import MbsAgencyTicker
from infima_client.core.models.mbs.collateral_type import MbsCollateralType
from infima_client.core.models.mbs.coupon_type import MbsCouponType
from infima_client.core.models.mbs.product import MbsProduct
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PoolV1Pool")


@define(auto_attribs=True)
class PoolV1Pool:
    """Pool attributes.

    Attributes:
        agency (Union[Unset, MbsAgency]):  Default: MbsAgency.NULL_AGENCY.
        agency_ticker (Union[Unset, MbsAgencyTicker]):  Default: MbsAgencyTicker.NULL_AGENCY_TICKER.
        collateral_type (Union[Unset, MbsCollateralType]):  Default: MbsCollateralType.NULL_COLLATERAL_TYPE.
        coupon (Union[Unset, float]):
        coupon_type (Union[Unset, MbsCouponType]):  Default: MbsCouponType.NULL_COUPON_TYPE.
        cpr1 (Union[Unset, float]):
        cusip (Union[Unset, str]):
        factor (Union[Unset, float]):
        factor_date (Union[Unset, CoreFactorDate]):
        inv_pct (Union[Unset, float]):
        iss_num_loans (Union[Unset, int]):
        iss_upb (Union[Unset, float]):
        iss_wac (Union[Unset, float]):
        iss_wala (Union[Unset, int]):
        issue_date (Union[Unset, CoreFactorDate]):
        maturity_date (Union[Unset, CoreFactorDate]):
        max_cs (Union[Unset, int]):
        max_ltv (Union[Unset, int]):
        max_ols (Union[Unset, float]):
        max_servicer (Union[Unset, str]):
        max_servicer_pct (Union[Unset, float]):
        max_state (Union[Unset, str]):
        max_state_pct (Union[Unset, float]):
        min_cs (Union[Unset, int]):
        min_ltv (Union[Unset, int]):
        min_ols (Union[Unset, float]):
        num_loans (Union[Unset, int]):
        orig_story (Union[Unset, str]):
        orig_story_pct (Union[Unset, float]):
        pool_number (Union[Unset, str]):
        prefix (Union[Unset, str]):
        product (Union[Unset, MbsProduct]):  Default: MbsProduct.NULL_PRODUCT.
        production_year (Union[Unset, int]):
        purch_pct (Union[Unset, float]):
        refi_pct (Union[Unset, float]):
        smm1 (Union[Unset, float]):
        upb (Union[Unset, float]):
        wac (Union[Unset, float]):
        wala (Union[Unset, float]):
        wals (Union[Unset, float]):
        wam (Union[Unset, float]):
        waocs (Union[Unset, int]):
        waols (Union[Unset, float]):
        waoltv (Union[Unset, int]):
    """

    agency: Union[Unset, MbsAgency] = MbsAgency.NULL_AGENCY
    agency_ticker: Union[Unset, MbsAgencyTicker] = MbsAgencyTicker.NULL_AGENCY_TICKER
    collateral_type: Union[
        Unset, MbsCollateralType
    ] = MbsCollateralType.NULL_COLLATERAL_TYPE
    coupon: Union[Unset, float] = UNSET
    coupon_type: Union[Unset, MbsCouponType] = MbsCouponType.NULL_COUPON_TYPE
    cpr1: Union[Unset, float] = UNSET
    cusip: Union[Unset, str] = UNSET
    factor: Union[Unset, float] = UNSET
    factor_date: Union[Unset, CoreFactorDate] = UNSET
    inv_pct: Union[Unset, float] = UNSET
    iss_num_loans: Union[Unset, int] = UNSET
    iss_upb: Union[Unset, float] = UNSET
    iss_wac: Union[Unset, float] = UNSET
    iss_wala: Union[Unset, int] = UNSET
    issue_date: Union[Unset, CoreFactorDate] = UNSET
    maturity_date: Union[Unset, CoreFactorDate] = UNSET
    max_cs: Union[Unset, int] = UNSET
    max_ltv: Union[Unset, int] = UNSET
    max_ols: Union[Unset, float] = UNSET
    max_servicer: Union[Unset, str] = UNSET
    max_servicer_pct: Union[Unset, float] = UNSET
    max_state: Union[Unset, str] = UNSET
    max_state_pct: Union[Unset, float] = UNSET
    min_cs: Union[Unset, int] = UNSET
    min_ltv: Union[Unset, int] = UNSET
    min_ols: Union[Unset, float] = UNSET
    num_loans: Union[Unset, int] = UNSET
    orig_story: Union[Unset, str] = UNSET
    orig_story_pct: Union[Unset, float] = UNSET
    pool_number: Union[Unset, str] = UNSET
    prefix: Union[Unset, str] = UNSET
    product: Union[Unset, MbsProduct] = MbsProduct.NULL_PRODUCT
    production_year: Union[Unset, int] = UNSET
    purch_pct: Union[Unset, float] = UNSET
    refi_pct: Union[Unset, float] = UNSET
    smm1: Union[Unset, float] = UNSET
    upb: Union[Unset, float] = UNSET
    wac: Union[Unset, float] = UNSET
    wala: Union[Unset, float] = UNSET
    wals: Union[Unset, float] = UNSET
    wam: Union[Unset, float] = UNSET
    waocs: Union[Unset, int] = UNSET
    waols: Union[Unset, float] = UNSET
    waoltv: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        agency: Union[Unset, str] = UNSET
        if not isinstance(self.agency, Unset):
            agency = self.agency.value

        agency_ticker: Union[Unset, str] = UNSET
        if not isinstance(self.agency_ticker, Unset):
            agency_ticker = self.agency_ticker.value

        collateral_type: Union[Unset, str] = UNSET
        if not isinstance(self.collateral_type, Unset):
            collateral_type = self.collateral_type.value

        coupon = self.coupon
        coupon_type: Union[Unset, str] = UNSET
        if not isinstance(self.coupon_type, Unset):
            coupon_type = self.coupon_type.value

        cpr1 = self.cpr1
        cusip = self.cusip
        factor = self.factor
        factor_date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.factor_date, Unset):
            factor_date = self.factor_date.to_dict()

        inv_pct = self.inv_pct
        iss_num_loans = self.iss_num_loans
        iss_upb = self.iss_upb
        iss_wac = self.iss_wac
        iss_wala = self.iss_wala
        issue_date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.issue_date, Unset):
            issue_date = self.issue_date.to_dict()

        maturity_date: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.maturity_date, Unset):
            maturity_date = self.maturity_date.to_dict()

        max_cs = self.max_cs
        max_ltv = self.max_ltv
        max_ols = self.max_ols
        max_servicer = self.max_servicer
        max_servicer_pct = self.max_servicer_pct
        max_state = self.max_state
        max_state_pct = self.max_state_pct
        min_cs = self.min_cs
        min_ltv = self.min_ltv
        min_ols = self.min_ols
        num_loans = self.num_loans
        orig_story = self.orig_story
        orig_story_pct = self.orig_story_pct
        pool_number = self.pool_number
        prefix = self.prefix
        product: Union[Unset, str] = UNSET
        if not isinstance(self.product, Unset):
            product = self.product.value

        production_year = self.production_year
        purch_pct = self.purch_pct
        refi_pct = self.refi_pct
        smm1 = self.smm1
        upb = self.upb
        wac = self.wac
        wala = self.wala
        wals = self.wals
        wam = self.wam
        waocs = self.waocs
        waols = self.waols
        waoltv = self.waoltv

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if agency is not UNSET:
            field_dict["agency"] = agency
        if agency_ticker is not UNSET:
            field_dict["agencyTicker"] = agency_ticker
        if collateral_type is not UNSET:
            field_dict["collateralType"] = collateral_type
        if coupon is not UNSET:
            field_dict["coupon"] = coupon
        if coupon_type is not UNSET:
            field_dict["couponType"] = coupon_type
        if cpr1 is not UNSET:
            field_dict["cpr1"] = cpr1
        if cusip is not UNSET:
            field_dict["cusip"] = cusip
        if factor is not UNSET:
            field_dict["factor"] = factor
        if factor_date is not UNSET:
            field_dict["factorDate"] = factor_date
        if inv_pct is not UNSET:
            field_dict["invPct"] = inv_pct
        if iss_num_loans is not UNSET:
            field_dict["issNumLoans"] = iss_num_loans
        if iss_upb is not UNSET:
            field_dict["issUpb"] = iss_upb
        if iss_wac is not UNSET:
            field_dict["issWac"] = iss_wac
        if iss_wala is not UNSET:
            field_dict["issWala"] = iss_wala
        if issue_date is not UNSET:
            field_dict["issueDate"] = issue_date
        if maturity_date is not UNSET:
            field_dict["maturityDate"] = maturity_date
        if max_cs is not UNSET:
            field_dict["maxCs"] = max_cs
        if max_ltv is not UNSET:
            field_dict["maxLtv"] = max_ltv
        if max_ols is not UNSET:
            field_dict["maxOls"] = max_ols
        if max_servicer is not UNSET:
            field_dict["maxServicer"] = max_servicer
        if max_servicer_pct is not UNSET:
            field_dict["maxServicerPct"] = max_servicer_pct
        if max_state is not UNSET:
            field_dict["maxState"] = max_state
        if max_state_pct is not UNSET:
            field_dict["maxStatePct"] = max_state_pct
        if min_cs is not UNSET:
            field_dict["minCs"] = min_cs
        if min_ltv is not UNSET:
            field_dict["minLtv"] = min_ltv
        if min_ols is not UNSET:
            field_dict["minOls"] = min_ols
        if num_loans is not UNSET:
            field_dict["numLoans"] = num_loans
        if orig_story is not UNSET:
            field_dict["origStory"] = orig_story
        if orig_story_pct is not UNSET:
            field_dict["origStoryPct"] = orig_story_pct
        if pool_number is not UNSET:
            field_dict["poolNumber"] = pool_number
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if product is not UNSET:
            field_dict["product"] = product
        if production_year is not UNSET:
            field_dict["productionYear"] = production_year
        if purch_pct is not UNSET:
            field_dict["purchPct"] = purch_pct
        if refi_pct is not UNSET:
            field_dict["refiPct"] = refi_pct
        if smm1 is not UNSET:
            field_dict["smm1"] = smm1
        if upb is not UNSET:
            field_dict["upb"] = upb
        if wac is not UNSET:
            field_dict["wac"] = wac
        if wala is not UNSET:
            field_dict["wala"] = wala
        if wals is not UNSET:
            field_dict["wals"] = wals
        if wam is not UNSET:
            field_dict["wam"] = wam
        if waocs is not UNSET:
            field_dict["waocs"] = waocs
        if waols is not UNSET:
            field_dict["waols"] = waols
        if waoltv is not UNSET:
            field_dict["waoltv"] = waoltv

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
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

        coupon = d.pop("coupon", UNSET)

        _coupon_type = d.pop("couponType", UNSET)
        coupon_type: Union[Unset, MbsCouponType]
        if isinstance(_coupon_type, Unset):
            coupon_type = UNSET
        else:
            coupon_type = MbsCouponType(_coupon_type)

        cpr1 = d.pop("cpr1", UNSET)

        cusip = d.pop("cusip", UNSET)

        factor = d.pop("factor", UNSET)

        _factor_date = d.pop("factorDate", UNSET)
        factor_date: Union[Unset, CoreFactorDate]
        if isinstance(_factor_date, Unset):
            factor_date = UNSET
        else:
            factor_date = CoreFactorDate.from_dict(_factor_date)

        inv_pct = d.pop("invPct", UNSET)

        iss_num_loans = d.pop("issNumLoans", UNSET)

        iss_upb = d.pop("issUpb", UNSET)

        iss_wac = d.pop("issWac", UNSET)

        iss_wala = d.pop("issWala", UNSET)

        _issue_date = d.pop("issueDate", UNSET)
        issue_date: Union[Unset, CoreFactorDate]
        if isinstance(_issue_date, Unset):
            issue_date = UNSET
        else:
            issue_date = CoreFactorDate.from_dict(_issue_date)

        _maturity_date = d.pop("maturityDate", UNSET)
        maturity_date: Union[Unset, CoreFactorDate]
        if isinstance(_maturity_date, Unset):
            maturity_date = UNSET
        else:
            maturity_date = CoreFactorDate.from_dict(_maturity_date)

        max_cs = d.pop("maxCs", UNSET)

        max_ltv = d.pop("maxLtv", UNSET)

        max_ols = d.pop("maxOls", UNSET)

        max_servicer = d.pop("maxServicer", UNSET)

        max_servicer_pct = d.pop("maxServicerPct", UNSET)

        max_state = d.pop("maxState", UNSET)

        max_state_pct = d.pop("maxStatePct", UNSET)

        min_cs = d.pop("minCs", UNSET)

        min_ltv = d.pop("minLtv", UNSET)

        min_ols = d.pop("minOls", UNSET)

        num_loans = d.pop("numLoans", UNSET)

        orig_story = d.pop("origStory", UNSET)

        orig_story_pct = d.pop("origStoryPct", UNSET)

        pool_number = d.pop("poolNumber", UNSET)

        prefix = d.pop("prefix", UNSET)

        _product = d.pop("product", UNSET)
        product: Union[Unset, MbsProduct]
        if isinstance(_product, Unset):
            product = UNSET
        else:
            product = MbsProduct(_product)

        production_year = d.pop("productionYear", UNSET)

        purch_pct = d.pop("purchPct", UNSET)

        refi_pct = d.pop("refiPct", UNSET)

        smm1 = d.pop("smm1", UNSET)

        upb = d.pop("upb", UNSET)

        wac = d.pop("wac", UNSET)

        wala = d.pop("wala", UNSET)

        wals = d.pop("wals", UNSET)

        wam = d.pop("wam", UNSET)

        waocs = d.pop("waocs", UNSET)

        waols = d.pop("waols", UNSET)

        waoltv = d.pop("waoltv", UNSET)

        pool_v1_pool = cls(
            agency=agency,
            agency_ticker=agency_ticker,
            collateral_type=collateral_type,
            coupon=coupon,
            coupon_type=coupon_type,
            cpr1=cpr1,
            cusip=cusip,
            factor=factor,
            factor_date=factor_date,
            inv_pct=inv_pct,
            iss_num_loans=iss_num_loans,
            iss_upb=iss_upb,
            iss_wac=iss_wac,
            iss_wala=iss_wala,
            issue_date=issue_date,
            maturity_date=maturity_date,
            max_cs=max_cs,
            max_ltv=max_ltv,
            max_ols=max_ols,
            max_servicer=max_servicer,
            max_servicer_pct=max_servicer_pct,
            max_state=max_state,
            max_state_pct=max_state_pct,
            min_cs=min_cs,
            min_ltv=min_ltv,
            min_ols=min_ols,
            num_loans=num_loans,
            orig_story=orig_story,
            orig_story_pct=orig_story_pct,
            pool_number=pool_number,
            prefix=prefix,
            product=product,
            production_year=production_year,
            purch_pct=purch_pct,
            refi_pct=refi_pct,
            smm1=smm1,
            upb=upb,
            wac=wac,
            wala=wala,
            wals=wals,
            wam=wam,
            waocs=waocs,
            waols=waols,
            waoltv=waoltv,
        )

        pool_v1_pool.additional_properties = d
        return pool_v1_pool

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
