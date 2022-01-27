from dataclasses import fields
from typing import Optional, Type, Union, cast

from simple_graphql.django.types import (
    ModelClass,
    ModelConfig,
    ModelSchemaConfig,
    ModelWithMeta,
)


def extract_schema_config(config: Optional[ModelConfig]) -> Optional[ModelSchemaConfig]:
    if not config:
        return None

    # TODO: Maybe add type validation (pydantic?)
    return ModelSchemaConfig(
        **{
            field.name: getattr(config, field.name, None)
            for field in fields(ModelSchemaConfig)
        }
    )


def extract_extra_meta_config(extra_meta: Optional[Type]) -> ModelSchemaConfig:
    return (
        extract_schema_config(getattr(extra_meta, "config", None))
        or ModelSchemaConfig.get_defaults()
    )


def get_model_graphql_meta(
    model_cls: Union[ModelClass, ModelWithMeta]
) -> Optional[ModelSchemaConfig]:
    if not hasattr(model_cls, "GraphQL"):
        return None
    # TODO: Remove the cast once mypy is more smart
    return extract_schema_config(cast(ModelWithMeta, model_cls).GraphQL)
