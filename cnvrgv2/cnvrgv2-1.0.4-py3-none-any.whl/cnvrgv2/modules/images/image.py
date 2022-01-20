from cnvrgv2.proxy import Proxy
from cnvrgv2.config import routes
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class Image(DynamicAttributes):

    available_attributes = {
        "slug": str,
        "name": str,
        "tag": str,
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current project
        if slug:
            self._context.set_scope(SCOPE.IMAGE, slug)

        scope = self._context.get_scope(SCOPE.IMAGE)

        self._proxy = Proxy(context=self._context)
        self._route = routes.IMAGE_BASE.format(scope["organization"], scope["image"])
        self._attributes = attributes or {}
        self.slug = scope["image"]
