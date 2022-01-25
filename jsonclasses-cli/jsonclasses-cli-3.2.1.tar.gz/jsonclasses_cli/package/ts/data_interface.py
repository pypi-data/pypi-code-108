from inflection import camelize
from jsonclasses.fdef import FType
from jsonclasses.cdef import CDef
from .interface import (
    interface, interface_first_line, interface_include_item, interface_include_key_item, interface_inst_items,
    interface_item, interface_pick_omit_items, interface_type_item, list_query_limit_skip_pn_ps, list_query_order_item)
from .shared_utils import (
    interface_required_include, field_ref_id_name, is_field_local_key, is_field_primary,
    is_field_ref, is_field_required_for_read, field_can_read, field_can_create, is_field_required_for_create,
    field_can_update, is_list_field, is_field_required_null_for_update, list_query_items, string,
    is_field_queryable)
from ...utils.package_utils import (
    to_create_input, to_include, to_include_key, to_list_query, to_result, to_result_picks, to_seek_query, to_single_query,
    to_sort_orders, to_update_input, to_query_data, is_field_link)
from ...utils.join_lines import join_lines
from .jtype_to_ts_type import jtype_to_ts_type


def data_interface(cdef: CDef) -> str:
    return join_lines([
        _interface_result(cdef),
        _interface_create_input(cdef),
        _interface_update_input(cdef),
        _interface_sort_order(cdef),
        _interface_result_pick(cdef),
        _interface_include_keys(cdef),
        _interface_include_type(cdef),
        _interface_single_query(cdef),
        _interface_list_query(cdef),
        _interface_seek_query(cdef),
        _interface_query_data(cdef),
    ], 2)


def _interface_result(cdef: CDef) -> str:
    items: list[str] = []
    for field in cdef.fields:
        if not field_can_read(field):
            continue
        name = camelize(field.name)
        ftype = jtype_to_ts_type(field.fdef, 'R')
        optional = not is_field_required_for_read(field)
        item = interface_item(name, ftype, optional)
        items.append(item)
        local_key = is_field_local_key(field)
        if local_key:
            is_list = '[]' if is_list_field(field) else ''
            idname = field_ref_id_name(field)
            idtype = jtype_to_ts_type(cdef.primary_field.fdef, 'R') + is_list
            item = interface_item(idname, idtype, optional)
            items.append(item)
    name = to_result(cdef)
    return interface(name, items, True)


def _interface_create_input(cdef: CDef) -> str:
    items: list[str] = []
    for field in cdef.fields:
        if not field_can_create(field):
            continue
        optional = not is_field_required_for_create(field)
        name = camelize(field.name)
        ftype = jtype_to_ts_type(field.fdef, 'C', is_field_link(field.fdef))
        optional = not is_field_required_for_read(field)
        item = interface_item(name, ftype, optional)
        items.append(item)
        local_key = is_field_local_key(field)
        if local_key:
            is_list = '[]' if is_list_field(field) else ''
            idname = field_ref_id_name(field)
            idtype = jtype_to_ts_type(cdef.primary_field.fdef, 'C') + is_list
            item = interface_item(idname, idtype, optional)
            items.append(item)
    name = to_create_input(cdef)
    return interface(name, items, True)


def _interface_update_input(cdef: CDef) -> str:
    items: list[str] = []
    for field in cdef.fields:
        if not field_can_update(field):
            continue
        null_for_update = '' if is_field_required_null_for_update(field) else ' | null'
        name = camelize(field.name)
        ftype = jtype_to_ts_type(field.fdef, 'U', is_field_link(field.fdef)) + null_for_update
        item = interface_item(name, ftype, True)
        items.append(item)
        local_key = is_field_local_key(field)
        if local_key:
            is_list = '[]' if is_list_field(field) else ''
            idname = field_ref_id_name(field)
            idtype = jtype_to_ts_type(cdef.primary_field.fdef, 'U') + is_list + null_for_update
            item = interface_item(idname, idtype, True)
            items.append(item)
    name = to_update_input(cdef)
    return interface(name, items, True)


def _interface_sort_order(cdef: CDef) -> str:
    items: list[str] = []
    for field in cdef.fields:
        if not is_field_queryable(field):
            continue
        if is_field_primary(field):
            continue
        if is_field_ref(field):
            continue
        if not field_can_read(field):
            continue
        name = camelize(field.name)
        items.append(string(name))
        items.append(string('-' + name))
    name = to_sort_orders(cdef)
    return interface_type_item(name, items)


def _interface_result_pick(cdef: CDef) -> str:
    items: list[str] = []
    for field in cdef.fields:
        if not field_can_read(field):
            continue
        name = string(camelize(field.name))
        items.append(name)
        if is_field_local_key(field):
            idname = string(field_ref_id_name(field))
            items.append(idname)
    name = to_result_picks(cdef)
    return interface_type_item(name, items)


def _interface_include_keys(cdef: CDef) -> str:
    cname = cdef.name
    keys: list[str] = []
    for field in cdef.fields:
        if is_field_ref(field):
            if field.fdef.ftype == FType.LIST:
                ftype = jtype_to_ts_type(field.fdef, 'R').removesuffix('[]')
                include_type = ftype + 'ListQuery'
            else:
                ftype = jtype_to_ts_type(field.fdef, 'R')
                include_type = ftype + 'SingleQuery'
            name = to_include_key(cname, field.name)
            keys.append(_interface_include_key(name, field.name, include_type))
    return join_lines(keys, 2)


def _interface_include_key(name: str, key: str, ftype: str) -> str:
    return join_lines([
        interface_first_line(name),
        interface_include_key_item(key, ftype),
        '}'
    ])


def _interface_include_type(cdef: CDef) -> str:
    cname = cdef.name
    include = to_include(cdef)
    include_types: list[str] = []
    for field in cdef.fields:
        if is_field_ref(field):
            name = to_include_key(cname, field.name)
            include_types.append(name)
    return interface_type_item(include, include_types) if len(include_types) else ""


def _interface_single_query(cdef: CDef) -> str:
    name = to_single_query(cdef)
    result_pick_name = to_result_picks(cdef)
    return join_lines([
        interface_first_line(name),
        interface_pick_omit_items(result_pick_name),
        _single_query_include(cdef),
        '}'
    ])


def _single_query_include(cdef: CDef) -> str:
    name = to_include(cdef)
    return interface_include_item(name) if interface_required_include(cdef) else ""


def _interface_list_query(cdef: CDef) -> str:
    name = to_list_query(cdef)
    items = list(map(lambda i: interface_item(i[0], i[1], True), list_query_items(cdef)))
    order = to_sort_orders(cdef)
    pick = to_result_picks(cdef)
    return join_lines([
        interface_first_line(name),
        interface_inst_items(items),
        list_query_order_item(order),
        list_query_limit_skip_pn_ps(),
        interface_pick_omit_items(pick),
        _single_query_include(cdef),
        '}'
    ])


def _interface_seek_query(cdef: CDef) -> str:
    name = to_seek_query(cdef)
    items = list(map(lambda i: interface_item(i[0], i[1], True), list_query_items(cdef)))
    return join_lines([
        interface_first_line(name),
        interface_inst_items(items),
        '}'
    ])


def _interface_query_data(cdef: CDef) -> str:
    name = to_query_data(cdef)
    items = [
        interface_item('_query', to_seek_query(cdef), False),
        interface_item('_data', to_update_input(cdef), False)
    ]
    return join_lines([
        interface_first_line(name),
        interface_inst_items(items),
        '}'
    ])
