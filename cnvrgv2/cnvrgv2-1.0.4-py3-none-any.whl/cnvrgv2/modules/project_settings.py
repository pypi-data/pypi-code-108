from cnvrgv2.config import routes
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.modules.base.data_owner import DataOwner
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.utils.url_utils import urljoin
from cnvrgv2.utils.validators import attributes_validator


class ProjectSettings(DataOwner):

    available_attributes = {
        "title": str,
        "image": str,
        "privacy": str,
        "mount_folders": list,
        "env_variables": list,
        "check_stuckiness": bool,
        "max_restarts": int,
        "stuck_time": int,
        "autosync": bool,
        "sync_time": int,
        "default_computes": list,
        "use_org_deploy_key": bool,
        "deploy_key": str,
        "webhooks_url": str,
        "slack_webhooks": bool,
        "slack_webhook_channel": str,
        "command_to_execute": str,
        "run_tensorboard_by_default": bool,
        "run_jupyter_by_default": bool,
        "email_on_error": bool,
        "email_on_success": bool,
        "working_directory": str,
        "requirements_path": str,
        "secrets": list,
        "project_idle_time": float,
        "is_git": bool,
        "git_repo": str,
        "git_branch": str,
        "private_repo": bool,
        "description": str,
        "tags": list,
        "collaborators": list,
        "git_access_token": bool,
        "output_dir": str
    }

    def __init__(self, project):
        self._context = Context(context=project._context)
        scope = self._context.get_scope(SCOPE.PROJECT)

        self._proxy = Proxy(context=self._context)

        org_base = routes.PROJECT_BASE.format(scope["organization"], scope["project"])
        self._route = urljoin(org_base, "settings")

        self._attributes = {}

    def save(self):
        """
        Save the local settings in the current project
        @return: None
        """
        self.update(**self._attributes)

    def update(self, **kwargs):
        """
        Updates current project's settings with the given params
        @param kwargs: any param out of the available attributes can be sent
        @return: None
        """
        attributes_validator(
            available_attributes=ProjectSettings.available_attributes,
            attributes=kwargs,
        )

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="settings", attributes={**self._attributes, **kwargs})
        )

        response_attributes = response.attributes
        response_attributes.pop('slug', None)
        self._attributes = response_attributes
