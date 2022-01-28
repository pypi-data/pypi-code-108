from typing import Iterable, List, Optional

from benchling_api_client.api.projects import archive_projects, get_project, list_projects, unarchive_projects
from benchling_api_client.types import Response

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset, optional_array_query_param
from benchling_sdk.models import (
    ListProjectsSort,
    Project,
    ProjectsArchivalChange,
    ProjectsArchive,
    ProjectsArchiveReason,
    ProjectsPaginatedList,
    ProjectsUnarchive,
)
from benchling_sdk.services.base_service import BaseService


class ProjectService(BaseService):
    """
    Projects.

    Manage project objects.

    See https://benchling.com/api/reference#/Projects
    """

    @api_method
    def get_by_id(self, project_id: str) -> Project:
        """
        Get a Project by ID.

        See https://benchling.com/api/reference#/Projects/getProject
        """
        response = get_project.sync_detailed(client=self.client, project_id=project_id)
        return model_from_detailed(response)

    @api_method
    def _projects_page(
        self,
        *,
        sort: Optional[ListProjectsSort] = ListProjectsSort.NAME,
        archive_reason: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        next_token: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> Response[ProjectsPaginatedList]:
        return list_projects.sync_detailed(
            client=self.client,
            sort=none_as_unset(sort),
            archive_reason=none_as_unset(archive_reason),
            ids=none_as_unset(optional_array_query_param(ids)),
            name=none_as_unset(name),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )

    def list(
        self,
        *,
        sort: Optional[ListProjectsSort] = None,
        archive_reason: Optional[str] = None,
        ids: Optional[Iterable[str]] = None,
        name: Optional[str] = None,
        page_size: Optional[int] = 50,
    ) -> PageIterator[Project]:
        """
        List Projects.

        See https://benchling.com/api/reference#/Projects/listProjects
        """

        def api_call(next_token: NextToken) -> Response[ProjectsPaginatedList]:
            return self._projects_page(
                sort=sort,
                archive_reason=archive_reason,
                ids=ids,
                name=name,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: ProjectsPaginatedList) -> Optional[List[Project]]:
            return body.projects

        return PageIterator(api_call, results_extractor)

    @api_method
    def archive(self, project_ids: Iterable[str], reason: ProjectsArchiveReason) -> ProjectsArchivalChange:
        """
        Archive Projects.

        See https://benchling.com/api/reference#/Projects/archiveProjects
        """
        archive_request = ProjectsArchive(project_ids=list(project_ids), reason=reason)
        response = archive_projects.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, project_ids: Iterable[str]) -> ProjectsArchivalChange:
        """
        Unarchive Projects.

        See https://benchling.com/api/reference#/Projects/unarchiveProjects
        """
        unarchive_request = ProjectsUnarchive(project_ids=list(project_ids))
        response = unarchive_projects.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)
