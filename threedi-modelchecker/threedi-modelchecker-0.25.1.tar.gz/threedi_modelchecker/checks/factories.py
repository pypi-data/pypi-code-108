from ..threedi_model import custom_types
from .base import EnumCheck
from .base import ForeignKeyCheck
from .base import GeometryCheck
from .base import GeometryTypeCheck
from .base import NotNullCheck
from .base import TypeCheck
from .base import UniqueCheck
from geoalchemy2.types import Geometry


def get_level(table, column, level_map):
    level = level_map.get(f"*.{column.name}")
    level = level_map.get(f"{table.name}.{column.name}", level)
    return level or "ERROR"


def generate_foreign_key_checks(table, custom_level_map=None, **kwargs):
    custom_level_map = custom_level_map or {}
    foreign_key_checks = []
    for fk_column in table.foreign_keys:
        level = get_level(table, fk_column.parent, custom_level_map)
        foreign_key_checks.append(
            ForeignKeyCheck(
                reference_column=fk_column.column,
                column=fk_column.parent,
                level=level,
                **kwargs,
            )
        )
    return foreign_key_checks


def generate_unique_checks(table, custom_level_map=None, **kwargs):
    custom_level_map = custom_level_map or {}
    unique_checks = []
    for column in table.columns:
        if column.unique or column.primary_key:
            level = get_level(table, column, custom_level_map)
            unique_checks.append(UniqueCheck(column, level=level, **kwargs))
    return unique_checks


def generate_not_null_checks(table, custom_level_map=None, **kwargs):
    custom_level_map = custom_level_map or {}
    not_null_checks = []
    for column in table.columns:
        if not column.nullable:
            level = get_level(table, column, custom_level_map)
            not_null_checks.append(NotNullCheck(column, level=level, **kwargs))
    return not_null_checks


def generate_type_checks(table, custom_level_map=None, **kwargs):
    custom_level_map = custom_level_map or {}
    data_type_checks = []
    for column in table.columns:
        level = get_level(table, column, custom_level_map)
        data_type_checks.append(TypeCheck(column, level=level, **kwargs))
    return data_type_checks


def generate_geometry_checks(table, custom_level_map=None, **kwargs):
    custom_level_map = custom_level_map or {}
    geometry_checks = []
    for column in table.columns:
        if type(column.type) == Geometry:
            level = get_level(table, column, custom_level_map)
            geometry_checks.append(GeometryCheck(column, level=level, **kwargs))
    return geometry_checks


def generate_geometry_type_checks(table, custom_level_map=None, **kwargs):
    custom_level_map = custom_level_map or {}
    geometry_type_checks = []
    for column in table.columns:
        if type(column.type) == Geometry:
            level = get_level(table, column, custom_level_map)
            geometry_type_checks.append(
                GeometryTypeCheck(column, level=level, **kwargs)
            )
    return geometry_type_checks


def generate_enum_checks(table, custom_level_map=None, **kwargs):
    custom_level_map = custom_level_map or {}
    enum_checks = []
    for column in table.columns:
        if issubclass(type(column.type), custom_types.CustomEnum):
            level = get_level(table, column, custom_level_map)
            enum_checks.append(EnumCheck(column, level=level, **kwargs))
    return enum_checks
