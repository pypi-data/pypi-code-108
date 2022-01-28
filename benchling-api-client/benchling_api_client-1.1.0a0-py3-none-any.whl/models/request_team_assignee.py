from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.team_summary import TeamSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestTeamAssignee")


@attr.s(auto_attribs=True, repr=False)
class RequestTeamAssignee:
    """  """

    _team: Union[Unset, TeamSummary] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("team={}".format(repr(self._team)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestTeamAssignee({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        team: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._team, Unset):
            team = self._team.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if team is not UNSET:
            field_dict["team"] = team

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_team() -> Union[Unset, TeamSummary]:
            team: Union[Unset, TeamSummary] = UNSET
            _team = d.pop("team")
            if not isinstance(_team, Unset):
                team = TeamSummary.from_dict(_team)

            return team

        team = get_team() if "team" in d else cast(Union[Unset, TeamSummary], UNSET)

        request_team_assignee = cls(
            team=team,
        )

        request_team_assignee.additional_properties = d
        return request_team_assignee

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
