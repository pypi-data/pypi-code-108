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
)

from attr import define, field

from infima_client.core.models.mbs.agency_ticker import MbsAgencyTicker
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="MarketV0GetViewRequest")


@define(auto_attribs=True)
class MarketV0GetViewRequest:
    """
    Attributes:
        ticker (Union[Unset, MbsAgencyTicker]):  Default: MbsAgencyTicker.NULL_AGENCY_TICKER.
    """

    ticker: Union[Unset, MbsAgencyTicker] = MbsAgencyTicker.NULL_AGENCY_TICKER
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ticker: Union[Unset, str] = UNSET
        if not isinstance(self.ticker, Unset):
            ticker = self.ticker.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ticker is not UNSET:
            field_dict["ticker"] = ticker

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _ticker = d.pop("ticker", UNSET)
        ticker: Union[Unset, MbsAgencyTicker]
        if isinstance(_ticker, Unset):
            ticker = UNSET
        else:
            ticker = MbsAgencyTicker(_ticker)

        market_v0_get_view_request = cls(
            ticker=ticker,
        )

        market_v0_get_view_request.additional_properties = d
        return market_v0_get_view_request

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
