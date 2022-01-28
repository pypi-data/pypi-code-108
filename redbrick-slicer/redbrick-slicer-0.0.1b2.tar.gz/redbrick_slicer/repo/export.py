"""Repo for accessing export apis."""
from typing import Dict

from redbrick_slicer.common.export import ExportControllerInterface
from redbrick_slicer.common.client import RBClient


class ExportRepo(ExportControllerInterface):
    """Handle API requests to get export data."""

    def __init__(self, client: RBClient) -> None:
        """Construct ExportRepo."""
        self.client = client

    def get_output_info(self, org_id: str, project_id: str) -> Dict:
        """Get info about the output labelset and taxonomy."""
        query_string = """
        query customGroup_rb_slicer($orgId: UUID!, $name: String!){
            customGroup(orgId: $orgId, name:$name){
                dataType
                taskType
                datapointCount
                taxonomy {
                    name
                    version
                    categories {
                        name
                        children {
                            name
                            classId
                            children {
                                name
                                classId
                                children {
                                    name
                                    classId
                                    children {
                                        name
                                        classId
                                        children {
                                            name
                                            classId
                                            children {
                                                name
                                                classId
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    colorMap {
                        name
                        color
                        classid
                        trail
                        taskcategory
                    }
                }
            }
        }
        """

        # EXECUTE THE QUERY
        query_variables = {
            "orgId": org_id,
            "name": project_id + "-output",
        }

        result = self.client.execute_query(query_string, query_variables)

        temp: Dict = result["customGroup"]
        return temp

    def get_datapoint_latest(self, org_id: str, project_id: str, task_id: str) -> Dict:
        """Get the latest labels for a single bdatapoint."""
        query_string = """
        query task_rb_slicer($orgId: UUID!, $projectId: UUID!, $taskId: UUID!) {
            task(
                orgId: $orgId
                projectId: $projectId
                taskId: $taskId
            ) {
                taskId
                currentStageName
                latestTaskData {
                    dataPoint {
                        name
                        itemsPresigned: items(presigned: true)
                        items(presigned: false)
                    }
                    createdByEmail
                    labelsData(interpolate: true)
                    labelsPath
                }
            }
        }
        """
        # EXECUTE THE QUERY
        query_variables = {
            "orgId": org_id,
            "projectId": project_id,
            "taskId": task_id,
        }

        result: Dict[str, Dict] = self.client.execute_query(
            query_string, query_variables, False
        )

        return result.get("task", {}) or {}
