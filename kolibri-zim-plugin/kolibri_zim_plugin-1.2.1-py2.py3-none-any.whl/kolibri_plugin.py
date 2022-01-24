from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from kolibri.core.content import hooks as content_hooks
from kolibri.plugins import KolibriPluginBase
from kolibri.plugins.hooks import register_hook
from le_utils.constants import format_presets


class ZimPlugin(KolibriPluginBase):
    root_view_urls = "root_urls"


@register_hook
class ZimAsset(content_hooks.ContentRendererHook):
    bundle_id = "main"
    presets = (format_presets.ZIM,)
