from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.organization_summary import OrganizationSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="Team")


@attr.s(auto_attribs=True, repr=False)
class Team:
    """  """

    _organization: Union[Unset, OrganizationSummary] = UNSET
    _handle: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("organization={}".format(repr(self._organization)))
        fields.append("handle={}".format(repr(self._handle)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Team({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        organization: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._organization, Unset):
            organization = self._organization.to_dict()

        handle = self._handle
        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if organization is not UNSET:
            field_dict["organization"] = organization
        if handle is not UNSET:
            field_dict["handle"] = handle
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_organization() -> Union[Unset, OrganizationSummary]:
            organization: Union[Unset, OrganizationSummary] = UNSET
            _organization = d.pop("organization")
            if not isinstance(_organization, Unset):
                organization = OrganizationSummary.from_dict(_organization)

            return organization

        organization = (
            get_organization() if "organization" in d else cast(Union[Unset, OrganizationSummary], UNSET)
        )

        def get_handle() -> Union[Unset, str]:
            handle = d.pop("handle")
            return handle

        handle = get_handle() if "handle" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        team = cls(
            organization=organization,
            handle=handle,
            id=id,
            name=name,
        )

        team.additional_properties = d
        return team

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
    def organization(self) -> OrganizationSummary:
        if isinstance(self._organization, Unset):
            raise NotPresentError(self, "organization")
        return self._organization

    @organization.setter
    def organization(self, value: OrganizationSummary) -> None:
        self._organization = value

    @organization.deleter
    def organization(self) -> None:
        self._organization = UNSET

    @property
    def handle(self) -> str:
        if isinstance(self._handle, Unset):
            raise NotPresentError(self, "handle")
        return self._handle

    @handle.setter
    def handle(self, value: str) -> None:
        self._handle = value

    @handle.deleter
    def handle(self) -> None:
        self._handle = UNSET

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
