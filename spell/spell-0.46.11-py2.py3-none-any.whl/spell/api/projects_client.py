from spell.api import base_client
from spell.api.utils import url_path_join


PROJECT_RESOURCE_URL = "projects"


class ProjectsClient(base_client.BaseClient):
    def create_project(self, proj_req):
        r = self.request("post", url_path_join(PROJECT_RESOURCE_URL, self.owner), payload=proj_req)
        self.check_and_raise(r)
        resp = self.get_json(r)
        return resp["spell_project"]

    def list_projects(self, show_archived=False):
        url = url_path_join(PROJECT_RESOURCE_URL, self.owner)
        r = self.request("get", url, params={"archived": show_archived})
        self.check_and_raise(r)
        resp = self.get_json(r)
        return resp["spell_projects"]

    def get_project(self, id):
        r = self.request("get", url_path_join(PROJECT_RESOURCE_URL, self.owner, id))
        self.check_and_raise(r)
        resp = self.get_json(r)
        return resp["spell_project"]

    def archive_project(self, id):
        r = self.request("delete", url_path_join(PROJECT_RESOURCE_URL, self.owner, id))
        self.check_and_raise(r)

    def unarchive_project(self, id):
        payload = {"project_id": id}
        url = url_path_join(PROJECT_RESOURCE_URL, self.owner, "unarchive")
        r = self.request("post", url, payload=payload)
        self.check_and_raise(r)

    def edit_project(self, id, name, description):
        payload = {"name": name, "description": description}
        r = self.request("patch", url_path_join(PROJECT_RESOURCE_URL, self.owner, id), payload=payload)
        self.check_and_raise(r)

    def add_runs(self, project_id, run_ids):
        payload = {"run_ids": run_ids}
        r = self.request(
            "post",
            url_path_join(PROJECT_RESOURCE_URL, self.owner, project_id, "runs"),
            payload=payload,
        )
        self.check_and_raise(r)

    def remove_runs(self, project_id, run_ids):
        payload = {"run_ids": run_ids}
        r = self.request(
            "delete",
            url_path_join(PROJECT_RESOURCE_URL, self.owner, project_id, "runs"),
            payload=payload,
        )
        self.check_and_raise(r)
