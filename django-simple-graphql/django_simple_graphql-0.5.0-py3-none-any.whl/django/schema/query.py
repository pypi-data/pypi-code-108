from typing import Dict, Optional, Type

import graphene
from graphene.utils.str_converters import to_snake_case
from graphene_django import DjangoObjectType

from simple_graphql.django.fields import DjangoAutoConnectionField
from simple_graphql.django.fields.node import DjangoAutoNode
from simple_graphql.django.types import ModelClass, ModelSchemaConfig


def build_ordering_enum(
    *, model_cls: ModelClass, args: ModelSchemaConfig
) -> Optional[graphene.Enum]:
    if not args.ordering_fields:
        return None
    return graphene.Enum(
        f"{model_cls.__name__}Ordering",
        [
            (f"{x}_{direction}".upper(), x if direction == "asc" else f"-{x}")
            for x in (args.ordering_fields or [])
            for direction in ("asc", "desc")
        ],
    )


def build_query_fields(
    *,
    model_cls: ModelClass,
    node_cls: Type[DjangoObjectType],
) -> Dict[str, graphene.Field]:
    query_name = to_snake_case(model_cls.__name__)
    return {
        f"get_{query_name}": DjangoAutoNode.Field(node_cls),
        f"list_{query_name}": DjangoAutoConnectionField(node_cls=node_cls),
    }
