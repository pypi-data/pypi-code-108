from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="BoundingBox")


@attr.s(auto_attribs=True)
class BoundingBox:
    """ """

    p: Union[Unset, int] = UNSET
    x: Union[Unset, float] = UNSET
    y: Union[Unset, float] = UNSET
    w: Union[Unset, float] = UNSET
    h: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        p = self.p
        x = self.x
        y = self.y
        w = self.w
        h = self.h

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if p is not UNSET:
            field_dict["p"] = p
        if x is not UNSET:
            field_dict["x"] = x
        if y is not UNSET:
            field_dict["y"] = y
        if w is not UNSET:
            field_dict["w"] = w
        if h is not UNSET:
            field_dict["h"] = h

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        p = d.pop("p", UNSET)

        x = d.pop("x", UNSET)

        y = d.pop("y", UNSET)

        w = d.pop("w", UNSET)

        h = d.pop("h", UNSET)

        bounding_box = cls(
            p=p,
            x=x,
            y=y,
            w=w,
            h=h,
        )

        return bounding_box
