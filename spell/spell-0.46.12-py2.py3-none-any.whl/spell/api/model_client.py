from spell.api import base_client
from spell.api.resources_client import ResourcesClient
from spell.api.models import ModelFileSpec
from spell.api.utils import url_path_join

MODEL_URL = "model"


class ModelClient(base_client.BaseClient):
    def new_model(self, owner, name, resource, version, files, description):
        payload = {
            "name": name,
            "version": version,
            "resource": resource,
            "files": [ModelFileSpec.from_string(f).to_payload() for f in files],
            "description": description,
        }
        r = self.request("post", url_path_join(MODEL_URL, owner), payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["model_version"]

    def update_model_description(self, owner, model_name, model_version, description):
        payload = {"description": description}
        r = self.request(
            "put",
            url_path_join(MODEL_URL, owner, model_name, "version", model_version),
            payload=payload,
        )

        self.check_and_raise(r)

    def list_models(self, owner):
        r = self.request("get", url_path_join(MODEL_URL, owner))
        self.check_and_raise(r)
        return self.get_json(r)["models"]

    def get_model(self, owner, model):
        r = self.request("get", url_path_join(MODEL_URL, owner, model))
        self.check_and_raise(r)
        return self.get_json(r)["model"]

    def get_model_version(self, owner, model, version):
        r = self.request("get", url_path_join(MODEL_URL, owner, model, "version", version))
        self.check_and_raise(r)
        return self.get_json(r)["model_version"]

    def rm_model(self, owner, model):
        r = self.request("delete", url_path_join(MODEL_URL, owner, model))
        self.check_and_raise(r)

    def rm_model_version(self, owner, model, version):
        r = self.request("delete", url_path_join(MODEL_URL, owner, model, "version", version))
        self.check_and_raise(r)

    def download_model_version(self, model_version_obj, dest, echo, quiet):
        resources_client = ResourcesClient(
            self.base_url,
            self.version_str,
            owner=self.owner,
            token=self.token,
            spell_admin_token=self.spell_admin_token,
        )

        resource = model_version_obj.resource
        if len(model_version_obj.files) == 0:
            todo = [resource]
        else:
            todo = [f"{resource}/{r.resource_path}" for r in model_version_obj.files]

        resources_client.download_resources(todo, dest, echo, quiet=quiet)
