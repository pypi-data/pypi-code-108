import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError, UnknownType
from ..models.organization import Organization
from ..models.user_summary import UserSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureLibrary")


@attr.s(auto_attribs=True, repr=False)
class FeatureLibrary:
    """  """

    _created_at: Union[Unset, datetime.datetime] = UNSET
    _description: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _name: Union[Unset, str] = UNSET
    _owner: Union[Unset, Organization, UserSummary, UnknownType] = UNSET
    _web_url: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("created_at={}".format(repr(self._created_at)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("owner={}".format(repr(self._owner)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FeatureLibrary({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self._created_at, Unset):
            created_at = self._created_at.isoformat()

        description = self._description
        id = self._id
        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        name = self._name
        owner: Union[Unset, Dict[str, Any]]
        if isinstance(self._owner, Unset):
            owner = UNSET
        elif isinstance(self._owner, UnknownType):
            owner = self._owner.value
        elif isinstance(self._owner, Organization):
            owner = UNSET
            if not isinstance(self._owner, Unset):
                owner = self._owner.to_dict()

        else:
            owner = UNSET
            if not isinstance(self._owner, Unset):
                owner = self._owner.to_dict()

        web_url = self._web_url

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if name is not UNSET:
            field_dict["name"] = name
        if owner is not UNSET:
            field_dict["owner"] = owner
        if web_url is not UNSET:
            field_dict["webURL"] = web_url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_created_at() -> Union[Unset, datetime.datetime]:
            created_at: Union[Unset, datetime.datetime] = UNSET
            _created_at = d.pop("createdAt")
            if _created_at is not None and not isinstance(_created_at, Unset):
                created_at = isoparse(cast(str, _created_at))

            return created_at

        created_at = get_created_at() if "createdAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_description() -> Union[Unset, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, str], UNSET)

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

        def get_owner() -> Union[Unset, Organization, UserSummary, UnknownType]:
            def _parse_owner(
                data: Union[Unset, Dict[str, Any]]
            ) -> Union[Unset, Organization, UserSummary, UnknownType]:
                owner: Union[Unset, Organization, UserSummary, UnknownType]
                if isinstance(data, Unset):
                    return data
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    owner = UNSET
                    _owner = data
                    if not isinstance(_owner, Unset):
                        owner = Organization.from_dict(_owner)

                    return owner
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    owner = UNSET
                    _owner = data
                    if not isinstance(_owner, Unset):
                        owner = UserSummary.from_dict(_owner)

                    return owner
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            owner = _parse_owner(d.pop("owner"))

            return owner

        owner = (
            get_owner() if "owner" in d else cast(Union[Unset, Organization, UserSummary, UnknownType], UNSET)
        )

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        feature_library = cls(
            created_at=created_at,
            description=description,
            id=id,
            modified_at=modified_at,
            name=name,
            owner=owner,
            web_url=web_url,
        )

        feature_library.additional_properties = d
        return feature_library

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
    def created_at(self) -> datetime.datetime:
        """ DateTime the Feature Library was created """
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
    def description(self) -> str:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET

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
        """ DateTime the Feature Library was last modified """
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
    def owner(self) -> Union[Organization, UserSummary, UnknownType]:
        if isinstance(self._owner, Unset):
            raise NotPresentError(self, "owner")
        return self._owner

    @owner.setter
    def owner(self, value: Union[Organization, UserSummary, UnknownType]) -> None:
        self._owner = value

    @owner.deleter
    def owner(self) -> None:
        self._owner = UNSET

    @property
    def web_url(self) -> str:
        """ The Benchling web UI url to view the Feature Library """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET
