from inflection import camelize
from jsonclasses.cdef import CDef
from jsonclasses.fdef import FType
from .unary_sort_order import unary_sort_order
from .codable_struct import codable_struct, codable_struct_class, codable_struct_item
from .codable_enum import codable_associated_item, codable_enum, codable_enum_item
from .codable_class import codable_class, codable_class_item
from .jtype_to_swift_type import jtype_to_swift_type
from .shared_utils import (
    class_create_input_items, class_update_input_items, is_field_primary,
    is_field_local_key, field_can_read, field_ref_id_name, is_field_queryable,
    is_field_ref, is_field_required_for_read, array, list_query_items,
    class_include_items, to_many_request_type
)
from ...utils.join_lines import join_lines
from ...utils.package_utils import (
    to_create_input, to_include_key, to_query_data, to_seek_query, to_update_input,
    to_single_query, to_list_query, to_result, to_result_picks, to_include, to_sort_orders
)


def data_class(cdef: CDef) -> str:
    return join_lines([
        _class_create_input(cdef),
        _class_update_input(cdef),
        _class_sort_orders(cdef),
        _class_result_picks(cdef),
        _class_include_key_enums(cdef),
        _class_include_enum(cdef),
        _class_many_request_enum(cdef),
        _class_single_query(cdef),
        _class_seek_query(cdef),
        _class_query_data(cdef),
        _class_list_query(cdef),
        _class_result(cdef),
    ], 2)


def _class_create_input(cdef: CDef) -> str:
    return codable_class(to_create_input(cdef), class_create_input_items(cdef))


def _class_update_input(cdef: CDef) -> str:
    return codable_class(to_update_input(cdef), class_update_input_items(cdef))


def _class_sort_orders(cdef: CDef) -> str:
    fnames: list[str] = []
    for field in cdef.fields:
        if not is_field_queryable(field):
            continue
        if is_field_primary(field):
            continue
        if is_field_ref(field):
            continue
        if not field_can_read(field):
            continue
        fnames.append(camelize(field.name))
    enum_items: list[str] = []
    for name in fnames:
        enum_items.append(codable_enum_item(name, 'String', name))
        desc_name = name + 'Desc'
        enum_items.append(codable_enum_item(desc_name, 'String', "-" + name))
    name = to_sort_orders(cdef)
    enum = codable_enum(name, 'String', enum_items)
    unary = unary_sort_order(name)
    return join_lines([enum, unary], 2)


def _class_result_picks(cdef: CDef) -> str:
    items: list[str] = []
    for field in cdef.fields:
        if not field_can_read(field):
            continue
        name = camelize(field.name)
        items.append(codable_enum_item(name, 'String', name))
        if is_field_local_key(field):
            idname = field_ref_id_name(field)
            items.append(codable_enum_item(idname, 'String', idname))
    return codable_enum(to_result_picks(cdef), 'String', items)


def _class_include_key_enums(cdef: CDef) -> str:
    cname = cdef.name
    enums: list[str] = []
    for field in cdef.fields:
        if is_field_ref(field):
            enums.append(_class_include_key_enum(cname, field.name))
    return join_lines(enums, 2)


def _class_include_key_enum(cname: str, fname: str) -> str:
    return codable_enum(to_include_key(cname, fname), 'Int', [
        codable_enum_item(fname, 'Int', '1')
    ])


def _class_include_enum_init_if(idx: int, key: str, q: str) -> str:
    return f"""
        {'} else ' if idx > 0 else ''}if container.contains(.{key}) {'{'}
            self = .{key}(try! container.decode({q}.self, forKey: .{key}))""".strip('\n')


def _class_include_enum_encode_case(key: str) -> str:
    return f"""
        case .{key}(let value):
            try! container.encode(value, forKey: .{key})""".strip('\n')


def _class_include_enum(cdef: CDef) -> str:
    items = class_include_items(cdef)
    if len(items) == 0:
        return ""
    cases = join_lines(map(lambda i: codable_associated_item(i[0], i[1] + '?'), items), 1)
    coding_keys = join_lines([
        '    enum CodingKeys: String, CodingKey {',
        *map(lambda i: f'        case {i[0]} = "{i[0]}"', items),
        '    }'
    ], 1)
    init = join_lines([
        '    public init(from decoder: Decoder) throws {',
        '        let container = try! decoder.container(keyedBy: CodingKeys.self)',
        join_lines(map(lambda t: _class_include_enum_init_if(t[0], t[1][0], t[1][1]), enumerate(items))),
        '        } else {',
        '            throw NSError()',
        '        }',
        '    }'
    ], 1)
    encode = join_lines([
        '    public func encode(to encoder: Encoder) throws {',
        '        var container = encoder.container(keyedBy: CodingKeys.self)',
        '        switch self {',
        join_lines(map(lambda t: _class_include_enum_encode_case(t[0]), items)),
        '        }',
        '    }'
    ])
    return codable_enum(to_include(cdef), None, [join_lines([
        cases,
        coding_keys,
        init,
        encode
    ], 2)])


def _single_query_items(cdef: CDef) -> list[str]:
    result_picks = array(to_result_picks(cdef))
    result_includes = array(to_include(cdef))
    pick = codable_struct_item(
        'fileprivate', 'var', '_pick', result_picks, True, 'nil')
    omit = codable_struct_item(
        'fileprivate', 'var', '_omit', result_picks, True, 'nil')
    if len(class_include_items(cdef)) == 0:
        includes = ""
    else:
        includes = codable_struct_item(
            'fileprivate', 'var', '_includes', result_includes, True, 'nil')
    return [pick, omit, includes]


def _single_query_picks_omits(cdef: CDef, single: bool = True) -> str:
    rpname = to_result_picks(cdef)
    return f"""
    public static func pick(_ picks: [{rpname}]) -> {to_single_query(cdef) if single else to_list_query(cdef)} {'{'}
        let instance = {to_single_query(cdef) if single else to_list_query(cdef)}()
        instance._pick = picks
        return instance
    {'}'}

    public func pick(_ picks: [{rpname}]) -> {to_single_query(cdef) if single else to_list_query(cdef)} {'{'}
        _pick = picks
        return self
    {'}'}

    public static func omit(_ omits: [{rpname}]) -> {to_single_query(cdef) if single else to_list_query(cdef)} {'{'}
        let instance = {to_single_query(cdef) if single else to_list_query(cdef)}()
        instance._omit = omits
        return instance
    {'}'}

    public func omit(_ omits: [{rpname}]) -> {to_single_query(cdef) if single else to_list_query(cdef)} {'{'}
        _omit = omits
        return self
    {'}'}""".strip('\n')


def _single_query_include(cdef: CDef, key: str, itype: str, qtype: str, single: bool = True) -> str:
    return f"""
    public static func include(_ ref: {itype}, _ query: {qtype}? = nil) -> {to_single_query(cdef) if single else to_list_query(cdef)} {'{'}
        let instance = {to_single_query(cdef) if single else to_list_query(cdef)}()
        instance._includes = [.{key}(query)]
        return instance
    {'}'}

    public func include(_ ref: {itype}, _ query: {qtype}? = nil) -> {to_single_query(cdef) if single else to_list_query(cdef)} {'{'}
        if _includes == nil {'{'} _includes = [] {'}'}
        _includes!.append(.{key}(query))
        return self
    {'}'}""".strip('\n')


def _single_query_includes(cdef: CDef, single: bool = True) -> str:
    items: list[tuple(str, str, str)] = []
    for field in cdef.fields:
        if is_field_ref(field):
            if field.fdef.ftype == FType.LIST:
                items.append((field.name, to_include_key(cdef.name, field.name), to_list_query(field.foreign_cdef)))
            else:
                items.append((field.name, to_include_key(cdef.name, field.name), to_single_query(field.foreign_cdef)))
    return join_lines(map(lambda i: _single_query_include(cdef, i[0], i[1], i[2], single), items), 2)


def _list_query_orders(order: str, cdef: CDef, single: bool = True) -> str:
    return f"""
    public static func order(_ order: {order}) -> {to_single_query(cdef) if single else to_list_query(cdef)} {"{"}
        let instance = {to_single_query(cdef) if single else to_list_query(cdef)}()
        instance._order = [order]
        return instance
    {"}"}

    public static func order(_ orders: [{order}]) -> {to_single_query(cdef) if single else to_list_query(cdef)} {"{"}
        let instance = {to_single_query(cdef) if single else to_list_query(cdef)}()
        instance._order = orders
        return instance
    {"}"}

    public func order(_ order: {order}) -> {to_single_query(cdef) if single else to_list_query(cdef)} {"{"}
        if _order == nil {"{"} _order = [] {"}"}
        _order!.append(order)
        return self
    {"}"}

    public func order(_ orders: [{order}]) -> {to_single_query(cdef) if single else to_list_query(cdef)} {"{"}
        if _order == nil {"{"} _order = [] {"}"}
        _order!.append(contentsOf: orders)
        return self
    {"}"}"""


def _list_query_limit_skip_pn_ps(cdef: CDef) -> str:
    lspp = ["limit", "skip", "pageNo", "pageSize"]
    reslut = []
    for i in lspp:
        reslut.append(f"""
    public static func {i}(_ {i}: Int) -> {to_list_query(cdef)} {"{"}
        let instance = {to_list_query(cdef)}()
        instance._{i} = {i}
        return instance
    {"}"}

    public func {i}(_ {i}: Int) -> {to_list_query(cdef)} {"{"}
        _{i} = {i}
        return self
    {"}"}""".strip('\n'))
    return join_lines(reslut)

def _class_single_query(cdef: CDef) -> str:
    return codable_struct_class(to_single_query(cdef), [join_lines([
        join_lines(_single_query_items(cdef), 1),
        _single_query_picks_omits(cdef, True),
        _single_query_includes(cdef, True)
    ], 2)])


def _list_query_find(cdef: CDef, query_name: str) -> str:
    items = list_query_items(cdef)
    last = len(items) - 1
    arglist = lambda i: f"        {i[1][0]}: {i[1][1]}? = nil{'' if i[0] == last else ','}"
    return join_lines([
        '    public static func `where`(',
        *map(arglist, enumerate(items)),
        f'    ) -> {query_name} {"{"}',
        f'        let instance = {query_name}()',
        *map(lambda i: f"        instance.{i[1][0]} = {i[1][0]}", enumerate(items)),
        '        return instance',
        '    }',
        '\n',
        '    public func `where`(',
        *map(arglist, enumerate(items)),
        f'    ) -> {query_name} {"{"}',
        *map(lambda i: f"        if {i[0]} != nil {'{'} self.{i[0]} = {i[0]} {'}'}", items),
        '        return self',
        '    }'
    ], 1)


def _class_seek_query(cdef: CDef) -> str:
    items = list(map(lambda i: codable_struct_item('public', 'var', i[0], i[1], True, 'nil'), list_query_items(cdef)))
    operators = [
        '\n',
        join_lines([
            _list_query_find(cdef, to_seek_query(cdef))
        ], 2)
    ]
    items.extend(operators)
    return codable_struct_class(to_seek_query(cdef), items)


def _class_query_data(cdef: CDef) -> str:
    items = [
        codable_class_item('fileprivate', 'var', '_query', to_seek_query(cdef), False),
        codable_class_item('fileprivate', 'var', '_data', to_update_input(cdef), False),
    ]
    return codable_class(to_query_data(cdef), items)


def _class_list_query(cdef: CDef) -> str:
    items = list(map(lambda i: codable_struct_item('public', 'var', i[0], i[1], True, 'nil'), list_query_items(cdef)))
    sort_order = to_sort_orders(cdef)
    sort_orders = array(sort_order)
    order = codable_struct_item(
        'fileprivate', 'var', '_order', sort_orders, True, 'nil')
    limit = codable_struct_item(
        'fileprivate', 'var', '_limit', 'Int', True, 'nil')
    skip = codable_struct_item(
        'fileprivate', 'var', '_skip', 'Int', True, 'nil')
    page_no = codable_struct_item(
        'fileprivate', 'var', '_pageNo', 'Int', True, 'nil')
    page_size = codable_struct_item(
        'fileprivate', 'var', '_pageSize', 'Int', True, 'nil')
    operators = [
        order, limit, skip, page_no, page_size, *_single_query_items(cdef),
        '\n',
        join_lines([
            _list_query_find(cdef, to_list_query(cdef)),
            _list_query_orders(sort_order, cdef, False),
            _list_query_limit_skip_pn_ps(cdef),
            _single_query_picks_omits(cdef, False),
            _single_query_includes(cdef, False)
        ], 2)
    ]
    items.extend(operators)
    return codable_struct_class(to_list_query(cdef), items)


def _class_result(cdef: CDef) -> str:
    items: list[str] = []
    for field in cdef.fields:
        if not field_can_read(field):
            continue
        optional = not is_field_required_for_read(field)
        name = camelize(field.name)
        stype = jtype_to_swift_type(field.fdef, 'R')
        local_key = is_field_local_key(field)
        item = codable_class_item('public', 'let', name, stype, optional)
        items.append(item)
        if local_key:
            idname = field_ref_id_name(field)
            item = codable_class_item('public', 'let', idname, 'String', optional)
            items.append(item)
    name = to_result(cdef)
    return codable_class(name, items, True)


def _class_many_request_enum(cdef: CDef) -> str:
    return join_lines([
        f'public enum {to_many_request_type(cdef)}: Codable {"{"}',
        '    case update',
        '    case create',
        '    case upsert',
        '\n',
        f'    func getContent(input: {to_query_data(cdef)}) -> Dictionary<String, {to_query_data(cdef)}> {"{"}',
        '        if self  == .update {',
        '            return ["_update": input]',
        '        }',
        '        else if self == .upsert {',
        '            return ["_upsert": input]',
        '        }',
        f'        return [String: {to_query_data(cdef)}]()',
        '    }',
        '\n',
        f'    func getContent(input: [{to_create_input(cdef)}]) -> Dictionary<String, [{to_create_input(cdef)}]> {"{"}',
        '        if self  == .create {',
        '            return ["_create": input]',
        '        }',
        f'        return [String: [{to_create_input(cdef)}]]()',
        '    }',
        '}',
    ])
