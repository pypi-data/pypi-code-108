from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Sense")


@attr.s(auto_attribs=True)
class Sense:
    """ """

    pageid: Union[Unset, str] = UNSET
    preferred: Union[Unset, str] = UNSET
    prob_c: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        pageid = self.pageid
        preferred = self.preferred
        prob_c = self.prob_c

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if pageid is not UNSET:
            field_dict["pageid"] = pageid
        if preferred is not UNSET:
            field_dict["preferred"] = preferred
        if prob_c is not UNSET:
            field_dict["prob_c"] = prob_c

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pageid = d.pop("pageid", UNSET)

        preferred = d.pop("preferred", UNSET)

        prob_c = d.pop("prob_c", UNSET)

        sense = cls(
            pageid=pageid,
            preferred=preferred,
            prob_c=prob_c,
        )

        return sense
