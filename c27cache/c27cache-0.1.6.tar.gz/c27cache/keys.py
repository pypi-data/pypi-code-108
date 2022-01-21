from lib2to3.pgen2.pgen import generate_grammar
from typing import Any, List
from c27cache.config import C27Cache


class C27CacheKeys:
    @staticmethod
    async def generate_key(
        key: str, config: C27Cache, obj: Any = None, obj_attr: str = None
    ) -> str:
        """Converts a raw key passed by the user to a key with an parameter passed by the user and associates a namespace"""

        _key = (
            key.format(
                getattr(obj, obj_attr),
            )
            if obj
            else key
        )

        namespaced_key = await C27CacheKeys.generate_namespaced_key(
            key=_key, config=config
        )
        return namespaced_key

    @staticmethod
    async def generate_keys(
        keys: List[str], config: C27Cache, obj: Any = None, obj_attr: str = None
    ) -> List[str]:
        """Converts a list of raw keys passed by the user to a list of namespaced keys with an optional parameter if passed"""
        
        namespaced_keys = [
            await C27CacheKeys.generate_key(
                key=k, config=config, obj=obj, obj_attr=obj_attr
            )
            for k in keys
        ]
        return namespaced_keys

    @staticmethod
    async def generate_namespaced_key(key: str, config: C27Cache) -> str:
        """Adds a namespace to the key"""
        return f"{config.namespace}:{key}".replace(" ", "")
