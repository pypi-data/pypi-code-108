from spell.api.runs_client import RunsClient
from spell.api.feedback_client import FeedbackClient
from spell.api.keys_client import KeysClient
from spell.api.resources_client import ResourcesClient
from spell.api.model_server_client import ModelServerClient
from spell.api.model_client import ModelClient
from spell.api.projects_client import ProjectsClient
from spell.api.supported_options_client import SupportedOptionsClient
from spell.api.user_client import UserClient
from spell.api.user_datasets_client import UserDatasetsClient
from spell.api.workspaces_client import WorkspacesClient
from spell.api.workflows_client import WorkflowsClient
from spell.api.links_client import LinksClient
from spell.api.cluster_client import ClusterClient
from spell.api.features_client import FeaturesClient
from spell.api.jupyter_workspaces_client import JupyterWorkspacesClient
from spell.api.config_client import ConfigClient
from spell.api.hyper_client import HyperClient


class APIClient(
    ClusterClient,
    FeaturesClient,
    FeedbackClient,
    KeysClient,
    LinksClient,
    ModelClient,
    ModelServerClient,
    ProjectsClient,
    ResourcesClient,
    RunsClient,
    SupportedOptionsClient,
    ConfigClient,
    UserClient,
    UserDatasetsClient,
    WorkflowsClient,
    WorkspacesClient,
    JupyterWorkspacesClient,
    HyperClient,
):
    def __init__(self, **kwargs):
        super(APIClient, self).__init__(**kwargs)
