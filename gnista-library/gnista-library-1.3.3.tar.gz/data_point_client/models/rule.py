from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.en_operator import EnOperator
from ..types import UNSET, Unset

T = TypeVar("T", bound="Rule")


@attr.s(auto_attribs=True)
class Rule:
    """ """

    number: Union[Unset, float] = UNSET
    op: Union[Unset, EnOperator] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        number = self.number
        op: Union[Unset, str] = UNSET
        if not isinstance(self.op, Unset):
            op = self.op.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if number is not UNSET:
            field_dict["number"] = number
        if op is not UNSET:
            field_dict["op"] = op

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        number = d.pop("number", UNSET)

        _op = d.pop("op", UNSET)
        op: Union[Unset, EnOperator]
        if isinstance(_op, Unset):
            op = UNSET
        else:
            op = EnOperator(_op)

        rule = cls(
            number=number,
            op=op,
        )

        return rule
