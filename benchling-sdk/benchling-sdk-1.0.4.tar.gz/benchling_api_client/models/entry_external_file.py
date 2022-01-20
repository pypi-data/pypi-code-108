from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryExternalFile")


@attr.s(auto_attribs=True, repr=False)
class EntryExternalFile:
    """The ExternalFile resource stores metadata about the file. The actual original file can be downloaded by using the 'downloadURL' property."""

    _download_url: Union[Unset, str] = UNSET
    _expires_at: Union[Unset, int] = UNSET
    _id: Union[Unset, str] = UNSET
    _size: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("download_url={}".format(repr(self._download_url)))
        fields.append("expires_at={}".format(repr(self._expires_at)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("size={}".format(repr(self._size)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryExternalFile({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        download_url = self._download_url
        expires_at = self._expires_at
        id = self._id
        size = self._size

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if download_url is not UNSET:
            field_dict["downloadURL"] = download_url
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at
        if id is not UNSET:
            field_dict["id"] = id
        if size is not UNSET:
            field_dict["size"] = size

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_download_url() -> Union[Unset, str]:
            download_url = d.pop("downloadURL")
            return download_url

        download_url = get_download_url() if "downloadURL" in d else cast(Union[Unset, str], UNSET)

        def get_expires_at() -> Union[Unset, int]:
            expires_at = d.pop("expiresAt")
            return expires_at

        expires_at = get_expires_at() if "expiresAt" in d else cast(Union[Unset, int], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_size() -> Union[Unset, int]:
            size = d.pop("size")
            return size

        size = get_size() if "size" in d else cast(Union[Unset, int], UNSET)

        entry_external_file = cls(
            download_url=download_url,
            expires_at=expires_at,
            id=id,
            size=size,
        )

        entry_external_file.additional_properties = d
        return entry_external_file

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
    def download_url(self) -> str:
        """A short-lived URL that can be used to download the original file."""
        if isinstance(self._download_url, Unset):
            raise NotPresentError(self, "download_url")
        return self._download_url

    @download_url.setter
    def download_url(self, value: str) -> None:
        self._download_url = value

    @download_url.deleter
    def download_url(self) -> None:
        self._download_url = UNSET

    @property
    def expires_at(self) -> int:
        """ UNIX timestamp when downloadURL expires. """
        if isinstance(self._expires_at, Unset):
            raise NotPresentError(self, "expires_at")
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: int) -> None:
        self._expires_at = value

    @expires_at.deleter
    def expires_at(self) -> None:
        self._expires_at = UNSET

    @property
    def id(self) -> str:
        """ ID of the external file """
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
    def size(self) -> int:
        """ Size, in bytes, of the external file """
        if isinstance(self._size, Unset):
            raise NotPresentError(self, "size")
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = value

    @size.deleter
    def size(self) -> None:
        self._size = UNSET
