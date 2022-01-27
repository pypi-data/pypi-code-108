from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.trading_algo_param_spec import TradingAlgoParamSpec
from ..types import UNSET, Unset

T = TypeVar("T", bound="TradingAlgo")


@attr.s(auto_attribs=True)
class TradingAlgo:
    """Holds code that will be executed each time the Trading Simulator requires an
    input.

    When a user creates an Algo, they define a list of parameters, with their
    names and types. These parameters will be set during the simulation, allowing Algos
    to be reused."""

    id: int
    name: str
    code: str
    author_user_id: int
    description: Union[Unset, str] = ""
    parameters_spec: Union[Unset, List[TradingAlgoParamSpec]] = UNSET
    is_builtin: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        code = self.code
        author_user_id = self.author_user_id
        description = self.description
        parameters_spec: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.parameters_spec, Unset):
            parameters_spec = []
            for parameters_spec_item_data in self.parameters_spec:
                parameters_spec_item = parameters_spec_item_data.to_dict()

                parameters_spec.append(parameters_spec_item)

        is_builtin = self.is_builtin

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "code": code,
                "authorUserId": author_user_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if parameters_spec is not UNSET:
            field_dict["parametersSpec"] = parameters_spec
        if is_builtin is not UNSET:
            field_dict["isBuiltin"] = is_builtin

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        code = d.pop("code")

        author_user_id = d.pop("authorUserId")

        description = d.pop("description", UNSET)

        parameters_spec = []
        _parameters_spec = d.pop("parametersSpec", UNSET)
        for parameters_spec_item_data in _parameters_spec or []:
            parameters_spec_item = TradingAlgoParamSpec.from_dict(parameters_spec_item_data)

            parameters_spec.append(parameters_spec_item)

        is_builtin = d.pop("isBuiltin", UNSET)

        trading_algo = cls(
            id=id,
            name=name,
            code=code,
            author_user_id=author_user_id,
            description=description,
            parameters_spec=parameters_spec,
            is_builtin=is_builtin,
        )

        trading_algo.additional_properties = d
        return trading_algo

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
