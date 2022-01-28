from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.org_membership_collaborator_role import OrgMembershipCollaboratorRole
from ..models.org_membership_collaborator_type import OrgMembershipCollaboratorType
from ..models.organization_summary import OrganizationSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrgMembershipCollaborator")


@attr.s(auto_attribs=True, repr=False)
class OrgMembershipCollaborator:
    """  """

    _organization: Union[Unset, OrganizationSummary] = UNSET
    _role: Union[Unset, OrgMembershipCollaboratorRole] = UNSET
    _type: Union[Unset, OrgMembershipCollaboratorType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("organization={}".format(repr(self._organization)))
        fields.append("role={}".format(repr(self._role)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "OrgMembershipCollaborator({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        organization: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._organization, Unset):
            organization = self._organization.to_dict()

        role: Union[Unset, int] = UNSET
        if not isinstance(self._role, Unset):
            role = self._role.value

        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if organization is not UNSET:
            field_dict["organization"] = organization
        if role is not UNSET:
            field_dict["role"] = role
        if type is not UNSET:
            field_dict["type"] = type

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

        def get_role() -> Union[Unset, OrgMembershipCollaboratorRole]:
            role = None
            _role = d.pop("role")
            if _role is not None and _role is not UNSET:
                try:
                    role = OrgMembershipCollaboratorRole(_role)
                except ValueError:
                    role = OrgMembershipCollaboratorRole.of_unknown(_role)

            return role

        role = get_role() if "role" in d else cast(Union[Unset, OrgMembershipCollaboratorRole], UNSET)

        def get_type() -> Union[Unset, OrgMembershipCollaboratorType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = OrgMembershipCollaboratorType(_type)
                except ValueError:
                    type = OrgMembershipCollaboratorType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, OrgMembershipCollaboratorType], UNSET)

        org_membership_collaborator = cls(
            organization=organization,
            role=role,
            type=type,
        )

        org_membership_collaborator.additional_properties = d
        return org_membership_collaborator

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
    def role(self) -> OrgMembershipCollaboratorRole:
        if isinstance(self._role, Unset):
            raise NotPresentError(self, "role")
        return self._role

    @role.setter
    def role(self, value: OrgMembershipCollaboratorRole) -> None:
        self._role = value

    @role.deleter
    def role(self) -> None:
        self._role = UNSET

    @property
    def type(self) -> OrgMembershipCollaboratorType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: OrgMembershipCollaboratorType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
