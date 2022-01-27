from typing import TYPE_CHECKING, Any, Callable, Type

from graphene.relay.node import Node, NodeField

from simple_graphql.django.config import extract_extra_meta_config
from simple_graphql.django.fields.authorize import authorize_query

if TYPE_CHECKING:
    from simple_graphql.django import ModelSchemaConfig


def build_resolver(base_resolver: Callable, config: "ModelSchemaConfig") -> Callable:
    def authorized_resolver(obj: Any, info: Any, **kwargs: Any):
        authorize_query(config, info)
        return base_resolver(obj, info, **kwargs)

    return authorized_resolver


class DjangoAutoNodeField(NodeField):
    config: "ModelSchemaConfig"

    def __init__(self, node: Type, type: Type, **kwargs: Any) -> None:
        self.config = extract_extra_meta_config(getattr(type, "ExtraMeta", None))
        super().__init__(node, type, **kwargs)

    def get_resolver(self, parent_resolver: Callable):
        return build_resolver(super().get_resolver(parent_resolver), self.config)


class DjangoAutoNode(Node):
    @classmethod
    def Field(cls, *args: Any, **kwargs: Any) -> DjangoAutoNodeField:
        return DjangoAutoNodeField(Node, *args, **kwargs)
