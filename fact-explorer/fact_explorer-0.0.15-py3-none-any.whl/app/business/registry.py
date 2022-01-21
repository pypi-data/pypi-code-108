from typing import Any, Dict, Optional, Union, List

from fact_explorer.config import get_configuration, get_logger

log = get_logger("business.registry")
configuration = get_configuration()

try:
    from schema_registry.registries.HttpRegistry import EnrichingHttpSchemaRegistry
    from schema_registry.registries.entities import VersionedType

    registry = EnrichingHttpSchemaRegistry(url=configuration.schema_registry_url)

    async def namespaces(
        with_types: bool = False,
    ) -> Union[List[str], Dict[str, VersionedType]]:
        if with_types:
            res = {}
            for namespace in registry.namespaces:

                res[namespace.name] = {
                    "title": namespace.title,
                    "types": list(registry.types(namespace=namespace.name)),
                }
            return res
        else:
            return [namespace.name for namespace in registry.namespaces]

    async def schema(
        namespace: str, type: str, version: Optional[int]
    ) -> Dict[str, Any]:
        return registry.get(namespace=namespace, type_name=type, version=version)  # type: ignore

    async def schema_registry_enabled() -> bool:
        return True

    async def prewarm_caches() -> None:
        registry.namespaces

except ImportError:

    if configuration.schema_registry_url:
        log.warning(
            (
                "Schema Registry URL configured but schema registry library not available."
                "Registry related features will NOT be available."
            )
        )

    async def namespaces(  # type:ignore
        with_types: bool = False,
    ) -> Union[List[str], Dict]:
        log.debug("Schema Registry not installed. Returning empty result.")
        return []

    async def schema(
        namespace: str, type: str, version: Optional[int]
    ) -> Dict[str, Any]:
        log.debug("Schema Registry not installed. Returning empty result.")
        return {}

    async def schema_registry_enabled() -> bool:
        return False

    async def prewarm_caches() -> None:
        pass
