from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.projects_archive_reason import ProjectsArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectsArchive")


@attr.s(auto_attribs=True, repr=False)
class ProjectsArchive:
    """  """

    _project_ids: List[str]
    _reason: ProjectsArchiveReason

    def __repr__(self):
        fields = []
        fields.append("project_ids={}".format(repr(self._project_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "ProjectsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        project_ids = self._project_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "projectIds": project_ids,
                "reason": reason,
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

        def get_reason() -> ProjectsArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = ProjectsArchiveReason(_reason)
            except ValueError:
                reason = ProjectsArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(ProjectsArchiveReason, UNSET)

        projects_archive = cls(
            project_ids=project_ids,
            reason=reason,
        )

        return projects_archive

    @property
    def project_ids(self) -> List[str]:
        """ A list of project IDs to archive. """
        if isinstance(self._project_ids, Unset):
            raise NotPresentError(self, "project_ids")
        return self._project_ids

    @project_ids.setter
    def project_ids(self, value: List[str]) -> None:
        self._project_ids = value

    @property
    def reason(self) -> ProjectsArchiveReason:
        """The reason for archiving the provided projects. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: ProjectsArchiveReason) -> None:
        self._reason = value
