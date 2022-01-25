from inflection import camelize
from jsonclasses.cdef import CDef
from jsonclasses.cgraph import CGraph
from jsonclasses.jfield import JField
from jsonclasses.fdef import (
    FStore, FType, Nullability, ReadRule, Queryability, WriteRule
)
from jsonclasses.modifiers.required_modifier import RequiredModifier
from jsonclasses.modifiers.default_modifier import DefaultModifier
from .codable_class import CodableClassItem, codable_class_item
from .jtype_to_swift_type import jtype_to_swift_type
from ...utils.package_utils import is_field_link, to_list_query, to_single_query


def class_include_items(cdef: CDef) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for field in cdef.fields:
        if is_field_ref(field):
            if field.fdef.ftype == FType.LIST:
                items.append((field.name, to_list_query(field.foreign_cdef)))
            else:
                items.append((field.name, to_single_query(field.foreign_cdef)))
    return items


def list_query_items(cdef: CDef) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for field in cdef.fields:
        if not is_field_queryable(field):
            continue
        name = camelize(field.name)
        type = jtype_to_swift_type(field.fdef, 'Q')
        if is_field_ref(field):
            if not is_field_local_key(field):
                continue
            idname = field_ref_id_name(field)
            items.append((idname, 'IDQuery'))
        else:
            items.append((name, type))
    return items


def is_field_local_key(field: JField) -> bool:
    return field.fdef.fstore == FStore.LOCAL_KEY


def class_update_input_items(cdef: CDef) -> list[CodableClassItem]:
    items: list[CodableClassItem] = []
    for field in cdef.fields:
        if not field_can_update(field):
            continue
        name = camelize(field.name)
        stype = jtype_to_swift_type(field.fdef, 'U', is_field_link(field.fdef))
        local_key = is_field_local_key(field)
        item = codable_class_item('public', 'var', name, stype, True)
        items.append(item)
        if local_key:
            idname = field_ref_id_name(field)
            item = codable_class_item('public', 'var', idname, 'String', True)
            items.append(item)
    return items


def class_create_input_items(cdef: CDef) -> list[CodableClassItem]:
    items: list[CodableClassItem] = []
    for field in cdef.fields:
        if not field_can_create(field):
            continue
        optional = not is_field_required_for_create(field)
        name = camelize(field.name)
        stype = jtype_to_swift_type(field.fdef, 'C', is_field_link(field.fdef))
        local_key = is_field_local_key(field)
        if local_key:
            optional = True
        item = codable_class_item('public', 'var', name, stype, optional)
        items.append(item)
        if local_key:
            idname = field_ref_id_name(field)
            item = codable_class_item('public', 'var', idname, 'String', True)
            items.append(item)
    return items


def is_field_required_for_create(field: JField) -> bool:
    if field_has_default(field):
        return False
    if is_field_nonnull(field):
        return True
    return next((True for v in field.types.modifier.vs if isinstance(v, RequiredModifier)), False)


def field_ref_id_name(field: JField) -> str:
    rkes = field.cdef.jconf.ref_name_strategy
    kes = field.cdef.jconf.input_key_strategy
    return kes(rkes(field))


def field_has_default(field: JField) -> bool:
    if is_field_nonnull(field):
        return True
    return next((True for v in field.types.modifier.vs if isinstance(v, DefaultModifier)), False)


def is_field_nonnull(field: JField) -> bool:
    if field.fdef.ftype == FType.LIST:
        if field.fdef.fstore == FStore.LOCAL_KEY or field.fdef.fstore == FStore.FOREIGN_KEY:
            if field.fdef.collection_nullability == Nullability.NONNULL:
                return True
    return False


def is_field_primary(field: JField) -> bool:
    return field.fdef.primary


def is_field_ref(field: JField) -> bool:
    if field.fdef.fstore == FStore.LOCAL_KEY:
        return True
    if field.fdef.fstore == FStore.FOREIGN_KEY:
        return True
    return False


def is_field_required_for_read(field: JField) -> bool:
    if is_field_nonnull(field):
        return True
    return next((True for v in field.types.modifier.vs if isinstance(v, RequiredModifier)), False)


def is_field_queryable(field: JField) -> bool:
    if field.fdef.read_rule == ReadRule.NO_READ:
        return False
    if field.fdef.fstore == FStore.TEMP:
        return False
    return field.fdef.queryability != Queryability.UNQUERYABLE


def field_can_create(field: JField) -> bool:
    return field.fdef.write_rule != WriteRule.NO_WRITE


def field_can_update(field: JField) -> bool:
    if field.fdef.write_rule == WriteRule.NO_WRITE:
        return False
    if field.fdef.write_rule == WriteRule.WRITE_ONCE:
        if is_field_required_for_create(field):
            return False
    return True


def field_can_read(field: JField) -> bool:
    if field.fdef.read_rule == ReadRule.NO_READ:
        return False
    if field.fdef.fstore == FStore.TEMP:
        return False
    return True


def to_many_request_type(cdef: CDef) -> str:
    return cdef.name + 'ManyRequestType'

def array(val: str) -> str:
    return '[' + val + ']'
