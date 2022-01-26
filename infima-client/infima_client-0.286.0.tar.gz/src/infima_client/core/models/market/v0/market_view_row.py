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

from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="MarketV0MarketViewRow")


@define(auto_attribs=True)
class MarketV0MarketViewRow:
    """
    Attributes:
        aols (Union[Unset, float]):
        coupon (Union[Unset, float]):
        fico (Union[Unset, float]):
        historical (Union[Unset, List[float]]):
        ls (Union[Unset, float]):
        ltv (Union[Unset, float]):
        predicted (Union[Unset, List[float]]):
        refi (Union[Unset, float]):
        upb (Union[Unset, float]):
        vintage (Union[Unset, int]):
        wac (Union[Unset, float]):
        wala (Union[Unset, float]):
        wam (Union[Unset, float]):
    """

    aols: Union[Unset, float] = UNSET
    coupon: Union[Unset, float] = UNSET
    fico: Union[Unset, float] = UNSET
    historical: Union[Unset, List[float]] = UNSET
    ls: Union[Unset, float] = UNSET
    ltv: Union[Unset, float] = UNSET
    predicted: Union[Unset, List[float]] = UNSET
    refi: Union[Unset, float] = UNSET
    upb: Union[Unset, float] = UNSET
    vintage: Union[Unset, int] = UNSET
    wac: Union[Unset, float] = UNSET
    wala: Union[Unset, float] = UNSET
    wam: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        aols = self.aols
        coupon = self.coupon
        fico = self.fico
        historical: Union[Unset, List[float]] = UNSET
        if not isinstance(self.historical, Unset):
            historical = self.historical

        ls = self.ls
        ltv = self.ltv
        predicted: Union[Unset, List[float]] = UNSET
        if not isinstance(self.predicted, Unset):
            predicted = self.predicted

        refi = self.refi
        upb = self.upb
        vintage = self.vintage
        wac = self.wac
        wala = self.wala
        wam = self.wam

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if aols is not UNSET:
            field_dict["aols"] = aols
        if coupon is not UNSET:
            field_dict["coupon"] = coupon
        if fico is not UNSET:
            field_dict["fico"] = fico
        if historical is not UNSET:
            field_dict["historical"] = historical
        if ls is not UNSET:
            field_dict["ls"] = ls
        if ltv is not UNSET:
            field_dict["ltv"] = ltv
        if predicted is not UNSET:
            field_dict["predicted"] = predicted
        if refi is not UNSET:
            field_dict["refi"] = refi
        if upb is not UNSET:
            field_dict["upb"] = upb
        if vintage is not UNSET:
            field_dict["vintage"] = vintage
        if wac is not UNSET:
            field_dict["wac"] = wac
        if wala is not UNSET:
            field_dict["wala"] = wala
        if wam is not UNSET:
            field_dict["wam"] = wam

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        aols = d.pop("aols", UNSET)

        coupon = d.pop("coupon", UNSET)

        fico = d.pop("fico", UNSET)

        historical = cast(List[float], d.pop("historical", UNSET))

        ls = d.pop("ls", UNSET)

        ltv = d.pop("ltv", UNSET)

        predicted = cast(List[float], d.pop("predicted", UNSET))

        refi = d.pop("refi", UNSET)

        upb = d.pop("upb", UNSET)

        vintage = d.pop("vintage", UNSET)

        wac = d.pop("wac", UNSET)

        wala = d.pop("wala", UNSET)

        wam = d.pop("wam", UNSET)

        market_v0_market_view_row = cls(
            aols=aols,
            coupon=coupon,
            fico=fico,
            historical=historical,
            ls=ls,
            ltv=ltv,
            predicted=predicted,
            refi=refi,
            upb=upb,
            vintage=vintage,
            wac=wac,
            wala=wala,
            wam=wam,
        )

        market_v0_market_view_row.additional_properties = d
        return market_v0_market_view_row

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
