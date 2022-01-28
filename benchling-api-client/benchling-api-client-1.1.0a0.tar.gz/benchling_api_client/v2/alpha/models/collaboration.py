from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.access_policy import AccessPolicy
from ..models.app_collaborator import AppCollaborator
from ..models.org_membership_collaborator import OrgMembershipCollaborator
from ..models.team_membership_collaborator import TeamMembershipCollaborator
from ..models.user_collaborator import UserCollaborator
from ..types import UNSET, Unset

T = TypeVar("T", bound="Collaboration")


@attr.s(auto_attribs=True, repr=False)
class Collaboration:
    """  """

    _access_policy: Union[Unset, AccessPolicy] = UNSET
    _collaborator: Union[
        Unset,
        OrgMembershipCollaborator,
        TeamMembershipCollaborator,
        UserCollaborator,
        AppCollaborator,
        UnknownType,
    ] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("access_policy={}".format(repr(self._access_policy)))
        fields.append("collaborator={}".format(repr(self._collaborator)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Collaboration({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        access_policy: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._access_policy, Unset):
            access_policy = self._access_policy.to_dict()

        collaborator: Union[Unset, Dict[str, Any]]
        if isinstance(self._collaborator, Unset):
            collaborator = UNSET
        elif isinstance(self._collaborator, UnknownType):
            collaborator = self._collaborator.value
        elif isinstance(self._collaborator, OrgMembershipCollaborator):
            collaborator = UNSET
            if not isinstance(self._collaborator, Unset):
                collaborator = self._collaborator.to_dict()

        elif isinstance(self._collaborator, TeamMembershipCollaborator):
            collaborator = UNSET
            if not isinstance(self._collaborator, Unset):
                collaborator = self._collaborator.to_dict()

        elif isinstance(self._collaborator, UserCollaborator):
            collaborator = UNSET
            if not isinstance(self._collaborator, Unset):
                collaborator = self._collaborator.to_dict()

        else:
            collaborator = UNSET
            if not isinstance(self._collaborator, Unset):
                collaborator = self._collaborator.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access_policy is not UNSET:
            field_dict["accessPolicy"] = access_policy
        if collaborator is not UNSET:
            field_dict["collaborator"] = collaborator

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_access_policy() -> Union[Unset, AccessPolicy]:
            access_policy: Union[Unset, AccessPolicy] = UNSET
            _access_policy = d.pop("accessPolicy")
            if not isinstance(_access_policy, Unset):
                access_policy = AccessPolicy.from_dict(_access_policy)

            return access_policy

        access_policy = (
            get_access_policy() if "accessPolicy" in d else cast(Union[Unset, AccessPolicy], UNSET)
        )

        def get_collaborator() -> Union[
            Unset,
            OrgMembershipCollaborator,
            TeamMembershipCollaborator,
            UserCollaborator,
            AppCollaborator,
            UnknownType,
        ]:
            def _parse_collaborator(
                data: Union[Unset, Dict[str, Any]]
            ) -> Union[
                Unset,
                OrgMembershipCollaborator,
                TeamMembershipCollaborator,
                UserCollaborator,
                AppCollaborator,
                UnknownType,
            ]:
                collaborator: Union[
                    Unset,
                    OrgMembershipCollaborator,
                    TeamMembershipCollaborator,
                    UserCollaborator,
                    AppCollaborator,
                    UnknownType,
                ]
                if isinstance(data, Unset):
                    return data
                discriminator_value: str = cast(str, data.get("type"))
                if discriminator_value is not None:
                    if discriminator_value == "ORGANIZATION_MEMBER":
                        collaborator = UNSET
                        _collaborator = data
                        if not isinstance(_collaborator, Unset):
                            collaborator = OrgMembershipCollaborator.from_dict(_collaborator)

                        return collaborator
                    if discriminator_value == "TEAM_MEMBER":
                        collaborator = UNSET
                        _collaborator = data
                        if not isinstance(_collaborator, Unset):
                            collaborator = TeamMembershipCollaborator.from_dict(_collaborator)

                        return collaborator
                    if discriminator_value == "USER":
                        collaborator = UNSET
                        _collaborator = data
                        if not isinstance(_collaborator, Unset):
                            collaborator = UserCollaborator.from_dict(_collaborator)

                        return collaborator
                    if discriminator_value == "APP":
                        collaborator = UNSET
                        _collaborator = data
                        if not isinstance(_collaborator, Unset):
                            collaborator = AppCollaborator.from_dict(_collaborator)

                        return collaborator

                    return UnknownType(value=data)
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    collaborator = UNSET
                    _collaborator = data
                    if not isinstance(_collaborator, Unset):
                        collaborator = OrgMembershipCollaborator.from_dict(_collaborator)

                    return collaborator
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    collaborator = UNSET
                    _collaborator = data
                    if not isinstance(_collaborator, Unset):
                        collaborator = TeamMembershipCollaborator.from_dict(_collaborator)

                    return collaborator
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    collaborator = UNSET
                    _collaborator = data
                    if not isinstance(_collaborator, Unset):
                        collaborator = UserCollaborator.from_dict(_collaborator)

                    return collaborator
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    collaborator = UNSET
                    _collaborator = data
                    if not isinstance(_collaborator, Unset):
                        collaborator = AppCollaborator.from_dict(_collaborator)

                    return collaborator
                except:  # noqa: E722
                    pass
                return UnknownType(data)

            collaborator = _parse_collaborator(d.pop("collaborator"))

            return collaborator

        collaborator = (
            get_collaborator()
            if "collaborator" in d
            else cast(
                Union[
                    Unset,
                    OrgMembershipCollaborator,
                    TeamMembershipCollaborator,
                    UserCollaborator,
                    AppCollaborator,
                    UnknownType,
                ],
                UNSET,
            )
        )

        collaboration = cls(
            access_policy=access_policy,
            collaborator=collaborator,
        )

        collaboration.additional_properties = d
        return collaboration

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
    def access_policy(self) -> AccessPolicy:
        if isinstance(self._access_policy, Unset):
            raise NotPresentError(self, "access_policy")
        return self._access_policy

    @access_policy.setter
    def access_policy(self, value: AccessPolicy) -> None:
        self._access_policy = value

    @access_policy.deleter
    def access_policy(self) -> None:
        self._access_policy = UNSET

    @property
    def collaborator(
        self,
    ) -> Union[
        OrgMembershipCollaborator, TeamMembershipCollaborator, UserCollaborator, AppCollaborator, UnknownType
    ]:
        if isinstance(self._collaborator, Unset):
            raise NotPresentError(self, "collaborator")
        return self._collaborator

    @collaborator.setter
    def collaborator(
        self,
        value: Union[
            OrgMembershipCollaborator,
            TeamMembershipCollaborator,
            UserCollaborator,
            AppCollaborator,
            UnknownType,
        ],
    ) -> None:
        self._collaborator = value

    @collaborator.deleter
    def collaborator(self) -> None:
        self._collaborator = UNSET
