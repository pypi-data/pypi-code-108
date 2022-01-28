import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.aligned_sequence import AlignedSequence
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaAlignment")


@attr.s(auto_attribs=True, repr=False)
class DnaAlignment:
    """  """

    _aligned_sequences: Union[Unset, List[AlignedSequence]] = UNSET
    _api_url: Union[Unset, str] = UNSET
    _created_at: Union[Unset, datetime.datetime] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _name: Union[Unset, str] = UNSET
    _reference_sequence_id: Union[Unset, str] = UNSET
    _web_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("aligned_sequences={}".format(repr(self._aligned_sequences)))
        fields.append("api_url={}".format(repr(self._api_url)))
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("reference_sequence_id={}".format(repr(self._reference_sequence_id)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DnaAlignment({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aligned_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aligned_sequences, Unset):
            aligned_sequences = []
            for aligned_sequences_item_data in self._aligned_sequences:
                aligned_sequences_item = aligned_sequences_item_data.to_dict()

                aligned_sequences.append(aligned_sequences_item)

        api_url = self._api_url
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        name = self._name
        reference_sequence_id = self._reference_sequence_id
        web_url = self._web_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if aligned_sequences is not UNSET:
            field_dict["alignedSequences"] = aligned_sequences
        if api_url is not UNSET:
            field_dict["apiURL"] = api_url
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name
        if reference_sequence_id is not UNSET:
            field_dict["referenceSequenceId"] = reference_sequence_id
        if web_url is not UNSET:
            field_dict["webURL"] = web_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_aligned_sequences() -> Union[Unset, List[AlignedSequence]]:
            aligned_sequences = []
            _aligned_sequences = d.pop("alignedSequences")
            for aligned_sequences_item_data in _aligned_sequences or []:
                aligned_sequences_item = AlignedSequence.from_dict(aligned_sequences_item_data)

                aligned_sequences.append(aligned_sequences_item)

            return aligned_sequences

        aligned_sequences = (
            get_aligned_sequences()
            if "alignedSequences" in d
            else cast(Union[Unset, List[AlignedSequence]], UNSET)
        )

        def get_api_url() -> Union[Unset, str]:
            api_url = d.pop("apiURL")
            return api_url

        api_url = get_api_url() if "apiURL" in d else cast(Union[Unset, str], UNSET)

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_reference_sequence_id() -> Union[Unset, str]:
            reference_sequence_id = d.pop("referenceSequenceId")
            return reference_sequence_id

        reference_sequence_id = (
            get_reference_sequence_id() if "referenceSequenceId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        dna_alignment = cls(
            aligned_sequences=aligned_sequences,
            api_url=api_url,
            created_at=created_at,
            id=id,
            modified_at=modified_at,
            name=name,
            reference_sequence_id=reference_sequence_id,
            web_url=web_url,
        )

        dna_alignment.additional_properties = d
        return dna_alignment

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
    def aligned_sequences(self) -> List[AlignedSequence]:
        if isinstance(self._aligned_sequences, Unset):
            raise NotPresentError(self, "aligned_sequences")
        return self._aligned_sequences

    @aligned_sequences.setter
    def aligned_sequences(self, value: List[AlignedSequence]) -> None:
        self._aligned_sequences = value

    @aligned_sequences.deleter
    def aligned_sequences(self) -> None:
        self._aligned_sequences = UNSET

    @property
    def api_url(self) -> str:
        """ The canonical url of the DNA Alignment in the API. """
        if isinstance(self._api_url, Unset):
            raise NotPresentError(self, "api_url")
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        self._api_url = UNSET

    @property
    def created_at(self) -> datetime.datetime:
        """ DateTime the DNA Alignment was created """
        if isinstance(self._created_at, Unset):
            raise NotPresentError(self, "created_at")
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime.datetime) -> None:
        self._created_at = value

    @created_at.deleter
    def created_at(self) -> None:
        self._created_at = UNSET

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
    def modified_at(self) -> datetime.datetime:
        """ DateTime the DNA Alignment was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

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
    def reference_sequence_id(self) -> str:
        """ The ID of the template or consensus DNA Sequence associated with the DNA Alignment """
        if isinstance(self._reference_sequence_id, Unset):
            raise NotPresentError(self, "reference_sequence_id")
        return self._reference_sequence_id

    @reference_sequence_id.setter
    def reference_sequence_id(self, value: str) -> None:
        self._reference_sequence_id = value

    @reference_sequence_id.deleter
    def reference_sequence_id(self) -> None:
        self._reference_sequence_id = UNSET

    @property
    def web_url(self) -> str:
        """ The Benchling web UI url to view the DNA Alignment """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET
