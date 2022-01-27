import cognite.airworkflow.constants as const
from cognite.airworkflow.model.deployment import Deployment
from cognite.airworkflow.util import cdf, env, functions


class FunctionDeployer:
    def __init__(self, deployment: Deployment, is_delete: bool = False, pr: bool = False):
        project_info = const.AUTHENTICATION[deployment.project]
        self.client = cdf.experimental_client(project_info.project)
        self.display_name = deployment.code_path.name
        self.function_name = functions.get_function_name(self.display_name, version=deployment.version, pr=pr)
        self.function_name_latest = functions.get_function_name(self.display_name, pr=pr, latest=True)
        self.file_name = self.function_name.replace("/", "_").replace(":", "_").replace(".", "_")

        self.is_delete = is_delete
        self.is_pr = pr
        self.deployment = deployment
        self.oidc = project_info.oidc
        self.secrets = (
            {}
            if (self.is_delete or self.deployment.secret_names is None)
            else {s: env.get_env_value(s) for s in self.deployment.secret_names}
        )

    def handle_deployment(self):
        if self.is_pr:
            self.handle_pull_request()
        else:
            self.handle_push()

    def handle_pull_request(self):
        functions.delete_function(self.client, self.function_name)
        if self.is_delete:
            return

        file_id = cdf.zip_and_upload(
            self.client,
            self.deployment.code_path / const.FUNCTION_REL_PATH,
            self.file_name,
            "AIR",
        )
        functions.deploy_function(
            self.client,
            self.function_name,
            file_id,
            self.secrets,
            owner="AIR",
            oidc=self.oidc,
        )

    def handle_push(self) -> None:
        file_id = cdf.zip_and_upload(
            self.client,
            self.deployment.code_path / const.FUNCTION_REL_PATH,
            self.file_name,
            "AIR",
        )
        functions.deploy_function(
            self.client,
            self.function_name_latest,
            file_id,
            self.secrets,
            owner="AIR",
            oidc=self.oidc,
        )
        functions.delete_function(self.client, self.function_name)
