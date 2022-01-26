from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.project import Project
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class ProjectsPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _projects: Union[Unset, List[Project]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("projects={}".format(repr(self._projects)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ProjectsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        projects: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._projects, Unset):
            projects = []
            for projects_item_data in self._projects:
                projects_item = projects_item_data.to_dict()

                projects.append(projects_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if projects is not UNSET:
            field_dict["projects"] = projects

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_projects() -> Union[Unset, List[Project]]:
            projects = []
            _projects = d.pop("projects")
            for projects_item_data in _projects or []:
                projects_item = Project.from_dict(projects_item_data)

                projects.append(projects_item)

            return projects

        projects = get_projects() if "projects" in d else cast(Union[Unset, List[Project]], UNSET)

        projects_paginated_list = cls(
            next_token=next_token,
            projects=projects,
        )

        projects_paginated_list.additional_properties = d
        return projects_paginated_list

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

    @property
    def projects(self) -> List[Project]:
        if isinstance(self._projects, Unset):
            raise NotPresentError(self, "projects")
        return self._projects

    @projects.setter
    def projects(self, value: List[Project]) -> None:
        self._projects = value

    @projects.deleter
    def projects(self) -> None:
        self._projects = UNSET
