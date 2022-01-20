from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestWriteTeamAssignee")


@attr.s(auto_attribs=True, repr=False)
class RequestWriteTeamAssignee:
    """  """

    _team_id: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("team_id={}".format(repr(self._team_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestWriteTeamAssignee({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        team_id = self._team_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "teamId": team_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_team_id() -> str:
            team_id = d.pop("teamId")
            return team_id

        team_id = get_team_id() if "teamId" in d else cast(str, UNSET)

        request_write_team_assignee = cls(
            team_id=team_id,
        )

        request_write_team_assignee.additional_properties = d
        return request_write_team_assignee

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
    def team_id(self) -> str:
        if isinstance(self._team_id, Unset):
            raise NotPresentError(self, "team_id")
        return self._team_id

    @team_id.setter
    def team_id(self, value: str) -> None:
        self._team_id = value
