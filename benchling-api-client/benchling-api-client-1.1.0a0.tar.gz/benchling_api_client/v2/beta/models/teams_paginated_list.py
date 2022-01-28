from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.team import Team
from ..types import UNSET, Unset

T = TypeVar("T", bound="TeamsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class TeamsPaginatedList:
    """  """

    _teams: Union[Unset, List[Team]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("teams={}".format(repr(self._teams)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TeamsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        teams: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._teams, Unset):
            teams = []
            for teams_item_data in self._teams:
                teams_item = teams_item_data.to_dict()

                teams.append(teams_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if teams is not UNSET:
            field_dict["teams"] = teams
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_teams() -> Union[Unset, List[Team]]:
            teams = []
            _teams = d.pop("teams")
            for teams_item_data in _teams or []:
                teams_item = Team.from_dict(teams_item_data)

                teams.append(teams_item)

            return teams

        teams = get_teams() if "teams" in d else cast(Union[Unset, List[Team]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        teams_paginated_list = cls(
            teams=teams,
            next_token=next_token,
        )

        teams_paginated_list.additional_properties = d
        return teams_paginated_list

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
    def teams(self) -> List[Team]:
        if isinstance(self._teams, Unset):
            raise NotPresentError(self, "teams")
        return self._teams

    @teams.setter
    def teams(self, value: List[Team]) -> None:
        self._teams = value

    @teams.deleter
    def teams(self) -> None:
        self._teams = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
