from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.translation_regions_item import TranslationRegionsItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="Translation")


@attr.s(auto_attribs=True, repr=False)
class Translation:
    """  """

    _amino_acids: Union[Unset, str] = UNSET
    _end: Union[Unset, int] = UNSET
    _regions: Union[Unset, List[TranslationRegionsItem]] = UNSET
    _start: Union[Unset, int] = UNSET
    _strand: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("amino_acids={}".format(repr(self._amino_acids)))
        fields.append("end={}".format(repr(self._end)))
        fields.append("regions={}".format(repr(self._regions)))
        fields.append("start={}".format(repr(self._start)))
        fields.append("strand={}".format(repr(self._strand)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Translation({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        amino_acids = self._amino_acids
        end = self._end
        regions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._regions, Unset):
            regions = []
            for regions_item_data in self._regions:
                regions_item = regions_item_data.to_dict()

                regions.append(regions_item)

        start = self._start
        strand = self._strand

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if amino_acids is not UNSET:
            field_dict["aminoAcids"] = amino_acids
        if end is not UNSET:
            field_dict["end"] = end
        if regions is not UNSET:
            field_dict["regions"] = regions
        if start is not UNSET:
            field_dict["start"] = start
        if strand is not UNSET:
            field_dict["strand"] = strand

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_amino_acids() -> Union[Unset, str]:
            amino_acids = d.pop("aminoAcids")
            return amino_acids

        amino_acids = get_amino_acids() if "aminoAcids" in d else cast(Union[Unset, str], UNSET)

        def get_end() -> Union[Unset, int]:
            end = d.pop("end")
            return end

        end = get_end() if "end" in d else cast(Union[Unset, int], UNSET)

        def get_regions() -> Union[Unset, List[TranslationRegionsItem]]:
            regions = []
            _regions = d.pop("regions")
            for regions_item_data in _regions or []:
                regions_item = TranslationRegionsItem.from_dict(regions_item_data)

                regions.append(regions_item)

            return regions

        regions = get_regions() if "regions" in d else cast(Union[Unset, List[TranslationRegionsItem]], UNSET)

        def get_start() -> Union[Unset, int]:
            start = d.pop("start")
            return start

        start = get_start() if "start" in d else cast(Union[Unset, int], UNSET)

        def get_strand() -> Union[Unset, int]:
            strand = d.pop("strand")
            return strand

        strand = get_strand() if "strand" in d else cast(Union[Unset, int], UNSET)

        translation = cls(
            amino_acids=amino_acids,
            end=end,
            regions=regions,
            start=start,
            strand=strand,
        )

        translation.additional_properties = d
        return translation

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
    def amino_acids(self) -> str:
        if isinstance(self._amino_acids, Unset):
            raise NotPresentError(self, "amino_acids")
        return self._amino_acids

    @amino_acids.setter
    def amino_acids(self, value: str) -> None:
        self._amino_acids = value

    @amino_acids.deleter
    def amino_acids(self) -> None:
        self._amino_acids = UNSET

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
    def regions(self) -> List[TranslationRegionsItem]:
        if isinstance(self._regions, Unset):
            raise NotPresentError(self, "regions")
        return self._regions

    @regions.setter
    def regions(self, value: List[TranslationRegionsItem]) -> None:
        self._regions = value

    @regions.deleter
    def regions(self) -> None:
        self._regions = UNSET

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
