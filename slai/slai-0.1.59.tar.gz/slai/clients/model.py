from slai.clients.cli import get_cli_client
from slai.modules.parameters import from_config
from importlib import import_module


def get_model_client(*, org_name, model_name):
    import_path = from_config(
        "MODEL_CLIENT",
        "slai.clients.model.ModelClient",
    )
    class_ = import_path.split(".")[-1]
    path = ".".join(import_path.split(".")[:-1])
    return getattr(import_module(path), class_)(
        org_name=org_name,
        model_name=model_name,
    )


class ModelClient:
    def __init__(
        self,
        *,
        org_name=None,
        model_name=None,
    ):
        self.cli_client = get_cli_client()
        self.org_name = org_name
        self.model_name = model_name
        self.model = self.get_model()

    def get_model(self):
        model_data = self.cli_client.retrieve_model(
            name=self.model_name, org_name=self.org_name
        )
        return model_data

    def get_model_version_by_name(self, *, model_version_name):
        model_version_data = self.cli_client.retrieve_model_version_by_name(
            model_id=self.model["id"],
            model_version_name=model_version_name,
        )
        return model_version_data

    def get_model_version_by_id(self, *, model_version_id):
        model_version_data = self.cli_client.retrieve_model_version_by_id(
            model_version_id=model_version_id,
        )
        return model_version_data

    def get_latest_model_artifact(self, model_version_id=None):
        model_data = self.get_model()

        if model_version_id is None:
            model_version_id = model_data["model_version_id"]

        model_artifact = self.cli_client.retrieve_model_artifact(
            model_version_id=model_version_id,
            model_artifact_id=None,
        )
        return model_artifact

    def list_model_artifacts(self, model_version_id):
        model_artifacts = self.cli_client.retrieve_model_artifact(
            model_version_id=model_version_id,
        )
        return model_artifacts
