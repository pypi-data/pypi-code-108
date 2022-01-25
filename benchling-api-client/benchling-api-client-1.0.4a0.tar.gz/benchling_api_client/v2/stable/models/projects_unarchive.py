from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectsUnarchive")


@attr.s(auto_attribs=True, repr=False)
class ProjectsUnarchive:
    """  """

    _project_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("project_ids={}".format(repr(self._project_ids)))
        return "ProjectsUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        project_ids = self._project_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "projectIds": project_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_project_ids() -> List[str]:
            project_ids = cast(List[str], d.pop("projectIds"))

            return project_ids

        project_ids = get_project_ids() if "projectIds" in d else cast(List[str], UNSET)

        projects_unarchive = cls(
            project_ids=project_ids,
        )

        return projects_unarchive

    @property
    def project_ids(self) -> List[str]:
        """ A list of project IDs to unarchive. """
        if isinstance(self._project_ids, Unset):
            raise NotPresentError(self, "project_ids")
        return self._project_ids

    @project_ids.setter
    def project_ids(self, value: List[str]) -> None:
        self._project_ids = value
