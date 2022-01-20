from cnvrgv2.config import routes
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class Query(DynamicAttributes):
    available_attributes = {
        "slug": str,
        "name": str,
        "query": str,
        "commit_sha1": str,
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current query
        if slug:
            self._context.set_scope(SCOPE.QUERY, slug)

        scope = self._context.get_scope(SCOPE.QUERY)

        self._proxy = Proxy(context=self._context)
        self._route = routes.QUERY_BASE.format(scope["organization"], scope["dataset"], scope["query"])
        self._attributes = attributes or {}
        self.slug = scope["query"]

    def delete(self):
        """
        Deletes the current query
        @return: None
        """
        self._proxy.call_api(route=self._route, http_method=HTTP.DELETE)
