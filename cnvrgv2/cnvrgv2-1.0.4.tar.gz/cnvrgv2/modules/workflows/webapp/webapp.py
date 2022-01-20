from datetime import datetime

from cnvrgv2.config import routes
from cnvrgv2.modules.base.workflow_instance_base import WorkflowInstanceBase
from cnvrgv2.proxy import Proxy
from cnvrgv2.context import Context, SCOPE


class WebappType:
    SHINY = "rshiny"
    DASH = "dash"
    VOILA = "voila"


class Webapp(WorkflowInstanceBase):
    available_attributes = {
        "webapp_type": str,
        "template_ids": list,
        "template_id": int,
        "compute": str,
        "num_of_exps": int,
        "updated_at": datetime,
        "iframe_url": str,
        "is_public": bool,
        "last_opened": datetime,
        "current_step": int,
        "strip_sources": bool,
        "copy_frequency": int,
        "file_name": str,
        "experiments": list,
        **WorkflowInstanceBase.available_attributes
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current project
        if slug:
            self._context.set_scope(SCOPE.WEBAPP, slug)

        scope = self._context.get_scope(SCOPE.WEBAPP)

        self._proxy = Proxy(context=self._context)
        self._route = routes.WEBAPP_BASE.format(scope["organization"], scope["project"], scope["webapp"])
        self._attributes = attributes or {}
        self._type = "Webapp"
        self.slug = scope["webapp"]

    def start(self):
        """
        Override start from workflows_base to remove functionality.
        start() is only relevant for Endpoints & Workspaces
        """
        raise AttributeError("'Webapp' object has no attribute 'start'")

    def sync_remote(self, commit_msg=None):
        raise NotImplementedError()
