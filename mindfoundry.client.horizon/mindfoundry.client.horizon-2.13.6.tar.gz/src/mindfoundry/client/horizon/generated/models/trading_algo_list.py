from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.trading_algo import TradingAlgo

T = TypeVar("T", bound="TradingAlgoList")


@attr.s(auto_attribs=True)
class TradingAlgoList:
    """  """

    trading_algos: List[TradingAlgo]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        trading_algos = []
        for trading_algos_item_data in self.trading_algos:
            trading_algos_item = trading_algos_item_data.to_dict()

            trading_algos.append(trading_algos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tradingAlgos": trading_algos,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        trading_algos = []
        _trading_algos = d.pop("tradingAlgos")
        for trading_algos_item_data in _trading_algos:
            trading_algos_item = TradingAlgo.from_dict(trading_algos_item_data)

            trading_algos.append(trading_algos_item)

        trading_algo_list = cls(
            trading_algos=trading_algos,
        )

        trading_algo_list.additional_properties = d
        return trading_algo_list

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
