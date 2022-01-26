from __future__ import annotations
import typing as T
from pydantic import BaseModel
from dgraph_orm.resolver import Resolver

Arguments = T.Dict[str, T.Any]

try:
    from strawberry.types.nodes import SelectedField
except Exception as _:

    class SelectedField(BaseModel):
        arguments: Arguments = {}
        name: str
        selections: T.List[SelectedField]


def camel_to_snake(s):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")


class NestedField(BaseModel):
    args: Arguments = {}
    children: T.Dict[str, NestedField] = {}


def nested_field_from_selected_field(
    selected_field: SelectedField,
) -> NestedField:
    children: T.Dict[str, NestedField] = {}
    for child in selected_field.selections:
        if child.selections:
            children[camel_to_snake(child.name)] = nested_field_from_selected_field(
                selected_field=child
            )
    snake_arguments = {}
    if getattr(selected_field, "arguments", None):
        snake_arguments = {
            camel_to_snake(key): val for key, val in selected_field.arguments.items()
        }
    return NestedField(args=snake_arguments, children=children)


ResolverType = T.TypeVar("ResolverType", bound=Resolver)


def resolver_from_nested_field(
    nested_field: NestedField, root_resolver: ResolverType
) -> ResolverType:
    # add args to root resolver
    for arg_name, arg_value in nested_field.args.items():
        if arg_name in root_resolver.query_params.__fields__:
            if hasattr(arg_value, "to_pydantic"):
                arg_value = arg_value.to_pydantic()
            setattr(root_resolver.query_params, arg_name, arg_value)
    for edge_name, edge_field in root_resolver.edges.__fields__.items():
        if edge_name in nested_field.children:
            nested_field_child = nested_field.children[edge_name]
            child_resolver = edge_field.type_()
            child_resolver = resolver_from_nested_field(
                nested_field=nested_field_child, root_resolver=child_resolver
            )
            setattr(root_resolver.edges, edge_name, child_resolver)
    return root_resolver


def resolver_from_selected_fields(
    selected_fields: T.List[SelectedField], root_resolver: ResolverType
) -> ResolverType:
    nested_field = nested_field_from_selected_field(selected_field=selected_fields[0])
    return resolver_from_nested_field(
        nested_field=nested_field, root_resolver=root_resolver
    )


NestedField.update_forward_refs()
