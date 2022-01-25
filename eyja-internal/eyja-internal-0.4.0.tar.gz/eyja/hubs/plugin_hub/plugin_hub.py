import importlib
import inspect

from typing import List

from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from eyja.interfaces.plugins import BasePlugin


class PluginHub(BaseHub):
    _plugins_ids = None
    _plugins = {}

    @classmethod
    async def init(cls, plugins: List[str]):
        cls._plugins_ids = ConfigHub.get('plugins', []) + plugins

        for plugin_id in cls._plugins_ids:
            module = importlib.import_module(plugin_id)
            for _, module_item in inspect.getmembers(module):
                if inspect.isclass(module_item):
                    if issubclass(module_item, BasePlugin) and module_item != BasePlugin:
                        cls._plugins[module_item.name] = {
                            'type': module_item.plugin_type,
                            'cls': module_item,
                        }

        await super().init()

    @classmethod
    def plugins(cls):
        return cls._plugins

    @classmethod
    def plugins_by_type(cls, plugin_type):
        return {k:v for k, v in cls._plugins.items() if v['type'] == plugin_type}

    @classmethod
    async def reset(cls):
        cls._plugins_ids = []

        await super().reset()
