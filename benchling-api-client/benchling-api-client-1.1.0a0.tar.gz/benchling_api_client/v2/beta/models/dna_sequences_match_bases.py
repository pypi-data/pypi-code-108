from typing import Any, cast, Dict, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_sequences_match_bases_archive_reason import DnaSequencesMatchBasesArchiveReason
from ..models.dna_sequences_match_bases_sort import DnaSequencesMatchBasesSort
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaSequencesMatchBases")


@attr.s(auto_attribs=True, repr=False)
class DnaSequencesMatchBases:
    """  """

    _bases: str
    _archive_reason: Union[
        Unset, DnaSequencesMatchBasesArchiveReason
    ] = DnaSequencesMatchBasesArchiveReason.NOT_ARCHIVED
    _next_token: Union[Unset, str] = UNSET
    _page_size: Union[Unset, int] = 50
    _registry_id: Union[Unset, None, str] = UNSET
    _sort: Union[Unset, DnaSequencesMatchBasesSort] = DnaSequencesMatchBasesSort.MODIFIEDATDESC

    def __repr__(self):
        fields = []
        fields.append("bases={}".format(repr(self._bases)))
        fields.append("archive_reason={}".format(repr(self._archive_reason)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("page_size={}".format(repr(self._page_size)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("sort={}".format(repr(self._sort)))
        return "DnaSequencesMatchBases({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        bases = self._bases
        archive_reason: Union[Unset, int] = UNSET
        if not isinstance(self._archive_reason, Unset):
            archive_reason = self._archive_reason.value

        next_token = self._next_token
        page_size = self._page_size
        registry_id = self._registry_id
        sort: Union[Unset, int] = UNSET
        if not isinstance(self._sort, Unset):
            sort = self._sort.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "bases": bases,
            }
        )
        if archive_reason is not UNSET:
            field_dict["archiveReason"] = archive_reason
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if page_size is not UNSET:
            field_dict["pageSize"] = page_size
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id
        if sort is not UNSET:
            field_dict["sort"] = sort

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_bases() -> str:
            bases = d.pop("bases")
            return bases

        bases = get_bases() if "bases" in d else cast(str, UNSET)

        def get_archive_reason() -> Union[Unset, DnaSequencesMatchBasesArchiveReason]:
            archive_reason = None
            _archive_reason = d.pop("archiveReason")
            if _archive_reason is not None and _archive_reason is not UNSET:
                try:
                    archive_reason = DnaSequencesMatchBasesArchiveReason(_archive_reason)
                except ValueError:
                    archive_reason = DnaSequencesMatchBasesArchiveReason.of_unknown(_archive_reason)

            return archive_reason

        archive_reason = (
            get_archive_reason()
            if "archiveReason" in d
            else cast(Union[Unset, DnaSequencesMatchBasesArchiveReason], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_page_size() -> Union[Unset, int]:
            page_size = d.pop("pageSize")
            return page_size

        page_size = get_page_size() if "pageSize" in d else cast(Union[Unset, int], UNSET)

        def get_registry_id() -> Union[Unset, None, str]:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(Union[Unset, None, str], UNSET)

        def get_sort() -> Union[Unset, DnaSequencesMatchBasesSort]:
            sort = None
            _sort = d.pop("sort")
            if _sort is not None and _sort is not UNSET:
                try:
                    sort = DnaSequencesMatchBasesSort(_sort)
                except ValueError:
                    sort = DnaSequencesMatchBasesSort.of_unknown(_sort)

            return sort

        sort = get_sort() if "sort" in d else cast(Union[Unset, DnaSequencesMatchBasesSort], UNSET)

        dna_sequences_match_bases = cls(
            bases=bases,
            archive_reason=archive_reason,
            next_token=next_token,
            page_size=page_size,
            registry_id=registry_id,
            sort=sort,
        )

        return dna_sequences_match_bases

    @property
    def bases(self) -> str:
        if isinstance(self._bases, Unset):
            raise NotPresentError(self, "bases")
        return self._bases

    @bases.setter
    def bases(self, value: str) -> None:
        self._bases = value

    @property
    def archive_reason(self) -> DnaSequencesMatchBasesArchiveReason:
        if isinstance(self._archive_reason, Unset):
            raise NotPresentError(self, "archive_reason")
        return self._archive_reason

    @archive_reason.setter
    def archive_reason(self, value: DnaSequencesMatchBasesArchiveReason) -> None:
        self._archive_reason = value

    @archive_reason.deleter
    def archive_reason(self) -> None:
        self._archive_reason = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET

    @property
    def page_size(self) -> int:
        if isinstance(self._page_size, Unset):
            raise NotPresentError(self, "page_size")
        return self._page_size

    @page_size.setter
    def page_size(self, value: int) -> None:
        self._page_size = value

    @page_size.deleter
    def page_size(self) -> None:
        self._page_size = UNSET

    @property
    def registry_id(self) -> Optional[str]:
        """ID of a registry. Restricts results to those registered in this registry. Specifying `null` returns unregistered items."""
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: Optional[str]) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET

    @property
    def sort(self) -> DnaSequencesMatchBasesSort:
        if isinstance(self._sort, Unset):
            raise NotPresentError(self, "sort")
        return self._sort

    @sort.setter
    def sort(self, value: DnaSequencesMatchBasesSort) -> None:
        self._sort = value

    @sort.deleter
    def sort(self) -> None:
        self._sort = UNSET
