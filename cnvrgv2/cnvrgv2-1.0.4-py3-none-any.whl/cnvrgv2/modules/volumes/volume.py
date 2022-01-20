
from cnvrgv2.config import routes
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.proxy import Proxy
from cnvrgv2.context import Context, SCOPE


class Volume(DynamicAttributes):

    available_attributes = {
        "slug": str,
        "title": str,
        "total_space": int,
        "used_space": int,
        "host_path": str,
        "host_ip": str,
        "read_only": bool,
        "hide": bool,
        "volume_type": str,
        "mount_path": str,
        "claim_name": str,
        "status": str,
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current volume
        if slug:
            self._context.set_scope(SCOPE.VOLUME, slug)

        scope = self._context.get_scope(SCOPE.VOLUME)

        self._proxy = Proxy(context=self._context)
        self._route = routes.VOLUME_BASE.format(scope["organization"], scope["project"], scope["volume"])
        self._attributes = attributes or {}
        self.slug = scope["volume"]
