from cnvrgv2.config import routes
from cnvrgv2.modules.project_settings import ProjectSettings
from cnvrgv2.modules.flows.flows_client import FlowsClient
from cnvrgv2.modules.volumes.volumes_client import VolumesClient
from cnvrgv2.modules.workflows import WorkspacesClient, WebappsClient, EndpointsClient, ExperimentsClient
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.modules.base.data_owner import DataOwner


class Project(DataOwner):

    available_attributes = {
        "title": str,
        "p_tags": list,
        "git": bool,
        "start_commit": str,
        "commit": str,
        "git_url": str,
        "git_branch": str,
        "num_files": int,
        "last_commit": str
    }

    def __init__(self, context=None, slug=None, attributes=None):
        # Init data attributes
        super().__init__()

        self._context = Context(context=context)

        # Set current context scope to current project
        if slug:
            self._context.set_scope(SCOPE.PROJECT, slug)

        scope = self._context.get_scope(SCOPE.PROJECT)

        self._proxy = Proxy(context=self._context)
        self._route = routes.PROJECT_BASE.format(scope["organization"], scope["project"])
        self._attributes = attributes or {}
        self.slug = scope["project"]

        self._init_clients()

    def save(self):
        pass

    def delete(self):
        """
        Deletes the current project
        @return: None
        """
        self._proxy.call_api(route=self._route, http_method=HTTP.DELETE)

    def _init_clients(self):
        self.workspaces = WorkspacesClient(self)
        self.endpoints = EndpointsClient(self)
        self.webapps = WebappsClient(self)
        self.experiments = ExperimentsClient(self)
        self.volumes = VolumesClient(self)
        self.settings = ProjectSettings(self)
        self.flows = FlowsClient(self._context)

    def _validate_config_ownership(self):
        return self.slug == self._config.project_slug

    def save_config(self, local_config_path=None):
        """
        Saves the project configuration in the local folder
        @return: None
        """

        self._config.update(local_config_path=local_config_path, **{
            "project_slug": self.slug,
            "organization": self._context.organization,
            "git": getattr(self, "git", False),
            "commit_sha1": self.local_commit
        })
