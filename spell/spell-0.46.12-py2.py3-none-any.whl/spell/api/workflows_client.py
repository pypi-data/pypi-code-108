from spell.api import base_client
from spell.api.utils import url_path_join

WORKFLOW_RESOURCE_URL = "workflows"
KILL_RESOURCE_URL = "kill"
STOP_RESOURCE_URL = "stop"


class WorkflowsClient(base_client.BaseClient):
    def workflow(self, run_req, workspace_specs, github_specs):
        payload = {
            "run": run_req if run_req else None,
            "workspace_specs": workspace_specs,
            "github_specs": github_specs,
        }
        r = self.request("post", url_path_join(WORKFLOW_RESOURCE_URL, self.owner), payload=payload)
        self.check_and_raise(r)
        resp = self.get_json(r)
        return resp["workflow"]

    def get_workflow(self, workflow_id):
        """Get a workflow

        Keyword arguments:
        workflow_id -- the id of the workflow

        Returns:
        a Workflow object
        """
        r = self.request("get", url_path_join(WORKFLOW_RESOURCE_URL, self.owner, workflow_id))
        self.check_and_raise(r)
        return self.get_json(r)["workflow"]

    def kill_workflow(self, workflow_id):
        """Kill a specific workflow run.

        Keyword arguments:
        workflow_id -- the id of the workflow

        """
        r = self.request("post", url_path_join(WORKFLOW_RESOURCE_URL, self.owner, workflow_id, KILL_RESOURCE_URL))
        self.check_and_raise(r)

    def stop_workflow(self, workflow_id):
        """Stop a specific workflow run.

        Keyword arguments:
        workflow_id -- the id of the workflow

        """
        r = self.request("post", url_path_join(WORKFLOW_RESOURCE_URL, self.owner, workflow_id, STOP_RESOURCE_URL))
        self.check_and_raise(r)

    def archive_workflow(self, workflow_id):
        """Archive a specific workflow run.

        Keyword arguments:
        workflow_id -- the id of the workflow

        """
        r = self.request("delete", url_path_join(WORKFLOW_RESOURCE_URL, self.owner, workflow_id))
        self.check_and_raise(r)
