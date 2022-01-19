from __future__ import annotations
import keyword
import typing as T
from pathlib import Path
import json
import re
from black import format_str, FileMode
import graphql
from pydantic import BaseModel

NODE_CONFIG_NAME = "GQL"
ORM_MODEL_NAME = "GQLInput"
NODE_MODEL_NAME = "Node"
DEFAULT_INDENT = "    "


def imports() -> str:
    lines = [
        "from __future__ import annotations",
        "from enum import Enum",
        "from datetime import datetime, date",
        "from pydantic import BaseModel, Field",
        f"from dgraph_orm import {ORM_MODEL_NAME}, Node, GQLException",
        f"from dgraph_orm.ACL.client import DgraphClient",
        "from dgraph_orm.resolver import Params, Resolver",
        "from typing import Optional, Set, Type, ClassVar, List",
    ]
    return "\n".join(lines)


scalar_d = {
    "String": "str",
    "Int": "int",
    "Float": "float",
    "Boolean": "bool",
    "ID": "str",
    "Int64": "int",
    "DateTime": "datetime",
}


def create_payload_node_name(node_name: str) -> str:
    return node_name[0].lower() + node_name[1:]


class NodeConfig(BaseModel):
    node_name: str

    resolver_name: str = None

    # object names
    add_model: str = None
    patch_model: str = None
    ref_model: str = None

    # queries
    get_function_name: str = None
    query_function_name: str = None
    payload_node_name: str = None

    # mutations
    add_function_name: str = None
    update_function_name: str = None
    delete_function_name: str = None

    url: str
    uid_field_name: str

    # not used in GQL
    node_path: str = None

    @classmethod
    def default_from_node_name(cls, node_name: str, url: str) -> NodeConfig:
        return cls(
            node_name=node_name,
            resolver_name=f"{node_name}Resolver",
            get_function_name=f"get{node_name}",
            query_function_name=f"query{node_name}",
            payload_node_name=f"{create_payload_node_name(node_name)}",
            add_function_name=f"add{node_name}",
            update_function_name=f"update{node_name}",
            delete_function_name=f"delete{node_name}",
            add_model=f"Add{node_name}Input",
            patch_model=f"{node_name}Patch",
            ref_model=f"{node_name}Ref",
            url=url,
            uid_field_name="id",
        )

    def create_aggregate(
        self, postfix: str = None, get_function_name: str = None
    ) -> NodeConfig:
        postfix = "AggregateResult" if postfix is None else postfix
        get_function_name = (
            f"aggregate{self.node_name}"
            if get_function_name is None
            else get_function_name
        )
        node_name = f"{self.node_name}{postfix}"
        return self.__class__(
            node_name=node_name,
            url=self.url,
            get_function_name=get_function_name,
            uid_field_name="count",
        )

    @staticmethod
    def str_or_none(s: T.Optional[str], quotes: bool = False) -> str:
        if s is None:
            return "None"
        if quotes:
            s = f'"{s}"'
        return s

    def to_config_class(self) -> str:
        s = f"""
class {NODE_CONFIG_NAME}:
    typename = "{self.node_name}"
    payload_node_name = {self.str_or_none(self.payload_node_name, quotes=True)}
    resolver: Type[{self.str_or_none(self.resolver_name)}]

    # models
    add_model: Type[{self.str_or_none(self.add_model)}] = {self.str_or_none(self.add_model)}
    patch_model: Type[{self.str_or_none(self.patch_model)}] = {self.str_or_none(self.patch_model)}
    ref_model: Type[{self.str_or_none(self.ref_model)}] = {self.str_or_none(self.ref_model)}

    # functions
    get_function_name: str = {self.str_or_none(self.get_function_name, quotes=True)}
    query_function_name: str = {self.str_or_none(self.query_function_name, quotes=True)}

    add_function_name: str = {self.str_or_none(self.add_function_name, quotes=True)}
    update_function_name: str = {self.str_or_none(self.update_function_name, quotes=True)}
    delete_function_name: str = {self.str_or_none(self.delete_function_name, quotes=True)}

    url: str = "{self.url}"
    uid_field_name: str = "{self.uid_field_name}"
    
    dgraph_client: DgraphClient = client
        """

        return s


def indent_lines(s: str, indent: str = DEFAULT_INDENT) -> str:
    chunks = s.split("\n")
    return indent + f"\n{indent}".join(chunks)


GQL_Type = T.TypeVar("GQL_Type", bound=graphql.GraphQLType)


class PythonType(BaseModel):
    pure_value: str
    is_pure_value_required: bool
    is_list: bool
    is_list_required: bool


def _parse_to_python(
    gql_type: T.Union[
        graphql.GraphQLList,
        graphql.GraphQLEnumType,
        graphql.GraphQLScalarType,
        graphql.GraphQLNonNull,
        graphql.GraphQLObjectType,
    ],
    first: bool = False,
) -> str:
    if first:
        if not isinstance(gql_type, graphql.GraphQLNonNull):
            return f"Optional[{_parse_to_python(gql_type)}]"
    if isinstance(gql_type, graphql.GraphQLNonNull):
        return _parse_to_python(gql_type.of_type)

    if isinstance(gql_type, graphql.GraphQLList):
        prefix = "List["
        postfix = "]"
        if not isinstance(gql_type.of_type, graphql.GraphQLNonNull):
            prefix += "Optional["
            postfix += "]"
        return f"{prefix}{_parse_to_python(gql_type.of_type)}{postfix}"

    if isinstance(gql_type, graphql.GraphQLScalarType):
        return scalar_d[str(gql_type)]

    s = str(gql_type)

    return s


def parse_to_python(
    gql_type: T.Union[
        graphql.GraphQLList,
        graphql.GraphQLEnumType,
        graphql.GraphQLScalarType,
        graphql.GraphQLNonNull,
        graphql.GraphQLObjectType,
    ],
    remove_optional_list: bool = False,
) -> str:
    s = _parse_to_python(gql_type=gql_type, first=True)
    optional_key = "Optional[List["
    if remove_optional_list and optional_key in s:
        s = s.replace(optional_key, "List[")[:-1]
    return s


def get_pure_type(gql_type: GQL_Type) -> T.Type[GQL_Type]:
    while hasattr(gql_type, "of_type"):
        gql_type = gql_type.of_type
    return gql_type


def python_line_from_gql_field(
    field_name: str,
    gql_field: T.Union[
        graphql.GraphQLField, graphql.GraphQLInputField, graphql.GraphQLArgument
    ],
    is_immutable: bool = False,
) -> str:
    python_type_str = parse_to_python(gql_type=gql_field.type)

    field_value_str = "Field("
    inner_value_type = "..."

    # check if optional
    if python_type_str.startswith("Optional["):
        inner_value_type = "None"

    if field_name in keyword.kwlist:
        inner_value_type += f', alias="{field_name}"'
        field_name = f"{field_name}_"

    if is_immutable:
        inner_value_type += ", allow_mutation=False"

    field_value_str = f"{field_value_str}{inner_value_type})"
    s = f"{field_name}: {python_type_str} = {field_value_str}"

    return s


def params_from_gql_arg(field_name: str, gql_arg: graphql.GraphQLArgument) -> str:
    python_type_str = parse_to_python(gql_type=gql_arg.type)

    default_value = None
    # check if optional
    if python_type_str.startswith("Optional["):
        default_value = "None"

    default_value_str = "" if default_value is None else f" = {default_value}"

    return f"{field_name}: {python_type_str}{default_value_str}"


FilterType = T.TypeVar("FilterType", bound=graphql.GraphQLType)


def filter_schema(
    schema: graphql.GraphQLSchema, gql_cls: T.Type[FilterType]
) -> T.Dict[str, FilterType]:
    filtered_d: T.Dict[str, FilterType] = dict()
    for type_name, type_object in schema.type_map.items():
        if isinstance(type_object, gql_cls):
            filtered_d[type_name] = type_object
    return filtered_d


def _build_enums(enum_types_d: T.Dict[str, graphql.GraphQLEnumType]) -> str:
    enum_str_lst: T.List[str] = []
    for type_name, object_type in enum_types_d.items():
        fields_str = "\n".join(
            [f'{val} = "{val}"' for val in object_type.values.keys()]
        )
        s = f"class {type_name}(str, Enum):\n{indent_lines(fields_str)}"
        enum_str_lst.append(s)
    enums_str = "\n".join(enum_str_lst)
    s = format_str(enums_str, mode=FileMode())
    return s


def build_enums(schema: graphql.GraphQLSchema) -> str:
    return _build_enums(filter_schema(schema, graphql.GraphQLEnumType))


def to_pydantic_line(input_name: str) -> str:
    s = f"""
def to_pydantic(self) -> {input_name}:
    return {input_name}.parse_raw(json.dumps(self, cls=EnhancedJSONEncoder))
    """
    return s


def _build_inputs(
    input_types_d: T.Dict[str, graphql.GraphQLInputObjectType],
    for_strawberry: bool = False,
) -> str:
    type_str_lst: T.List[str] = []
    for type_name, object_type in input_types_d.items():
        field_str_lst: T.List[str] = []
        for field_name, gql_field in object_type.fields.items():
            python_line = python_line_from_gql_field(
                field_name=field_name, gql_field=gql_field
            )
            if for_strawberry:
                pure_type = get_pure_type(gql_type=gql_field.type)
                if pure_type not in scalar_d.values():
                    python_line = python_line.replace(
                        str(pure_type), f"Strawberry.{pure_type}"
                    )
                    python_line = (
                        python_line.replace("Field", "strawberry.field")
                        .replace("alias=", "name=")
                        .replace("None", "default=None")
                        .replace("...", "")
                    )
                # ending = "" if "..." in python_line else " = None"
                # python_line = f'{python_line[:python_line.index(" =")]}{ending}'
            field_str_lst.append(python_line)
        if for_strawberry:
            # sort field_str_lst for straw putting required fields first
            field_str_lst.sort(key=lambda _: _.count("="))
        fields_str = "\n".join(field_str_lst)
        class_str = f"class {type_name}({ORM_MODEL_NAME}):"
        if for_strawberry:
            class_str = f"@strawberry.input\nclass {type_name}:"
        type_str = f"{class_str}\n{indent_lines(fields_str)}"
        if for_strawberry:
            type_str += f"\n{indent_lines(to_pydantic_line(input_name=type_name))}"
        type_str_lst.append(type_str)
    types_str = "\n".join(type_str_lst)
    s = format_str(types_str, mode=FileMode())
    return s


def build_inputs(schema: graphql.GraphQLSchema, for_strawberry: bool = False) -> str:
    return _build_inputs(
        filter_schema(schema, graphql.GraphQLInputObjectType),
        for_strawberry=for_strawberry,
    )


def _build_non_input_non_nodes(
    object_types_d: T.Dict[str, graphql.GraphQLObjectType]
) -> str:
    type_str_lst: T.List[str] = []
    for type_name, object_type in object_types_d.items():
        field_str_lst: T.List[str] = []
        for field_name, gql_field in object_type.fields.items():
            python_line = python_line_from_gql_field(
                field_name=field_name, gql_field=gql_field
            )
            field_str_lst.append(python_line)
        fields_str = "\n".join(field_str_lst)
        type_str = f"class {type_name}({ORM_MODEL_NAME}):\n{indent_lines(fields_str)}"
        type_str_lst.append(type_str)
    types_str = "\n".join(type_str_lst)
    s = format_str(types_str, mode=FileMode())
    return s


def build_non_input_non_nodes(
    schema: graphql.GraphQLSchema, node_names: T.List[str]
) -> str:
    d = {
        key: val
        for key, val in filter_schema(schema, graphql.GraphQLObjectType).items()
        if key not in node_names
    }
    return _build_non_input_non_nodes(d)


def _build_nodes(
    node_types_d: T.Dict[str, graphql.GraphQLObjectType],
    node_config_d: T.Dict[str, NodeConfig],
    schema: graphql.GraphQLSchema,
    hydrated: bool = False,
) -> str:
    type_str_lst: T.List[str] = []
    for type_name, object_type in node_types_d.items():
        node_builder = NodeBuilder(
            node_name=type_name,
            gql_object=object_type,
            node_config=node_config_d[type_name],
            schema=schema,
            hydrated=hydrated and node_config_d[type_name].node_path,
        )
        node_resolver_s = node_builder.build_node_and_resolver()
        type_str_lst.append(node_resolver_s)
    types_str = "\n".join(type_str_lst)
    s = format_str(types_str, mode=FileMode())
    return s


def build_nodes(
    schema: graphql.GraphQLSchema,
    node_configs: T.List[NodeConfig],
    hydrated: bool = False,
) -> str:
    nodes_d = filter_schema(schema, graphql.GraphQLObjectType)
    node_names = [n.node_name for n in node_configs]
    filtered_d = {
        node_name: node_object
        for node_name, node_object in nodes_d.items()
        if node_name in node_names
    }
    return _build_nodes(
        filtered_d,
        {n.node_name: n for n in node_configs},
        schema=schema,
        hydrated=hydrated,
    )


class NodeBuilder:
    def __init__(
        self,
        node_name: str,
        node_config: NodeConfig,
        gql_object: graphql.GraphQLObjectType,
        schema: graphql.GraphQLSchema,
        hydrated: bool = False,
    ):
        self.node_name = node_name
        self.node_config = node_config
        self.gql_object = gql_object

        self.fields: T.Dict[str, graphql.GraphQLField] = dict()
        self.edges: T.Dict[str, graphql.GraphQLField] = dict()

        self.create_edges_and_fields(gql_object=gql_object)

        self.schema = schema
        self.query_type = schema.query_type
        self.immutable_fields = []
        if self.node_config.get_function_name:
            self.immutable_fields = self.query_type.fields[
                self.node_config.get_function_name
            ].args.keys()

        self.mutation_type = schema.mutation_type

        self.hydrated = hydrated

    @property
    def resolver_name(self) -> str:
        return f"{self.node_name}Resolver"

    def create_edges_and_fields(self, gql_object: graphql.GraphQLObjectType) -> None:
        for field_name, gql_field in gql_object.fields.items():
            if isinstance(get_pure_type(gql_field.type), graphql.GraphQLObjectType):
                self.edges[field_name] = gql_field
            else:
                self.fields[field_name] = gql_field

    def build_edge_functions(self) -> str:
        edge_str_lst: T.List[str] = []
        for edge_name, gql_field in self.edges.items():
            return_type = parse_to_python(
                gql_type=gql_field.type, remove_optional_list=True
            )
            resolver_name = f"{get_pure_type(gql_field.type)}Resolver"
            s = f"""
async def {edge_name}(self, resolver: {resolver_name} = None, refresh: bool = False, use_stale: bool = False) -> {return_type}:
    return await self.resolve(name="{edge_name}", resolver=resolver, refresh=refresh, use_stale=use_stale)
            """
            edge_str_lst.append(s)
        edges_str = "\n".join(edge_str_lst)
        return edges_str

    def build_add(self) -> str:
        if self.node_config.add_function_name is None:
            return ""
        has_upsert = (
            "upsert"
            in self.mutation_type.fields[self.node_config.add_function_name].args
        )
        upsert_str = ", upsert: bool = False"
        if not has_upsert:
            upsert_str = ""
        add_upsert_str = f", upsert=upsert"
        if not has_upsert:
            add_upsert_str = ""
        return f"""
@classmethod
async def add(cls, *, input: {self.node_config.add_model}, resolver: {self.resolver_name} = None{upsert_str}, use_one_time: bool = False) -> {self.node_name}:
    return (await cls.add_many(inputs=[input], resolver=resolver{add_upsert_str}, use_one_time=use_one_time))[0]

@classmethod
async def add_many(cls, *, inputs: List[{self.node_config.add_model}], resolver: {self.resolver_name} = None{upsert_str}, use_one_time: bool = False) -> List[{self.node_name}]:
    return await cls._add(inputs=inputs, given_resolver=resolver, upsert={"upsert" if has_upsert else "None"}, use_one_time=use_one_time)
        """

    def build_update(self) -> str:
        if self.node_config.update_function_name is None:
            return ""

        # now get the patch
        patch_model: graphql.GraphQLInputObjectType = self.schema.type_map[
            self.node_config.patch_model
        ]

        patchable_fields = patch_model.fields.keys()

        arg_str_lst: T.List[str] = []
        to_set_names: T.List[str] = []
        to_remove_names: T.List[str] = []
        for field_name, gql_field in self.edges.items():
            if field_name not in patchable_fields:
                continue
            main_str = ""
            return_type = parse_to_python(
                gql_type=gql_field.type, remove_optional_list=True
            )
            python_type_and_value = f"{return_type} = None"

            set_str = f"{field_name}: {python_type_and_value}"
            to_set_names.append(field_name)
            main_str += set_str

            if not isinstance(gql_field.type, graphql.GraphQLNonNull):
                # if not func.is_required_for_node():
                remove_str = f"remove_{field_name}: {python_type_and_value}"
                main_str += f", {remove_str}"
                to_remove_names.append(field_name)
            arg_str_lst.append(main_str)
        edges_arg_str = ", ".join(arg_str_lst)
        to_set_d_lst: T.List[str] = [f'"{name}": {name}' for name in to_set_names]
        to_remove_d_lst: T.List[str] = [
            f'"{name}": remove_{name}' for name in to_remove_names
        ]
        to_set_d_str = f'{{{", ".join(to_set_d_lst)}}}'
        to_remove_d_str = f'{{{", ".join(to_remove_d_lst)}}}'
        return f"""
async def update(self, resolver: {self.resolver_name} = None, {edges_arg_str}) -> bool:
    return await self._update(given_resolver=resolver, to_set={to_set_d_str}, to_remove={to_remove_d_str})
        """

    def build_fields(self) -> str:
        field_str_lst: T.List[str] = []
        for field_name, gql_field in self.fields.items():
            python_line = python_line_from_gql_field(
                field_name=field_name,
                gql_field=gql_field,
                is_immutable=field_name in self.immutable_fields,
            )
            # change from List to Set for fields on Node
            python_line = python_line.replace("List[", "Set[")
            field_str_lst.append(python_line)
        fields_str = "\n".join(field_str_lst)
        return fields_str

    def build_node_and_resolver(self) -> str:
        node_str = self.build_node()
        resolver_str = self.build_resolver()
        s = f"{self.node_name}.{NODE_CONFIG_NAME}.resolver = {self.node_name}Resolver"
        final_s = "\n".join([node_str, resolver_str, s])
        return format_str(final_s, mode=FileMode())

    def build_node(self) -> str:
        fields_str = self.build_fields()
        if self.hydrated:
            fields_str = ""
        edges_funcs_str = self.build_edge_functions()
        add_func_str = self.build_add()
        update_func_str = self.build_update()
        config_str = self.node_config.to_config_class()
        class_str = f"class {self.node_name}({NODE_MODEL_NAME}):"
        if self.hydrated:
            class_str = f"class {self.node_name}({self.node_name}Hydrated):"
        lines = [
            class_str,
            indent_lines(fields_str),
            indent_lines(edges_funcs_str),
            indent_lines(add_func_str),
            indent_lines(update_func_str),
            indent_lines(config_str),
        ]
        s = "\n".join(lines)
        return format_str(s, mode=FileMode())

    def build_resolver(self) -> str:
        get_field = self.query_type.fields.get(self.node_config.get_function_name, None)
        query_field = self.query_type.fields.get(
            self.node_config.query_function_name, None
        )

        resolver_builder = ResolverBuilder(
            node_name=self.node_name,
            get_field=get_field,
            query_field=query_field,
            edge_field_d=self.edges,
        )

        resolver_str = resolver_builder.build_resolver()
        return resolver_str


def build_model_fields_from_field(field: graphql.GraphQLField) -> str:
    lines: T.List[str] = []
    for arg_name, arg in field.args.items():
        line = python_line_from_gql_field(field_name=arg_name, gql_field=arg)
        lines.append(line)
    if not lines:
        return "pass"
    return "\n".join(lines)


class ResolverBuilder:
    def __init__(
        self,
        node_name: str,
        get_field: T.Optional[graphql.GraphQLField],
        query_field: T.Optional[graphql.GraphQLField],
        edge_field_d: T.Optional[T.Dict[str, graphql.GraphQLField]],
    ):
        self.node_name = node_name
        self.get_field = get_field
        self.query_field = query_field
        self.edge_field_d = edge_field_d

    def build_get_params(self) -> str:
        if not self.get_field:
            fields_str = "pass"
        else:
            fields_str = build_model_fields_from_field(field=self.get_field)
        return f"class {self.node_name}GetParams(Params):\n{indent_lines(fields_str)}"

    def build_query_params(self) -> str:
        if not self.query_field:
            fields_str = "pass"
        else:
            fields_str = build_model_fields_from_field(field=self.query_field)
        return f"class {self.node_name}QueryParams(Params):\n{indent_lines(fields_str)}"

    def build_edges(self) -> str:
        if not self.edge_field_d:
            fields_str = "pass"
        else:
            lines: T.List[str] = []
            for arg_name, arg in self.edge_field_d.items():
                resolver_name = f"{get_pure_type(arg.type)}Resolver"
                line = f"{arg_name}: Optional[{resolver_name}] = None"
                lines.append(line)
            if not lines:
                return "pass"
            fields_str = "\n".join(lines)
        return f"class {self.node_name}Edges(BaseModel):\n{indent_lines(fields_str)}"

    def build_get_functions(self) -> str:
        if not self.get_field:
            return ""
        params_str = ", ".join(
            [
                f"{params_from_gql_arg(arg_name, arg)}"
                for arg_name, arg in self.get_field.args.items()
            ]
        )
        arg_names = self.get_field.args.keys()
        kwargs_str = ", ".join(f'"{arg_name}": {arg_name}' for arg_name in arg_names)
        kwargs_eq_str = ", ".join(f"{arg_name}={arg_name}" for arg_name in arg_names)
        kwargs_d_str = f"{{{kwargs_str}}}"
        print_str = " and ".join([f"{{{arg_name}=}}" for arg_name in arg_names])
        get = f"""
async def get(self, {params_str}) -> Optional[{self.node_name}]:
    return await self._get({kwargs_d_str})
        """
        gerror = f"""
async def gerror(self, {params_str}) -> {self.node_name}:
    node = await self.get({kwargs_eq_str})
    if not node:
        raise GQLException(f"No {self.node_name} with {print_str}")
    return node
        """
        return f"{get}\n{gerror}"

    @property
    def resolver_name(self) -> str:
        return self.node_name + "Resolver"

    def build_query_functions(self) -> str:
        if not self.query_field:
            return ""
        f_str_lst: T.List[str] = []
        for arg_name, arg in self.query_field.args.items():
            python_line = f"{arg_name}: {parse_to_python(gql_type=arg.type)} = None"
            f_str = f"""
def {arg_name}(self, {python_line}, /) -> {self.resolver_name}:
    if {arg_name} is not None:
        if not issubclass({arg_name}.__class__, BaseModel):
            if hasattr({arg_name}, "to_pydantic"):
                {arg_name} = {arg_name}.to_pydantic()
    self.query_params.{arg_name} = {arg_name}
    return self
            """
            f_str_lst.append(f_str.strip())
        return "\n\n".join(f_str_lst)

    def build_edge_functions(self) -> str:
        if not self.edge_field_d:
            return ""
        f_str_lst: T.List[str] = []
        for edge_name, edge_field in self.edge_field_d.items():
            edge_resolver = f"{get_pure_type(edge_field.type)}Resolver"
            f_str = f"""
def {edge_name}(self, _: Optional[{edge_resolver}] = None, /) -> {self.resolver_name}:
    self.edges.{edge_name} = _ or {edge_resolver}()
    return self
            """
            f_str_lst.append(f_str.strip())
        return "\n\n".join(f_str_lst)

    def build_resolver(self) -> str:
        get_params = self.build_get_params()
        query_params = self.build_query_params()
        edges = self.build_edges()

        classes_str_lst = [get_params, query_params, edges]
        classes_str = "\n\n".join(classes_str_lst)
        classes_str = format_str(classes_str, mode=FileMode())

        get_functions = self.build_get_functions()
        query_functions = self.build_query_functions()
        edge_functions = self.build_edge_functions()

        functions_str_lst = [get_functions, query_functions, edge_functions]
        functions_str = "\n\n".join(functions_str_lst)
        functions_str = format_str(functions_str, mode=FileMode())

        edges_str = f"{self.node_name}Edges"
        query_str = f"{self.node_name}QueryParams"

        resolver_header = f"""
class {self.node_name}Resolver(Resolver[{self.node_name}]):
    node: ClassVar[Type[{self.node_name}]] = {self.node_name}
    edges: {edges_str} = Field(default_factory={edges_str})
    query_params: {query_str} = Field(default_factory={query_str}) 
        """

        classes_with_resolver_header = f"{classes_str}\n{resolver_header}"
        classes_with_resolver_header = format_str(
            classes_with_resolver_header, mode=FileMode()
        )

        full_s = f"{classes_with_resolver_header}\n{indent_lines(functions_str)}"
        full_s = format_str(full_s, mode=FileMode())
        return full_s


def get_class_names_from_str(s: str) -> T.List[str]:
    class_names_pattern = r"class (\w*)\("
    return re.findall(class_names_pattern, s)


def build_strawberry_class(schema: graphql.GraphQLSchema) -> str:
    pre = """
import dataclasses
import json
import strawberry

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)
    """

    enum_names: T.List[str] = []
    for type_name, gql_type in schema.type_map.items():
        if isinstance(gql_type, graphql.GraphQLEnumType):
            if not type_name.startswith("__"):
                enum_names.append(type_name)
    enums_str = "\n".join([f"{name} = strawberry.enum({name})" for name in enum_names])

    inputs_s = build_inputs(schema=schema, for_strawberry=True)
    lines = [
        pre,
        f"class Strawberry:",
        indent_lines(enums_str),
        indent_lines(inputs_s),
    ]
    s = "\n".join(lines)
    s = format_str(s, mode=FileMode())
    return s


def build_all(
    dgraph_client_str: str,
    node_path_imports_str,
    schema: graphql.GraphQLSchema,
    node_configs: T.List[NodeConfig],
    include_strawberry: bool = False,
    hydrated: bool = False,
) -> str:
    # order map so that you can track db schema changes
    schema.type_map = {
        k: schema.type_map[k] for k in sorted(list(schema.type_map.keys()))
    }
    enums = build_enums(schema)
    inputs = build_inputs(schema)
    non_input_non_nodes = build_non_input_non_nodes(
        schema, node_names=[n.node_name for n in node_configs]
    )
    nodes = build_nodes(schema, node_configs=node_configs, hydrated=hydrated)

    update_forward_ref_lines = [
        f"{n.node_name}Edges.update_forward_refs()" for n in node_configs
    ]
    update_forward_ref_nodes = [
        f"{n.node_name}.update_forward_refs()" for n in node_configs
    ]

    update_forward_ref_lines_str = "\n".join(update_forward_ref_lines)
    update_forward_ref_nodes_str = "\n".join(update_forward_ref_nodes)

    input_names = get_class_names_from_str(inputs)
    non_input_names = get_class_names_from_str(non_input_non_nodes)

    update_forward_ref_input_str = "\n".join(
        [f"{name}.update_forward_refs()" for name in input_names]
    )
    update_forward_ref_type_str = "\n".join(
        [f"{name}.update_forward_refs()" for name in non_input_names]
    )

    lines = [
        imports(),
        dgraph_client_str,
        node_path_imports_str,
        enums,
        inputs,
        non_input_non_nodes,
        nodes,
        update_forward_ref_input_str,
        update_forward_ref_type_str,
        update_forward_ref_lines_str,
        update_forward_ref_nodes_str,
    ]
    final_s = "\n".join(lines)
    s = format_str(final_s, mode=FileMode())
    if include_strawberry:
        straw_str = build_strawberry_class(schema=schema)
        s += f"\n{straw_str}"
        s = format_str(s, mode=FileMode())
    return s


from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from dgraph_orm.ACL.client import DgraphClient


async def schema_from_url(
    url: str,
    api_key: str = None,
    user_id: str = None,
    password: str = None,
    namespace: int = None,
) -> graphql.GraphQLSchema:
    headers = {}
    if api_key:
        client = DgraphClient(client_url=url, api_key=api_key)
        await client.login_into_namespace(
            user_id=user_id, password=password, namespace=namespace
        )
        headers = client.headers
    transport = AIOHTTPTransport(url=url, headers=headers)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql(
        """
        {
          __schema {
            types {
              name
            }
          }
        }
    """
    )
    await client.execute_async(query)
    return client.schema


def node_configs_from_app_config(app_name: str, app_config: dict) -> T.List[NodeConfig]:
    url = app_config["url"]
    nodes = app_config["nodes"]
    node_configs: T.List[NodeConfig] = []
    for node_name, data in nodes.items():
        if data.get("default", False):
            node_config = NodeConfig.default_from_node_name(node_name, url=url)
        else:
            config_data = data.get("config", {})
            node_config = NodeConfig(node_name=node_name, url=url, **config_data)
        node_config.node_path = data.get("node_path", None)
        node_configs.append(node_config)
        if data.get("aggregate", False):
            node_configs.append(node_config.create_aggregate())
    return node_configs


def filename_safe(s: str) -> str:
    return "".join([c for c in s if c.isalpha() or c.isdigit() or c == " "]).rstrip()


def build_dgraph_client(app_config: dict) -> str:
    client_url, api_key = app_config["url"], app_config.get("api_key")
    first_line = f'client = DgraphClient.from_cloud(client_url="{client_url}", api_key="{api_key}")'
    if "namespace" not in app_config:
        return first_line
    s = f"""
{first_line}
async def login_client() -> None:
    await client.login_into_namespace(
        user_id="{app_config['user_id']}",
        password="{app_config['password']}",
        namespace={app_config['namespace']},
    )
    """
    return format_str(s, mode=FileMode())


def build_node_path_imports(node_configs: T.List[NodeConfig]) -> str:
    strs: T.List[str] = []
    for node in node_configs:
        if node.node_path:
            strs.append(
                f"from {node.node_path} import {node.node_name} as {node.node_name}Hydrated"
            )
            strs.append(
                f"{node.node_name}Hydrated.GQL.resolver.node = {node.node_name}Hydrated"
            )
    return "\n".join(strs)


async def build_from_app_config(
    app_name: str, app_config: dict, parent_dir: Path, include_strawberry: bool = False
) -> None:
    node_configs = node_configs_from_app_config(
        app_name=app_name, app_config=app_config
    )
    schema = await schema_from_url(
        app_config["url"],
        app_config.get("api_key"),
        app_config.get("user_id"),
        app_config.get("password"),
        app_config.get("namespace"),
    )
    dgraph_client_str = build_dgraph_client(app_config)
    node_path_imports_str = build_node_path_imports(node_configs)
    # build once for models, another for nodes if necessary
    s = build_all(
        dgraph_client_str=dgraph_client_str,
        node_path_imports_str="",
        schema=schema,
        node_configs=node_configs,
        include_strawberry=include_strawberry,
    )
    open(parent_dir / f"{filename_safe(app_name)}.py", "w").write(s)
    print("already build all once")
    if node_path_imports_str:
        s = build_all(
            dgraph_client_str=dgraph_client_str,
            node_path_imports_str=node_path_imports_str,
            schema=schema,
            node_configs=node_configs,
            include_strawberry=include_strawberry,
            hydrated=True,
        )
        open(parent_dir / f"{filename_safe(app_name)}_hydrated.py", "w").write(s)


async def build_from_config(
    config_path: Path, path_to_write_to: Path, include_strawberry: bool = False
) -> None:
    path_to_write_to.mkdir(parents=True, exist_ok=True)
    config = json.loads(open(config_path, "r").read())
    for app_name, app_config in config.items():
        await build_from_app_config(
            app_name=app_name,
            app_config=app_config,
            parent_dir=path_to_write_to,
            include_strawberry=include_strawberry,
        )


if __name__ == "__main__":
    build_from_config(Path("gql_config.json"), Path("generated"))
