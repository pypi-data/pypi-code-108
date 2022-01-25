from __future__ import annotations
import typing as T
import json
from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from dgraph_orm import GQLException
from .node import Node, Params


NodeType = T.TypeVar("NodeType", bound=Node)

GetParamsType = T.TypeVar("GetParamsType", bound=Params)
QueryParamsType = T.TypeVar("QueryParamsType", bound=Params)
EdgesType = T.TypeVar("EdgesType", bound=BaseModel)

ResolverType = T.TypeVar("ResolverType", bound="Resolver")

BaseModelType = T.TypeVar("BaseModelType", bound=BaseModel)


def get_fields_and_nested_fields(cls: T.Type[BaseModelType]) -> T.List[str]:
    field_names: T.List[str] = []
    for field_name, model_field in cls.__fields__.items():
        t = model_field.type_
        if issubclass(t, Node):
            field_names.append(
                f"{field_name}{{{','.join(get_fields_and_nested_fields(t))}}}"
            )
        else:
            field_names.append(field_name)
    return [*field_names, "__typename"]


class Resolver(BaseModel, T.Generic[NodeType]):
    node: T.ClassVar[T.Type[NodeType]]

    query_params: QueryParamsType
    edges: EdgesType

    def gql_fields_str(self) -> str:
        """This does not include the top level..."""
        # TODO this currently just gets all nested fields -> change to make it get edges intelligently
        """DB node is for when you wrap a resolver but need the db node's fields"""
        n = getattr(self, "db_node", getattr(self, "node"))
        fields = get_fields_and_nested_fields(n)
        for resolver_name in self.edges.__fields__.keys():
            resolver: T.Optional[Resolver] = getattr(self.edges, resolver_name, None)
            if resolver:
                child_gql_str = resolver.params_and_fields()
                fields.append(f"{resolver_name} {child_gql_str}")
        return f'{{ {",".join(fields)} }}'

    def params_and_fields(self) -> str:
        return f"{self.query_params.to_str()}{self.gql_fields_str()}"

    def make_get_query_str(self, kwargs_d: dict) -> str:
        kwargs = {k: v for k, v in kwargs_d.items() if v is not None}
        # this is not necessarily true
        if not kwargs:
            pass  # for agg queries (for one)
            # raise GQLException(
            #     f".get requires one field to be given of {list(kwargs_d.keys())}"
            # )
        inner_params = ",".join(
            [
                f"{field_name}: {json.dumps(jsonable_encoder(val))}"
                for field_name, val in kwargs.items()
            ]
        )
        s = f"{{ {self.get_query_name()}({inner_params}){self.gql_fields_str()} }}"
        print(s)
        return s

    @classmethod
    def get_query_name(cls) -> str:
        function_name = cls.node.GQL.get_function_name
        if not function_name:
            raise GQLException(f"No get function found for {cls.node.GQL.typename}!")
        return function_name

    @classmethod
    def query_query_name(cls) -> str:
        function_name = cls.node.GQL.query_function_name
        if not function_name:
            raise GQLException(f"No query function found for {cls.node.GQL.typename}!")
        return function_name

    def make_query_query_str(self) -> str:
        s = f"{{ {self.query_query_name()}{self.params_and_fields()} }}"
        print(s)
        return s

    def make_add_query_str(self) -> str:
        s = f"{{ {self.node.GQL.payload_node_name}{self.params_and_fields()} }}"
        return s

    def make_add_mutation_str(self, include_upsert: bool) -> str:
        typename = self.node.GQL.typename
        add_model_name = self.node.GQL.add_model.__name__
        add_function_name = self.node.GQL.add_function_name
        if not (self.node.GQL.add_model and add_function_name):
            raise GQLException("Add model or add function is missing")
        upsert_str = f", $upsert: Boolean"
        inner_upsert_str = f", upsert: $upsert"
        if include_upsert is False:
            upsert_str = ""
            inner_upsert_str = ""
        s = f"""
            mutation Add{typename}($input: [{add_model_name}!]!{upsert_str}) {{
                {add_function_name}(input: $input{inner_upsert_str}) {self.make_add_query_str()}
            }}
        """
        return s

    def make_update_mutation_str(self) -> str:
        typename = self.node.GQL.typename
        patch_model_name = self.node.GQL.patch_model.__name__
        update_function_name = self.node.GQL.update_function_name
        if not (self.node.GQL.patch_model and update_function_name):
            raise GQLException("Update model or update function is missing")
        s = f"""
            mutation Update{typename}($set: {patch_model_name}, $remove: {patch_model_name}, $filter: {typename}Filter!) {{
                {update_function_name}(input: {{filter: $filter, set: $set, remove: $remove}}) {self.make_add_query_str()}
            }}
        """
        return s

    def make_delete_mutation_str(self) -> str:
        typename = self.node.GQL.typename

        delete_function_name = self.node.GQL.delete_function_name
        if not delete_function_name:
            raise GQLException("Delete function is missing")

        s = f"""
            mutation Delete{typename}($filter: {typename}Filter!) {{
                {delete_function_name}(filter: $filter) {self.make_add_query_str()}
            }}
        """
        return s

    async def query(self) -> T.List[NodeType]:
        s = self.make_query_query_str()
        res = await self.node.GQL.dgraph_client.execute(query_str=s)
        lst: T.List[dict] = res["data"][self.query_query_name()]
        return [self.parse_obj_nested(d) for d in lst]

    def parse_obj_nested(self, gql_d: dict) -> NodeType:
        node: NodeType = self.node.parse_obj(gql_d)
        other_fields = set(gql_d.keys()) - set(node.__fields__.keys()) - {"__typename"}
        for field in other_fields:
            resolver = getattr(self.edges, field, None)
            if not resolver:
                raise GQLException(f"No resolver {field} found!")
            nested_d = gql_d[field]
            value_to_save = nested_d
            if nested_d:
                if (list_or_set := type(nested_d)) in {list, set}:
                    val = list_or_set(resolver.parse_obj_nested(d) for d in nested_d)
                else:
                    val = resolver.parse_obj_nested(nested_d)
                value_to_save = val
            node.cache.add(key=field, resolver=resolver, val=value_to_save, gql_d=gql_d)
        node._used_resolver = self
        node._original_dict = node.dict()
        return node

    async def _get(self, kwargs_d: dict) -> T.Optional[NodeType]:
        s = self.make_get_query_str(kwargs_d=kwargs_d)
        res = await self.node.GQL.dgraph_client.execute(query_str=s)
        obj = res["data"][self.get_query_name()]
        if obj:
            return self.parse_obj_nested(obj)
        return None

    @staticmethod
    def resolvers_by_typename() -> T.Dict[str, T.Type[Resolver]]:
        d = {}
        subs = Resolver.__subclasses__()
        for sub in subs:
            typename = sub.node.GQL.typename
            if typename in d:
                raise GQLException(
                    f"Two Resolvers share the typename {typename}: ({sub.__name__}, {d[typename].__name__})"
                )
            d[typename] = sub
        return d
