from typing import Any, cast, Dict, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_sequences_match_bases_archive_reason import AaSequencesMatchBasesArchiveReason
from ..models.aa_sequences_match_bases_sort import AaSequencesMatchBasesSort
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaSequencesMatchBases")


@attr.s(auto_attribs=True, repr=False)
class AaSequencesMatchBases:
    """  """

    _amino_acids: str
    _archive_reason: Union[
        Unset, AaSequencesMatchBasesArchiveReason
    ] = AaSequencesMatchBasesArchiveReason.NOT_ARCHIVED
    _next_token: Union[Unset, str] = UNSET
    _page_size: Union[Unset, int] = 50
    _registry_id: Union[Unset, None, str] = UNSET
    _sort: Union[Unset, AaSequencesMatchBasesSort] = AaSequencesMatchBasesSort.MODIFIEDATDESC

    def __repr__(self):
        fields = []
        fields.append("amino_acids={}".format(repr(self._amino_acids)))
        fields.append("archive_reason={}".format(repr(self._archive_reason)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("page_size={}".format(repr(self._page_size)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("sort={}".format(repr(self._sort)))
        return "AaSequencesMatchBases({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        amino_acids = self._amino_acids
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
                "aminoAcids": amino_acids,
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

        def get_amino_acids() -> str:
            amino_acids = d.pop("aminoAcids")
            return amino_acids

        amino_acids = get_amino_acids() if "aminoAcids" in d else cast(str, UNSET)

        def get_archive_reason() -> Union[Unset, AaSequencesMatchBasesArchiveReason]:
            archive_reason = None
            _archive_reason = d.pop("archiveReason")
            if _archive_reason is not None and _archive_reason is not UNSET:
                try:
                    archive_reason = AaSequencesMatchBasesArchiveReason(_archive_reason)
                except ValueError:
                    archive_reason = AaSequencesMatchBasesArchiveReason.of_unknown(_archive_reason)

            return archive_reason

        archive_reason = (
            get_archive_reason()
            if "archiveReason" in d
            else cast(Union[Unset, AaSequencesMatchBasesArchiveReason], UNSET)
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

        def get_sort() -> Union[Unset, AaSequencesMatchBasesSort]:
            sort = None
            _sort = d.pop("sort")
            if _sort is not None and _sort is not UNSET:
                try:
                    sort = AaSequencesMatchBasesSort(_sort)
                except ValueError:
                    sort = AaSequencesMatchBasesSort.of_unknown(_sort)

            return sort

        sort = get_sort() if "sort" in d else cast(Union[Unset, AaSequencesMatchBasesSort], UNSET)

        aa_sequences_match_bases = cls(
            amino_acids=amino_acids,
            archive_reason=archive_reason,
            next_token=next_token,
            page_size=page_size,
            registry_id=registry_id,
            sort=sort,
        )

        return aa_sequences_match_bases

    @property
    def amino_acids(self) -> str:
        if isinstance(self._amino_acids, Unset):
            raise NotPresentError(self, "amino_acids")
        return self._amino_acids

    @amino_acids.setter
    def amino_acids(self, value: str) -> None:
        self._amino_acids = value

    @property
    def archive_reason(self) -> AaSequencesMatchBasesArchiveReason:
        if isinstance(self._archive_reason, Unset):
            raise NotPresentError(self, "archive_reason")
        return self._archive_reason

    @archive_reason.setter
    def archive_reason(self, value: AaSequencesMatchBasesArchiveReason) -> None:
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
    def sort(self) -> AaSequencesMatchBasesSort:
        if isinstance(self._sort, Unset):
            raise NotPresentError(self, "sort")
        return self._sort

    @sort.setter
    def sort(self, value: AaSequencesMatchBasesSort) -> None:
        self._sort = value

    @sort.deleter
    def sort(self) -> None:
        self._sort = UNSET
