from functools import partial
from typing import Any, Dict, Optional, Type, Union

import graphene
from django.db.models import QuerySet
from graphene.types.mountedtype import MountedType
from graphene.types.unmountedtype import UnmountedType
from graphene_django.filter import DjangoFilterConnectionField

from simple_graphql.django.config import extract_extra_meta_config
from simple_graphql.django.fields.authorize import authorize_query
from simple_graphql.django.search import order_qs, search_qs
from simple_graphql.django.types import ModelInstance, ModelSchemaConfig


class DjangoAutoConnectionField(DjangoFilterConnectionField):
    ordering_options: Optional[graphene.Enum]
    config: ModelSchemaConfig

    def __init__(
        self,
        node_cls: Type[graphene.ObjectType],
        **kwargs: Union[UnmountedType, MountedType],
    ):

        extra_meta = getattr(node_cls, "ExtraMeta", None)
        self.config = extract_extra_meta_config(extra_meta)
        self.ordering_options = getattr(extra_meta, "ordering_options", None)

        if self.ordering_options:
            kwargs.setdefault("order_by", graphene.Argument(self.ordering_options))
        if self.config.search_fields:
            kwargs.setdefault("search_query", graphene.String())

        # graphene-django is shadowing "order_by", so we're skipping it's super
        # call by copying its initializaiton here
        self._fields = None
        self._provided_filterset_class = None
        self._filterset_class = None
        self._filtering_args = None
        self._extra_filter_meta = None
        self._base_args = None

        super(DjangoFilterConnectionField, self).__init__(node_cls, **kwargs)

    @classmethod
    def resolve_queryset(
        cls, connection, iterable, info, args: Dict[str, Any], *_args, **kwargs
    ) -> QuerySet[ModelInstance]:
        config: ModelSchemaConfig = kwargs.pop("config")
        ordering_options: Optional[graphene.Enum] = kwargs.pop("ordering_options", None)

        authorize_query(config, info)

        qs = super().resolve_queryset(
            connection, iterable, info, args, *_args, **kwargs
        )

        if config.search_fields:
            qs = search_qs(qs, config.search_fields, args.get("search_query", None))

        if ordering_options:
            ordering = args.get("order_by", None)
            qs = order_qs(qs, ordering)

        return qs

    def get_queryset_resolver(self):
        return partial(
            self.resolve_queryset,
            filterset_class=self.filterset_class,
            filtering_args=self.filtering_args,
            ordering_options=self.ordering_options,
            config=self.config,
        )
