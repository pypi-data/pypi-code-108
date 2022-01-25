from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="Primer")


@attr.s(auto_attribs=True, repr=False)
class Primer:
    """  """

    _bases: Union[Unset, str] = UNSET
    _bind_position: Union[Unset, int] = UNSET
    _color: Union[Unset, str] = UNSET
    _end: Union[Unset, int] = UNSET
    _name: Union[Unset, str] = UNSET
    _oligo_id: Union[Unset, str] = UNSET
    _overhang_length: Union[Unset, int] = UNSET
    _start: Union[Unset, int] = UNSET
    _strand: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("bases={}".format(repr(self._bases)))
        fields.append("bind_position={}".format(repr(self._bind_position)))
        fields.append("color={}".format(repr(self._color)))
        fields.append("end={}".format(repr(self._end)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("oligo_id={}".format(repr(self._oligo_id)))
        fields.append("overhang_length={}".format(repr(self._overhang_length)))
        fields.append("start={}".format(repr(self._start)))
        fields.append("strand={}".format(repr(self._strand)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Primer({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        bases = self._bases
        bind_position = self._bind_position
        color = self._color
        end = self._end
        name = self._name
        oligo_id = self._oligo_id
        overhang_length = self._overhang_length
        start = self._start
        strand = self._strand

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bases is not UNSET:
            field_dict["bases"] = bases
        if bind_position is not UNSET:
            field_dict["bindPosition"] = bind_position
        if color is not UNSET:
            field_dict["color"] = color
        if end is not UNSET:
            field_dict["end"] = end
        if name is not UNSET:
            field_dict["name"] = name
        if oligo_id is not UNSET:
            field_dict["oligoId"] = oligo_id
        if overhang_length is not UNSET:
            field_dict["overhangLength"] = overhang_length
        if start is not UNSET:
            field_dict["start"] = start
        if strand is not UNSET:
            field_dict["strand"] = strand

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_bases() -> Union[Unset, str]:
            bases = d.pop("bases")
            return bases

        bases = get_bases() if "bases" in d else cast(Union[Unset, str], UNSET)

        def get_bind_position() -> Union[Unset, int]:
            bind_position = d.pop("bindPosition")
            return bind_position

        bind_position = get_bind_position() if "bindPosition" in d else cast(Union[Unset, int], UNSET)

        def get_color() -> Union[Unset, str]:
            color = d.pop("color")
            return color

        color = get_color() if "color" in d else cast(Union[Unset, str], UNSET)

        def get_end() -> Union[Unset, int]:
            end = d.pop("end")
            return end

        end = get_end() if "end" in d else cast(Union[Unset, int], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_oligo_id() -> Union[Unset, str]:
            oligo_id = d.pop("oligoId")
            return oligo_id

        oligo_id = get_oligo_id() if "oligoId" in d else cast(Union[Unset, str], UNSET)

        def get_overhang_length() -> Union[Unset, int]:
            overhang_length = d.pop("overhangLength")
            return overhang_length

        overhang_length = get_overhang_length() if "overhangLength" in d else cast(Union[Unset, int], UNSET)

        def get_start() -> Union[Unset, int]:
            start = d.pop("start")
            return start

        start = get_start() if "start" in d else cast(Union[Unset, int], UNSET)

        def get_strand() -> Union[Unset, int]:
            strand = d.pop("strand")
            return strand

        strand = get_strand() if "strand" in d else cast(Union[Unset, int], UNSET)

        primer = cls(
            bases=bases,
            bind_position=bind_position,
            color=color,
            end=end,
            name=name,
            oligo_id=oligo_id,
            overhang_length=overhang_length,
            start=start,
            strand=strand,
        )

        primer.additional_properties = d
        return primer

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def bases(self) -> str:
        if isinstance(self._bases, Unset):
            raise NotPresentError(self, "bases")
        return self._bases

    @bases.setter
    def bases(self, value: str) -> None:
        self._bases = value

    @bases.deleter
    def bases(self) -> None:
        self._bases = UNSET

    @property
    def bind_position(self) -> int:
        if isinstance(self._bind_position, Unset):
            raise NotPresentError(self, "bind_position")
        return self._bind_position

    @bind_position.setter
    def bind_position(self, value: int) -> None:
        self._bind_position = value

    @bind_position.deleter
    def bind_position(self) -> None:
        self._bind_position = UNSET

    @property
    def color(self) -> str:
        if isinstance(self._color, Unset):
            raise NotPresentError(self, "color")
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color = value

    @color.deleter
    def color(self) -> None:
        self._color = UNSET

    @property
    def end(self) -> int:
        if isinstance(self._end, Unset):
            raise NotPresentError(self, "end")
        return self._end

    @end.setter
    def end(self, value: int) -> None:
        self._end = value

    @end.deleter
    def end(self) -> None:
        self._end = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def oligo_id(self) -> str:
        if isinstance(self._oligo_id, Unset):
            raise NotPresentError(self, "oligo_id")
        return self._oligo_id

    @oligo_id.setter
    def oligo_id(self, value: str) -> None:
        self._oligo_id = value

    @oligo_id.deleter
    def oligo_id(self) -> None:
        self._oligo_id = UNSET

    @property
    def overhang_length(self) -> int:
        if isinstance(self._overhang_length, Unset):
            raise NotPresentError(self, "overhang_length")
        return self._overhang_length

    @overhang_length.setter
    def overhang_length(self, value: int) -> None:
        self._overhang_length = value

    @overhang_length.deleter
    def overhang_length(self) -> None:
        self._overhang_length = UNSET

    @property
    def start(self) -> int:
        if isinstance(self._start, Unset):
            raise NotPresentError(self, "start")
        return self._start

    @start.setter
    def start(self, value: int) -> None:
        self._start = value

    @start.deleter
    def start(self) -> None:
        self._start = UNSET

    @property
    def strand(self) -> int:
        if isinstance(self._strand, Unset):
            raise NotPresentError(self, "strand")
        return self._strand

    @strand.setter
    def strand(self, value: int) -> None:
        self._strand = value

    @strand.deleter
    def strand(self) -> None:
        self._strand = UNSET
