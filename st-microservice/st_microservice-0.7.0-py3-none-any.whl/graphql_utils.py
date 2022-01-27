import decimal
from typing import List, Any
from datetime import date

from graphql import GraphQLError
from graphql.type.definition import GraphQLObjectType, get_named_type
from ariadne import UnionType
from ariadne.types import GraphQLResolveInfo
from sqlalchemy import select
from sqlalchemy.orm import Session
from pyparsing import ParseException

from .starlettebackend import User
from .filter_parser import number_filter_parser, date_filter_parser, boolean_filter_parser


nulldate = date(1753, 1, 1)


model_types = UnionType('ModelTypes')


@model_types.type_resolver
def resolve_error_type(obj, *_):
    return obj.__class__.__name__


def get_dbsession(info) -> Session:
    return info.context['request'].state.dbsession


def get_user(info: GraphQLResolveInfo) -> User:
    return info.context['request'].user


def get_all_records(info, q):
    return get_dbsession(info).execute(q).scalars().unique().all()  # Todo: Watch out for that .unique()


def get_one_record(info, q):
    return get_dbsession(info).execute(q).scalars().first()


def get_one_field(info, q):
    return get_dbsession(info).execute(q).scalar()


def resolve_type_inspector(_, info: GraphQLResolveInfo, type_name):
    gqltype = info.schema.get_type(type_name)
    if gqltype is None or not isinstance(gqltype, GraphQLObjectType):
        return None

    all_filter = hasattr(gqltype, '__all_filter__')
    primary_keys = getattr(gqltype, '__primary_keys__', None)

    field_details = []
    for field_name, field in gqltype.fields.items():
        has_filter = False
        if hasattr(field, '__filter__'):
            if getattr(field, '__filter__'):
                has_filter = True
        elif all_filter:
            has_filter = True

        field_filter_type = None
        if has_filter:
            field_type = get_named_type(field.type)
            if field_type is None:
                raise Exception('Can only filter on Named Types')
            # Deducing Filter type by GraphQL type. Contrary to simple_table_resolver
            if field_type.name == 'String':
                field_filter_type = 'STRING'
            elif field_type.name in ['Int', 'Float']:
                field_filter_type = 'NUMBER'
            elif field_type.name == 'Date':
                field_filter_type = 'DATE'
            elif field_type.name == 'Boolean':
                field_filter_type = 'BOOLEAN'
            else:
                raise GraphQLError(f'Type {field_type.name} cannot support filtering on field {field_name}')

        # Todo: impelement editable
        field_details.append({'field_name': field_name, 'filter_type': field_filter_type, 'editable': False})

    return {'field_details': field_details, 'primary_keys': primary_keys}


def load_from_model_query(model, filters: List[Any], limit: int, offset: int, query_modifiers=None):
    q = select(model)

    for f in filters:
        field = getattr(model, f['field_name'])
        field_type = field.type.python_type
        value = f['value']

        # Deducing filter type by model column type. Contrary to resolve_type_inspector.
        try:
            if field_type is str:
                q = q.where(field.like(value))
            elif field_type in [int, float, decimal.Decimal]:
                q = number_filter_parser(q, field, value)
            elif field_type is date:
                q = date_filter_parser(q, field, value)
            elif field_type is bool:
                q = boolean_filter_parser(q, field, value)
            else:
                raise GraphQLError(f'Cannot filter on column type {field_type}')
        except ParseException as e:
            raise GraphQLError(f'Cannot parse value: {value} for field {field} of type {field_type} [{e}]')

    if query_modifiers is not None:
        q = query_modifiers(q)

    return q.limit(limit).offset(offset)


def resolve_type_loader_factory(type_name_to_model_dict):
    """ Used to inject model_name to model mapping """
    def resolve_type_loader(_, info, type_name, filters: List[Any], limit: int, offset: int):
        gqltype = info.schema.get_type(type_name)
        if gqltype is None:  # Check if Type exists in GQL
            raise GraphQLError(f'Type {type_name} does not exist')
        if not getattr(gqltype, '__db_model__', False):  # Check if GQL type is configured
            raise GraphQLError(f'Type {type_name} is linked to a DB Model')

        model = type_name_to_model_dict.get(type_name)
        if model is None:  # Check if model is found
            raise GraphQLError(f'Type {type_name} is not mapped to a database model')

        q = load_from_model_query(model, filters, limit, offset)
        return get_all_records(info, q)
    return resolve_type_loader


def simple_table_resolver_factory(model, query_modifiers=None):
    def simple_table_resolver(_, info, filters: List[Any], limit: int, offset: int):
        q = load_from_model_query(model, filters, limit, offset, query_modifiers)
        return get_all_records(info, q)
    return simple_table_resolver
