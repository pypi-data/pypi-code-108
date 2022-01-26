from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreationOrigin")


@attr.s(auto_attribs=True, repr=False)
class CreationOrigin:
    """  """

    _application: Union[Unset, None, str] = UNSET
    _origin_id: Union[Unset, None, str] = UNSET
    _origin_modal_uuid: Union[Unset, None, str] = UNSET
    _origin_type: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("application={}".format(repr(self._application)))
        fields.append("origin_id={}".format(repr(self._origin_id)))
        fields.append("origin_modal_uuid={}".format(repr(self._origin_modal_uuid)))
        fields.append("origin_type={}".format(repr(self._origin_type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CreationOrigin({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        application = self._application
        origin_id = self._origin_id
        origin_modal_uuid = self._origin_modal_uuid
        origin_type = self._origin_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if application is not UNSET:
            field_dict["application"] = application
        if origin_id is not UNSET:
            field_dict["originId"] = origin_id
        if origin_modal_uuid is not UNSET:
            field_dict["originModalUuid"] = origin_modal_uuid
        if origin_type is not UNSET:
            field_dict["originType"] = origin_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_application() -> Union[Unset, None, str]:
            application = d.pop("application")
            return application

        application = get_application() if "application" in d else cast(Union[Unset, None, str], UNSET)

        def get_origin_id() -> Union[Unset, None, str]:
            origin_id = d.pop("originId")
            return origin_id

        origin_id = get_origin_id() if "originId" in d else cast(Union[Unset, None, str], UNSET)

        def get_origin_modal_uuid() -> Union[Unset, None, str]:
            origin_modal_uuid = d.pop("originModalUuid")
            return origin_modal_uuid

        origin_modal_uuid = (
            get_origin_modal_uuid() if "originModalUuid" in d else cast(Union[Unset, None, str], UNSET)
        )

        def get_origin_type() -> Union[Unset, None, str]:
            origin_type = d.pop("originType")
            return origin_type

        origin_type = get_origin_type() if "originType" in d else cast(Union[Unset, None, str], UNSET)

        creation_origin = cls(
            application=application,
            origin_id=origin_id,
            origin_modal_uuid=origin_modal_uuid,
            origin_type=origin_type,
        )

        creation_origin.additional_properties = d
        return creation_origin

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
    def application(self) -> Optional[str]:
        if isinstance(self._application, Unset):
            raise NotPresentError(self, "application")
        return self._application

    @application.setter
    def application(self, value: Optional[str]) -> None:
        self._application = value

    @application.deleter
    def application(self) -> None:
        self._application = UNSET

    @property
    def origin_id(self) -> Optional[str]:
        if isinstance(self._origin_id, Unset):
            raise NotPresentError(self, "origin_id")
        return self._origin_id

    @origin_id.setter
    def origin_id(self, value: Optional[str]) -> None:
        self._origin_id = value

    @origin_id.deleter
    def origin_id(self) -> None:
        self._origin_id = UNSET

    @property
    def origin_modal_uuid(self) -> Optional[str]:
        if isinstance(self._origin_modal_uuid, Unset):
            raise NotPresentError(self, "origin_modal_uuid")
        return self._origin_modal_uuid

    @origin_modal_uuid.setter
    def origin_modal_uuid(self, value: Optional[str]) -> None:
        self._origin_modal_uuid = value

    @origin_modal_uuid.deleter
    def origin_modal_uuid(self) -> None:
        self._origin_modal_uuid = UNSET

    @property
    def origin_type(self) -> Optional[str]:
        if isinstance(self._origin_type, Unset):
            raise NotPresentError(self, "origin_type")
        return self._origin_type

    @origin_type.setter
    def origin_type(self, value: Optional[str]) -> None:
        self._origin_type = value

    @origin_type.deleter
    def origin_type(self) -> None:
        self._origin_type = UNSET
