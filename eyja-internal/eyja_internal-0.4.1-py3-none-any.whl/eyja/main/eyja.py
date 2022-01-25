from typing import List, Union

from eyja.hubs.config_hub import ConfigHub
from eyja.hubs.plugin_hub import PluginHub
from eyja.hubs.data_hub import DataHub


class Eyja:
    @classmethod
    async def init(
        cls,
        config_file: str = None,
        config: Union[str, dict] = None,
        plugins: List[str] = []
    ):
        await ConfigHub.init(
            config_file=config_file,
            config=config,
        )
        await PluginHub.init(
            plugins=plugins
        )
        await DataHub.init()

    @classmethod
    async def reset(cls):
        await ConfigHub.reset()
        await PluginHub.reset()
        await DataHub.reset()

    @classmethod
    def is_initialized(cls):
        return all([
            ConfigHub.is_initialized(),
            PluginHub.is_initialized(),
            DataHub.is_initialized(),
        ])
