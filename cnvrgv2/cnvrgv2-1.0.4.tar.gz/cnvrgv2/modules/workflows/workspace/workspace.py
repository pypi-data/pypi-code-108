from cnvrgv2.config import routes
from cnvrgv2.modules.base.workflow_instance_base import WorkflowInstanceBase
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin


class NotebookType:
    JUPYTER_LAB = "jupyterlab"
    VS_CODE = "vscode"
    R_STUDIO = "r_studio"


class Workspace(WorkflowInstanceBase):

    available_attributes = {
        "jupyter_token": str,
        "iframe_url": str,
        "is_spark": bool,
        "spark_url": str,
        "spark_master_url": str,
        "notebook_type": str,
        "tensorboard_url": str,
        "commits": list,
        "webapps": dict,
        "endpoints": list,
        "experiments": list,
        "current_step": str,
        "workspace_steps": str,
        "on_stop_build": dict,
        **WorkflowInstanceBase.available_attributes
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current project
        if slug:
            self._context.set_scope(SCOPE.WORKSPACE, slug)

        scope = self._context.get_scope(SCOPE.WORKSPACE)

        self._proxy = Proxy(context=self._context)
        self._route = routes.WORKSPACE_BASE.format(scope["organization"], scope["project"], scope["workspace"])
        self._attributes = attributes or {}
        self._type = "NotebookSession"
        self.slug = scope["workspace"]

    def build_image(self, registry, repository, tag="latest", is_custom=False, link_to_workspace=True):
        """
        Build an image from the current workspace
        @param registry: Name of the registry
        @param repository: Name of the repository in the registry
        @param tag: A tag for the image
        @param is_custom:
        @param link_to_workspace: If true, workspace will start from the linked image
        @return: None
        """

        build_image_url = urljoin(self._route, routes.WORKSPACE_BUILD_IMAGE_SUFFIX)

        attributes = {
            "registry_slug": registry,
            "repo": repository,
            "tag": tag,
            "is_custom": is_custom,
            "link_to_workspace": link_to_workspace
        }

        self._proxy.call_api(
            route=build_image_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def activate_build_image_on_stop(self, registry, repository, tag="latest", link_to_workspace=True):
        """
        Build image when workspace is stopped
        @param registry: Name of the registry
        @param repository: Name of the repository in the registry
        @param tag: A tag for the image
        @param link_to_workspace: If true, workspace will start from the linked image
        @return: None
        """
        activate_build_image_url = urljoin(self._route, routes.WORKSPACE_ACTIVATE_BUILD_IMAGE_ON_STOP_SUFFIX)

        attributes = {
            "registry_slug": registry,
            "repo": repository,
            "tag": tag,
            "activate": True,
            "is_custom": True,
            "link_to_workspace": link_to_workspace,
        }

        response_attributes = self._proxy.call_api(
            route=activate_build_image_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        ).attributes

        self._attributes = {**self._attributes, **response_attributes}

    def disable_build_image_on_stop(self):
        """
        Stop automatically build when workspace is stopped
        @return: None
        """
        disable_build_image_url = urljoin(self._route, routes.WORKSPACE_DISABLE_BUILD_IMAGE_ON_STOP_SUFFIX)

        response_attributes = self._proxy.call_api(
            route=disable_build_image_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        ).attributes

        self._attributes = {**self._attributes, **response_attributes}

    def start_tensorboard(self):
        """
        Starts a tensorboard server in the current workspace
        """
        url = urljoin(self._route, routes.WORKflOW_START_TENSORBOARD_SUFFIX)

        self._proxy.call_api(
            route=url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        )

    def stop_tensorboard(self):
        """
        Stop the tensorboard session in the current workspace
        """
        url = urljoin(self._route, routes.WORKflOW_STOP_TENSORBOARD_SUFFIX)

        self._proxy.call_api(
            route=url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes={})
        )
