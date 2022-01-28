from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.blob_type import BlobType
from ..models.blob_upload_status import BlobUploadStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="Blob")


@attr.s(auto_attribs=True, repr=False)
class Blob:
    """  """

    _id: Union[Unset, str] = UNSET
    _mime_type: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _type: Union[Unset, BlobType] = UNSET
    _upload_status: Union[Unset, BlobUploadStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("mime_type={}".format(repr(self._mime_type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("upload_status={}".format(repr(self._upload_status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Blob({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        mime_type = self._mime_type
        name = self._name
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        upload_status: Union[Unset, int] = UNSET
        if not isinstance(self._upload_status, Unset):
            upload_status = self._upload_status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type
        if name is not UNSET:
            field_dict["name"] = name
        if type is not UNSET:
            field_dict["type"] = type
        if upload_status is not UNSET:
            field_dict["uploadStatus"] = upload_status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_mime_type() -> Union[Unset, str]:
            mime_type = d.pop("mimeType")
            return mime_type

        mime_type = get_mime_type() if "mimeType" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, BlobType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = BlobType(_type)
                except ValueError:
                    type = BlobType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, BlobType], UNSET)

        def get_upload_status() -> Union[Unset, BlobUploadStatus]:
            upload_status = None
            _upload_status = d.pop("uploadStatus")
            if _upload_status is not None and _upload_status is not UNSET:
                try:
                    upload_status = BlobUploadStatus(_upload_status)
                except ValueError:
                    upload_status = BlobUploadStatus.of_unknown(_upload_status)

            return upload_status

        upload_status = (
            get_upload_status() if "uploadStatus" in d else cast(Union[Unset, BlobUploadStatus], UNSET)
        )

        blob = cls(
            id=id,
            mime_type=mime_type,
            name=name,
            type=type,
            upload_status=upload_status,
        )

        blob.additional_properties = d
        return blob

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
    def id(self) -> str:
        """ The universally unique identifier (UUID) for the blob. """
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

    @property
    def name(self) -> str:
        """ Name of the blob """
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
    def type(self) -> BlobType:
        """One of RAW_FILE or VISUALIZATION. If VISUALIZATION, the blob may be displayed as an image preview."""
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: BlobType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def upload_status(self) -> BlobUploadStatus:
        if isinstance(self._upload_status, Unset):
            raise NotPresentError(self, "upload_status")
        return self._upload_status

    @upload_status.setter
    def upload_status(self, value: BlobUploadStatus) -> None:
        self._upload_status = value

    @upload_status.deleter
    def upload_status(self) -> None:
        self._upload_status = UNSET
