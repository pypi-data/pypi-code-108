from ast import Tuple
from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from eyja.hubs.plugin_hub import PluginHub
from eyja.interfaces.plugins import BasePlugin
from eyja.constants.types import (
    PluginTypes,
    ConfigTypes,
)
from eyja.errors import ParseModelNamespaceError


class DataHub(BaseHub):
    _storages = {}

    @classmethod
    async def init(cls):
        cls._storage_configs = ConfigHub.get('storages')
        cls._storage_plugins = PluginHub.plugins_by_type(PluginTypes.STORAGE_CLIENT)

        await cls.init_storage()
        await super().init()

    @classmethod
    async def init_storage(cls):
        if not ConfigHub.get(ConfigTypes.STORAGE_CONFIGS):
            return

        for storage_name, storage_config in ConfigHub.get(ConfigTypes.STORAGE_CONFIGS).items():
            configs = {}

            if isinstance(storage_config, list):
                for config in storage_config:
                    configs[config['name']] = config
            elif isinstance(storage_config, dict):
                configs['default'] = storage_config

            plugin: BasePlugin = cls._storage_plugins[storage_name]['cls']
            for config_name, config_value in configs.items():
                if storage_name not in cls._storages:
                    cls._storages[storage_name] = {}
                cls._storages[storage_name][config_name] = await plugin.run(**config_value)

    @classmethod
    async def reset(cls):
        cls._storages = {}
        await super().reset()

    @classmethod
    def get_client(cls, obj) -> Tuple:
        storage_type, storage_connection, object_space, object_type = obj.namespace()

        if len(storage_type) < 1:
            storage_type = list(cls._storages.keys())[0]

        if len(storage_connection) < 1:
            storage_connection = 'default'

        if storage_type not in cls._storages:
            raise ParseModelNamespaceError(
                'Unknown storage type'
            )

        if storage_connection not in cls._storages[storage_type]:
            raise ParseModelNamespaceError(
                f'Unknown storage connection - [{storage_connection}]'
            )

        client = cls._storages[storage_type][storage_connection]

        if len(object_space) < 1:
            object_space = str(client._buckets[0])

        return (client, object_space, object_type)

    @classmethod
    async def save(cls, obj):
        client, object_space, object_type = cls.get_client(obj)
        await client.save(obj, object_space, object_type)

    @classmethod
    async def delete(cls, obj):
        client, object_space, object_type = cls.get_client(obj)
        await client.delete(obj, object_space, object_type)

    @classmethod
    async def delete_all(cls, obj, filter):
        client, object_space, object_type = cls.get_client(obj)
        await client.delete_all(obj, object_space, object_type, filter)

    @classmethod
    async def get(cls, obj_cls, object_id):
        client, object_space, object_type = cls.get_client(obj_cls)
        return await client.get(obj_cls, object_space, object_type, object_id)

    @classmethod
    async def find(cls, obj_cls, filter):
        client, object_space, object_type = cls.get_client(obj_cls)
        return await client.find(obj_cls, object_space, object_type, filter)

    @classmethod
    async def count(cls, obj_cls, filter):
        client, object_space, object_type = cls.get_client(obj_cls)
        return await client.count(obj_cls, object_space, object_type, filter)
