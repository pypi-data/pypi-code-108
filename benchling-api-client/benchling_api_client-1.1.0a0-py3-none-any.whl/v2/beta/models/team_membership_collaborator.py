from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.team_membership_collaborator_role import TeamMembershipCollaboratorRole
from ..models.team_membership_collaborator_type import TeamMembershipCollaboratorType
from ..models.team_summary import TeamSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="TeamMembershipCollaborator")


@attr.s(auto_attribs=True, repr=False)
class TeamMembershipCollaborator:
    """  """

    _role: Union[Unset, TeamMembershipCollaboratorRole] = UNSET
    _team: Union[Unset, TeamSummary] = UNSET
    _type: Union[Unset, TeamMembershipCollaboratorType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("role={}".format(repr(self._role)))
        fields.append("team={}".format(repr(self._team)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TeamMembershipCollaborator({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        role: Union[Unset, int] = UNSET
        if not isinstance(self._role, Unset):
            role = self._role.value

        team: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._team, Unset):
            team = self._team.to_dict()

        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if role is not UNSET:
            field_dict["role"] = role
        if team is not UNSET:
            field_dict["team"] = team
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_role() -> Union[Unset, TeamMembershipCollaboratorRole]:
            role = None
            _role = d.pop("role")
            if _role is not None and _role is not UNSET:
                try:
                    role = TeamMembershipCollaboratorRole(_role)
                except ValueError:
                    role = TeamMembershipCollaboratorRole.of_unknown(_role)

            return role

        role = get_role() if "role" in d else cast(Union[Unset, TeamMembershipCollaboratorRole], UNSET)

        def get_team() -> Union[Unset, TeamSummary]:
            team: Union[Unset, TeamSummary] = UNSET
            _team = d.pop("team")
            if not isinstance(_team, Unset):
                team = TeamSummary.from_dict(_team)

            return team

        team = get_team() if "team" in d else cast(Union[Unset, TeamSummary], UNSET)

        def get_type() -> Union[Unset, TeamMembershipCollaboratorType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = TeamMembershipCollaboratorType(_type)
                except ValueError:
                    type = TeamMembershipCollaboratorType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, TeamMembershipCollaboratorType], UNSET)

        team_membership_collaborator = cls(
            role=role,
            team=team,
            type=type,
        )

        team_membership_collaborator.additional_properties = d
        return team_membership_collaborator

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
    def role(self) -> TeamMembershipCollaboratorRole:
        if isinstance(self._role, Unset):
            raise NotPresentError(self, "role")
        return self._role

    @role.setter
    def role(self, value: TeamMembershipCollaboratorRole) -> None:
        self._role = value

    @role.deleter
    def role(self) -> None:
        self._role = UNSET

    @property
    def team(self) -> TeamSummary:
        if isinstance(self._team, Unset):
            raise NotPresentError(self, "team")
        return self._team

    @team.setter
    def team(self, value: TeamSummary) -> None:
        self._team = value

    @team.deleter
    def team(self) -> None:
        self._team = UNSET

    @property
    def type(self) -> TeamMembershipCollaboratorType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: TeamMembershipCollaboratorType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
