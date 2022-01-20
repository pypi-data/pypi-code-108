from yangsuite import get_logger
from ysyangtree import ParseYang

log = get_logger(__name__)


class YSGnmiYangtree(ParseYang):
    """ParseYang with tree contents modified for gNMI use cases."""

    def __init__(self, *args, **kwargs):
        self._model_prefixes = {}

        super(YSGnmiYangtree, self).__init__(*args, **kwargs)

    @property
    def model_prefixes(self):
        """Dictionary mapping prefix to model name."""
        if not self._model_prefixes:
            for module_stmt in self.ctx.modules.values():
                self._model_prefixes[module_stmt.i_prefix] = \
                    module_stmt.i_modulename

        return self._model_prefixes

    def get_module_node_data(self, node_callback=None):
        """Override base class to get model prefixes."""
        node = super(YSGnmiYangtree, self).get_module_node_data()

        node['data']['namespace_modules'] = self.model_prefixes

        return node
