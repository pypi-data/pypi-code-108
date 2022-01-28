"""Handlers to access APIs for getting projects."""
from typing import Dict

from redbrick_slicer.common.client import RBClient
from redbrick_slicer.common.project import ProjectRepoInterface


class ProjectRepo(ProjectRepoInterface):
    """Class to manage interaction with project APIs."""

    def __init__(self, client: RBClient) -> None:
        """Construct ProjectRepo."""
        self.client = client

    def get_project(self, org_id: str, project_id: str) -> Dict:
        """
        Get project name and status.

        Raise an exception if project does not exist.
        """
        query = """
            query project_rb_slicer($orgId: UUID!, $projectId: UUID!){
                project(orgId: $orgId, projectId: $projectId){
                    orgId
                    projectId
                    name
                    status
                    tdType
                    taxonomy {
                        name
                    }
                    projectUrl
                }
            }
        """
        variables = {"orgId": org_id, "projectId": project_id}
        response: Dict[str, Dict] = self.client.execute_query(query, variables)
        if response.get("project"):
            return response["project"]

        raise Exception("Project does not exist")
