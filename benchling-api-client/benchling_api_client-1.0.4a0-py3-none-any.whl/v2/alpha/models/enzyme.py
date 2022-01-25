from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="Enzyme")


@attr.s(auto_attribs=True, repr=False)
class Enzyme:
    """  """

    _cutsites: Union[Unset, List[int]] = UNSET
    _id: Union[Unset, str] = UNSET
    _isoschizomers: Union[Unset, List[str]] = UNSET
    _name: Union[Unset, str] = UNSET
    _offsets: Union[Unset, List[int]] = UNSET
    _restriction_site: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("cutsites={}".format(repr(self._cutsites)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("isoschizomers={}".format(repr(self._isoschizomers)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("offsets={}".format(repr(self._offsets)))
        fields.append("restriction_site={}".format(repr(self._restriction_site)))
        return "Enzyme({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        cutsites: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._cutsites, Unset):
            cutsites = self._cutsites

        id = self._id
        isoschizomers: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._isoschizomers, Unset):
            isoschizomers = self._isoschizomers

        name = self._name
        offsets: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._offsets, Unset):
            offsets = self._offsets

        restriction_site = self._restriction_site

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if cutsites is not UNSET:
            field_dict["cutsites"] = cutsites
        if id is not UNSET:
            field_dict["id"] = id
        if isoschizomers is not UNSET:
            field_dict["isoschizomers"] = isoschizomers
        if name is not UNSET:
            field_dict["name"] = name
        if offsets is not UNSET:
            field_dict["offsets"] = offsets
        if restriction_site is not UNSET:
            field_dict["restrictionSite"] = restriction_site

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_cutsites() -> Union[Unset, List[int]]:
            cutsites = cast(List[int], d.pop("cutsites"))

            return cutsites

        cutsites = get_cutsites() if "cutsites" in d else cast(Union[Unset, List[int]], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_isoschizomers() -> Union[Unset, List[str]]:
            isoschizomers = cast(List[str], d.pop("isoschizomers"))

            return isoschizomers

        isoschizomers = get_isoschizomers() if "isoschizomers" in d else cast(Union[Unset, List[str]], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_offsets() -> Union[Unset, List[int]]:
            offsets = cast(List[int], d.pop("offsets"))

            return offsets

        offsets = get_offsets() if "offsets" in d else cast(Union[Unset, List[int]], UNSET)

        def get_restriction_site() -> Union[Unset, str]:
            restriction_site = d.pop("restrictionSite")
            return restriction_site

        restriction_site = (
            get_restriction_site() if "restrictionSite" in d else cast(Union[Unset, str], UNSET)
        )

        enzyme = cls(
            cutsites=cutsites,
            id=id,
            isoschizomers=isoschizomers,
            name=name,
            offsets=offsets,
            restriction_site=restriction_site,
        )

        return enzyme

    @property
    def cutsites(self) -> List[int]:
        if isinstance(self._cutsites, Unset):
            raise NotPresentError(self, "cutsites")
        return self._cutsites

    @cutsites.setter
    def cutsites(self, value: List[int]) -> None:
        self._cutsites = value

    @cutsites.deleter
    def cutsites(self) -> None:
        self._cutsites = UNSET

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def isoschizomers(self) -> List[str]:
        if isinstance(self._isoschizomers, Unset):
            raise NotPresentError(self, "isoschizomers")
        return self._isoschizomers

    @isoschizomers.setter
    def isoschizomers(self, value: List[str]) -> None:
        self._isoschizomers = value

    @isoschizomers.deleter
    def isoschizomers(self) -> None:
        self._isoschizomers = UNSET

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
    def offsets(self) -> List[int]:
        if isinstance(self._offsets, Unset):
            raise NotPresentError(self, "offsets")
        return self._offsets

    @offsets.setter
    def offsets(self, value: List[int]) -> None:
        self._offsets = value

    @offsets.deleter
    def offsets(self) -> None:
        self._offsets = UNSET

    @property
    def restriction_site(self) -> str:
        if isinstance(self._restriction_site, Unset):
            raise NotPresentError(self, "restriction_site")
        return self._restriction_site

    @restriction_site.setter
    def restriction_site(self, value: str) -> None:
        self._restriction_site = value

    @restriction_site.deleter
    def restriction_site(self) -> None:
        self._restriction_site = UNSET
