from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.algo_execution_symbol import AlgoExecutionSymbol

T = TypeVar("T", bound="AlgoSymbolsList")


@attr.s(auto_attribs=True)
class AlgoSymbolsList:
    """  """

    symbols: List[AlgoExecutionSymbol]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        symbols = []
        for symbols_item_data in self.symbols:
            symbols_item = symbols_item_data.to_dict()

            symbols.append(symbols_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "symbols": symbols,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        symbols = []
        _symbols = d.pop("symbols")
        for symbols_item_data in _symbols:
            symbols_item = AlgoExecutionSymbol.from_dict(symbols_item_data)

            symbols.append(symbols_item)

        algo_symbols_list = cls(
            symbols=symbols,
        )

        algo_symbols_list.additional_properties = d
        return algo_symbols_list

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
