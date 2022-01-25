import aiofiles
import yaml

from typing import Any, Union

from eyja.hubs.base_hub import BaseHub


class ConfigHub(BaseHub):
    _config: dict = {}

    @classmethod
    async def init(cls, config_file: str = None, config: Union[str, dict] = None) -> bool:
        init_result = False
        if config_file:
            init_result = await cls.load_from_file(config_file)
        elif config:
            if isinstance(config, str):
                init_result = cls.load_from_str(config)
            elif isinstance(config, dict):
                init_result = cls.load_from_dict(config)

        if init_result:
            await super().init()

        return init_result

    @classmethod
    def sync_init(cls, config_file: str = None, config: Union[str, dict] = None) -> bool:
        init_result = False
        if config_file:
            init_result = cls.sync_load_from_file(config_file)
        elif config:
            if isinstance(config, str):
                init_result = cls.load_from_str(config)
            elif isinstance(config, dict):
                init_result = cls.load_from_dict(config)

        if init_result:
            super().sync_init()

        return init_result

    @classmethod
    async def reset(cls):
        cls._config = {}

        await super().reset()

    @classmethod
    async def load_from_file(cls, config_file: str = None) -> bool:
        async with aiofiles.open(config_file, 'r') as fp:
            config_data = await fp.read()

        return cls.load_from_str(config_data)

    @classmethod
    def sync_load_from_file(cls, config_file: str = None) -> bool:
        with open(config_file, 'r') as fp:
            config_data = fp.read()

        return cls.load_from_str(config_data)

    @classmethod
    def load_from_str(cls, data: str) -> bool:
        config_data = yaml.load(data, Loader=yaml.FullLoader)
        return cls.load_from_dict(config_data)        

    @classmethod
    def load_from_dict(cls, data: dict) -> bool:
        cls._config = data

        return True

    @classmethod
    def get(cls, path: str, default: Any = None) -> Any:
        path_parts = path.split('.')
        result = None

        for part in path_parts:
            if not result:
                result = cls._config
            
            if not isinstance(result, dict):
                return default

            if not part in result:
                return default

            result = result.get(part)
        
        return result
