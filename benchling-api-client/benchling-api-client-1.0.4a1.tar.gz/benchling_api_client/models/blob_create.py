from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.blob_create_type import BlobCreateType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BlobCreate")


@attr.s(auto_attribs=True, repr=False)
class BlobCreate:
    """  """

    _data64: str
    _md5: str
    _name: str
    _type: BlobCreateType
    _mime_type: Union[Unset, str] = "application/octet-stream"

    def __repr__(self):
        fields = []
        fields.append("data64={}".format(repr(self._data64)))
        fields.append("md5={}".format(repr(self._md5)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("mime_type={}".format(repr(self._mime_type)))
        return "BlobCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        data64 = self._data64
        md5 = self._md5
        name = self._name
        type = self._type.value

        mime_type = self._mime_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data64": data64,
                "md5": md5,
                "name": name,
                "type": type,
            }
        )
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_data64() -> str:
            data64 = d.pop("data64")
            return data64

        data64 = get_data64() if "data64" in d else cast(str, UNSET)

        def get_md5() -> str:
            md5 = d.pop("md5")
            return md5

        md5 = get_md5() if "md5" in d else cast(str, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_type() -> BlobCreateType:
            _type = d.pop("type")
            try:
                type = BlobCreateType(_type)
            except ValueError:
                type = BlobCreateType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(BlobCreateType, UNSET)

        def get_mime_type() -> Union[Unset, str]:
            mime_type = d.pop("mimeType")
            return mime_type

        mime_type = get_mime_type() if "mimeType" in d else cast(Union[Unset, str], UNSET)

        blob_create = cls(
            data64=data64,
            md5=md5,
            name=name,
            type=type,
            mime_type=mime_type,
        )

        return blob_create

    @property
    def data64(self) -> str:
        """ base64 encoded file contents """
        if isinstance(self._data64, Unset):
            raise NotPresentError(self, "data64")
        return self._data64

    @data64.setter
    def data64(self, value: str) -> None:
        self._data64 = value

    @property
    def md5(self) -> str:
        """The MD5 hash of the blob part. Note: this should be the hash of the raw data of the blob part, not the hash of the base64 encoding."""
        if isinstance(self._md5, Unset):
            raise NotPresentError(self, "md5")
        return self._md5

    @md5.setter
    def md5(self, value: str) -> None:
        self._md5 = value

    @property
    def name(self) -> str:
        """ Name of the blob """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def type(self) -> BlobCreateType:
        """One of RAW_FILE or VISUALIZATION. If VISUALIZATION, the blob may be displayed as an image preview."""
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: BlobCreateType) -> None:
        self._type = value

    @property
    def mime_type(self) -> str:
        """ eg. application/jpeg """
        if isinstance(self._mime_type, Unset):
            raise NotPresentError(self, "mime_type")
        return self._mime_type

    @mime_type.setter
    def mime_type(self, value: str) -> None:
        self._mime_type = value

    @mime_type.deleter
    def mime_type(self) -> None:
        self._mime_type = UNSET
