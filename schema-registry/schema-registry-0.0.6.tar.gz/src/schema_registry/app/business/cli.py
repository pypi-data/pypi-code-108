from typing import Union
from schema_registry.config import get_configuration
from schema_registry.registries.HttpRegistry import (
    EnrichingHttpSchemaRegistry,
    HttpSchemaRegistry,
)


def get_registry(
    profile: str = "default", extended: bool = False
) -> Union[EnrichingHttpSchemaRegistry, HttpSchemaRegistry]:
    config = get_configuration(profile)

    if extended:
        return EnrichingHttpSchemaRegistry(url=config.schema_registry_url)
    else:
        return HttpSchemaRegistry(url=config.schema_registry_url)
        # TODO: Unsupported methods
