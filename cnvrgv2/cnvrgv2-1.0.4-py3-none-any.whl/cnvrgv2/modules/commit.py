from cnvrgv2.config import routes
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF


class Commit(DynamicAttributes):

    available_attributes = {
        "sha1": str,
        "source": str,
        "message": str,
        "created_at": str
    }

    def __init__(self, context=None, slug=None, attributes=None):

        self._context = Context(context=context)

        # Set current context scope to current dataset
        if slug:
            self._context.set_scope(SCOPE.COMMIT, slug)

        self.scope = self._context.get_scope(SCOPE.COMMIT)

        self._proxy = Proxy(context=self._context)
        self._route = routes.COMMIT_BASE.format(self.scope["organization"], self.scope["dataset"], self.scope["commit"])
        self._attributes = attributes or {}

    def cache_commit(self, external_disk_title):
        """
        Caches the current commit onto an external disk, for quick access
        @param external_disk_title: title of the external disk to cache commit on
        @return: None
        """
        cache_commit_route = routes.WORKFLOW_STANDALONE_BASE.format(self.scope["organization"])

        attributes = {
            "commit_hash": self.sha1,
            "dataset_slug": self.scope["dataset"],
            "external_disk_title": external_disk_title,
            "task": "cache"
        }

        self._proxy.call_api(
            route=cache_commit_route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="DatasetWarmup", attributes=attributes)
        )
        # TODO: Should return something? Update docstring

    def clear_cached_commit(self, external_disk_title):
        """
        Removes the current cached commit from the external disk.
        @param external_disk_title: title of the external disk to remove cached commit from
        @return: None
        """
        clear_cached_commit_route = routes.WORKFLOW_STANDALONE_BASE.format(self.scope["organization"])

        attributes = {
            "commit_hash": self.sha1,
            "dataset_slug": self.scope["dataset"],
            "external_disk_title": external_disk_title,
            "task": "clear"
        }

        self._proxy.call_api(
            route=clear_cached_commit_route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="DatasetWarmup", attributes=attributes)
        )
        # TODO: Should return something? Update docstring
