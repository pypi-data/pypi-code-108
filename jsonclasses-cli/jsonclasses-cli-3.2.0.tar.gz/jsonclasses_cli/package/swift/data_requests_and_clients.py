from typing import cast
from inflection import camelize, pluralize
from jsonclasses.cdef import CDef
from jsonclasses_server.aconf import AConf
from .codable_class import CodableClassItem
from .shared_utils import class_create_input_items, class_include_items, class_update_input_items, list_query_items, to_many_request_type
from ...utils.join_lines import join_lines
from ...utils.package_utils import (
    class_needs_api, class_needs_session, to_client, to_create_input, to_create_many_request, to_create_request, to_delete_many_request, to_delete_request,
    to_id_request, to_include_key, to_list_query, to_list_request, to_list_result, to_query_data, to_result_picks, to_seek_query, to_session, to_session_input, to_sign_in_request, to_single_query,
    to_update_input, to_result, to_update_many_request, to_update_request, to_sort_orders, to_upsert_request
)


def data_client_instances(cdef: CDef) -> str:
    if not class_needs_api(cdef):
        return ''
    var_name = camelize(pluralize(cdef.name))
    return f'public var {var_name} = {to_client(cdef)}()'


def data_requests_and_clients(cdef: CDef) -> str:
    if not class_needs_api(cdef):
        return ''
    aconf = cast(AConf, cdef.cls.aconf)
    return join_lines([
        _data_create_request(cdef, aconf.name) if 'C' in aconf.actions else '',
        _data_update_request(cdef, aconf.name) if 'U' in aconf.actions else '',
        _data_delete_request(cdef, aconf.name) if 'D' in aconf.actions else '',
        _data_id_request(cdef, aconf.name) if 'R' in aconf.actions else '',
        _data_upsert_request(cdef, aconf.name) if all(element in aconf.actions for element in ['C','U']) else '',
        _data_create_many_request(cdef, aconf.name) if 'C' in aconf.actions else '',
        _data_update_many_request(cdef, aconf.name) if 'U' in aconf.actions else '',
        _data_delete_many_request(cdef, aconf.name) if 'D' in aconf.actions else '',
        _data_find_request(cdef, aconf.name) if 'L' in aconf.actions else '',
        _data_sign_in_request(cdef, aconf.name) if class_needs_session(cdef) else '',
        _data_client(cdef, aconf)
    ], 2)


def _data_find_request_nums(cdef: CDef, method_name: str) -> str:
    return f"""
    public func {method_name}(_ {method_name}: Int) -> {to_list_request(cdef)} {'{'}
        if query == nil {'{'} query = {to_list_query(cdef)}() {'}'}
        query = query!.{method_name}({method_name})
        return self
    {'}'}

    public func {method_name}(_ {method_name}: Int) async throws -> [{to_result(cdef)}] {'{'}
        return try await self.{method_name}({method_name}).exec()
    {'}'}""".strip('\n')


def _data_find_request_method(cdef: CDef) -> str:
    return f"""
    public func order(_ order: {to_sort_orders(cdef)}) -> {to_list_request(cdef)} {'{'}
        if query == nil {'{'} query = {to_list_query(cdef)}() {'}'}
        query = query!.order(order)
        return self
    {'}'}

    public func order(_ orders: [{to_sort_orders(cdef)}]) -> {to_list_request(cdef)} {'{'}
        if query == nil {'{'} query = {to_list_query(cdef)}() {'}'}
        query = query!.order(orders)
        return self
    {'}'}

    public func order(_ order: {to_sort_orders(cdef)}) async throws -> [{to_result(cdef)}] {'{'}
        return try await self.order(order).exec()
    {'}'}

    public func order(_ orders: [{to_sort_orders(cdef)}]) async throws -> [{to_result(cdef)}] {'{'}
        return try await self.order(orders).exec()
    {'}'}

{join_lines(map(lambda n: _data_find_request_nums(cdef, n), ['skip', 'limit', 'pageSize', 'pageNo']), 2)}
""".strip('\n')


def _data_query_request_common(
    cdef: CDef,
    single: bool = True,
    is_create_many: bool = False,
    is_sign_in: bool = False) -> str:
    return join_lines([f"""
    public func pick(_ picks: [{to_result_picks(cdef)}]) -> Self {'{'}
        if query == nil {'{'} query = {to_single_query(cdef) if single or is_create_many else to_list_query(cdef)}() {'}'}
        query = query!.pick(picks)
        return self
    {'}'}

    public func pick(_ picks: [{to_result_picks(cdef)}]) async throws -> {to_session(cdef, 'swift') if is_sign_in else to_result(cdef) if single else to_list_result(cdef)} {'{'}
        return try await self.pick(picks).exec()
    {'}'}

    public func omit(_ omits: [{to_result_picks(cdef)}]) -> Self {'{'}
        if query == nil {'{'} query = {to_single_query(cdef) if single or is_create_many else to_list_query(cdef)}() {'}'}
        query = query!.omit(omits)
        return self
    {'}'}

    public func omit(_ omits: [{to_result_picks(cdef)}]) async throws -> {to_session(cdef, 'swift') if is_sign_in else to_result(cdef) if single else to_list_result(cdef)} {'{'}
        return try await self.omit(omits).exec()
    {'}'}""".strip('\n'), _data_query_request_includes(cdef, single, is_create_many, is_sign_in)], 2)


def _data_query_request_include(cdef: CDef, item: tuple[str, str], single: bool = True, is_create_many: bool = False, is_sign_in: bool = False) -> str:
    return f"""
    public func include(_ ref: {to_include_key(cdef.name, item[0])}, _ query: {item[1]}? = nil) -> Self {'{'}
        if self.query == nil {'{'} self.query = {to_single_query(cdef) if single or is_create_many else to_list_query(cdef)}() {'}'}
        self.query = self.query!.include(ref, query)
        return self
    {'}'}

    public func include(_ ref: {to_include_key(cdef.name, item[0])}, _ query: {item[1]}? = nil) async throws -> {to_session(cdef, 'swift') if is_sign_in else to_result(cdef) if single else to_list_result(cdef)} {'{'}
        if self.query == nil {'{'} self.query = {to_single_query(cdef) if single or is_create_many else to_list_query(cdef)}() {'}'}
        self.query = self.query!.include(ref, query)
        return try await self.exec()
    {'}'}
    """.strip('\n')


def _data_query_request_includes(cdef: CDef, single: bool = True, is_create_many: bool = False, is_sign_in: bool = False) -> str:
    items = class_include_items(cdef)
    if len(items) == 0:
        return ''
    return join_lines(map(lambda i: _data_query_request_include(cdef, i, single, is_create_many, is_sign_in), items), 2)


def _data_create_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_create_request(cdef)} {'{'}",
        f"    internal var input: {to_create_input(cdef)}",
        f"    internal var query: {to_single_query(cdef)}?",
        '\n',
        f"    internal init(input: {to_create_input(cdef)}, query: {to_single_query(cdef)}? = nil) {'{'}",
        '        self.input = input',
        '        self.query = query'
        '    }',
        '\n',
        f"    internal func exec() async throws -> {to_result(cdef)} {'{'}",
        f"        return try await RequestManager.shared.post(",
        f'            url: "/{name}", input: input, query: query',
        f"        )",
        "    }",
        '\n',
        _data_query_request_common(cdef),
        '}'
    ], 1)


def _data_update_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_update_request(cdef)} {'{'}",
        "    internal var id: String",
        f"    internal var input: {to_update_input(cdef)}",
        f"    internal var query: {to_single_query(cdef)}?",
        '\n',
        f"    internal init(id: String, input: {to_update_input(cdef)}, query: {to_single_query(cdef)}? = nil) {'{'}",
        '        self.id = id',
        '        self.input = input',
        '        self.query = query'
        '    }',
        '\n',
        f"    internal func exec() async throws -> {to_result(cdef)} {'{'}",
        f"        return try await RequestManager.shared.patch(",
        f'            url: "/{name}/\(id)", input: input, query: query',
        f"        )",
        "    }",
        '\n',
        _data_query_request_common(cdef),
        '}'
    ], 1)


def _data_delete_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_delete_request(cdef)} {'{'}",
        "    internal var id: String",
        "\n",
        "    internal init(id: String) {",
        '        self.id = id',
        '    }',
        "\n",
        "    internal func exec() async throws {",
        "        return try await RequestManager.shared.delete(",
        f'            url: "/{name}/\(id)"',
        "        )",
        "    }",
        "}"
    ], 1)


def _data_id_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_id_request(cdef)} {'{'}",
        "    internal var id: String",
        f"    internal var query: {to_single_query(cdef)}?",
        '\n',
        f"    internal init(id: String, query: {to_single_query(cdef)}? = nil) {'{'}",
        '        self.id = id',
        '        self.query = query',
        '    }',
        '\n',
        f"    internal func exec() async throws -> {to_result(cdef)} {'{'}",
        f"        return try await RequestManager.shared.get(",
        f'            url: "/{name}/\(id)", query: query',
        f"        )!",
        "    }",
        '\n',
        _data_query_request_common(cdef),
        '}'
    ], 1)


def _data_upsert_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_upsert_request(cdef)} {'{'}",
        f"    internal var input: {to_query_data(cdef)}",
        f"    internal var query: {to_seek_query(cdef)}?",
        '\n',
        f"    internal init(input: {to_query_data(cdef)}, query: {to_seek_query(cdef)}? = nil) {'{'}",
        '        self.input = input',
        '        self.query = query',
        '    }',
        '\n',
        f"    internal func exec() async throws -> {to_result(cdef)} {'{'}",
        f"        return try await RequestManager.shared.post(",
        f'            url: "/{name}",',
        f'            input: {to_many_request_type(cdef)}.upsert.getContent(input: self.input),',
        "            query: self.query",
        "        )",
        "    }",
        '}'
    ], 1)


def _data_create_many_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_create_many_request(cdef)} {'{'}",
        f"    internal var input: [{to_create_input(cdef)}]",
        f"    internal var query: {to_single_query(cdef)}?",
        '\n',
        f"    internal init(input: [{to_create_input(cdef)}], query: {to_single_query(cdef)}? = nil) {'{'}",
        '        self.input = input',
        '        self.query = query'
        '    }',
        '\n',
        f"    internal func exec() async throws -> [{to_result(cdef)}] {'{'}",
        f"        return try await RequestManager.shared.post(",
        f'            url: "/{name}", input: {to_many_request_type(cdef)}.create.getContent(input: self.input), query: query',
        f"        )",
        "    }",
        '\n',
        _data_query_request_common(cdef, False, True),
        '}'
    ], 1)


def _data_update_many_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_update_many_request(cdef)} {'{'}",
        f"    internal var input: {to_query_data(cdef)}",
        f"    internal var query: {to_seek_query(cdef)}?",
        '\n',
        f"    internal init(input: {to_query_data(cdef)}, query: {to_seek_query(cdef)}? = nil) {'{'}",
        '        self.input = input',
        '        self.query = query',
        '    }',
        '\n',
        f"    internal func exec() async throws -> [{to_result(cdef)}] {'{'}",
        f"        return try await RequestManager.shared.patch(",
        f'            url: "/{name}", input: {to_many_request_type(cdef)}.update.getContent(input: self.input), query: self.query',
        f"        )",
        "    }",
        '}'
    ], 1)


def _data_delete_many_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_delete_many_request(cdef)} {'{'}",
        f"    internal var query: {to_seek_query(cdef)}?",
        "\n",
        f"    internal init(query: {to_seek_query(cdef)}? = nil) {'{'}",
        '        self.query = query',
        '    }',
        "\n",
        "    internal func exec() async throws {",
        "        return try await RequestManager.shared.delete(",
        f'            url: "/{name}",',
        '            query: self.query',
        "        )",
        "    }",
        "}"
    ], 1)


def _data_find_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_list_request(cdef)} {'{'}",
        f"    internal var query: {to_list_query(cdef)}?",
        '\n',
        f"    internal init(query: {to_list_query(cdef)}? = nil) {'{'}",
        '        self.query = query',
        '    }',
        '\n',
        f"    internal func exec() async throws -> [{to_result(cdef)}] {'{'}",
        f"        return try await RequestManager.shared.get(",
        f'            url: "/{name}", query: query',
        f"        )!",
        "    }",
        '\n',
        _data_find_request_method(cdef),
        _data_query_request_common(cdef, False),
        '}'
    ], 1)


def _data_sign_in_request(cdef: CDef, name: str) -> str:
    return join_lines([
        f"public class {to_sign_in_request(cdef)} {'{'}",
        f"    internal var input: {to_session_input(cdef)}",
        f"    internal var query: {to_single_query(cdef)}?",
        '\n',
        f"    internal init(input: {to_session_input(cdef)}, query: {to_single_query(cdef)}? = nil) {'{'}",
        '        self.input = input',
        '        self.query = query',
        '    }',
        '\n',
        f"    internal func exec() async throws -> {to_session(cdef, 'swift')} {'{'}",
        f"        SessionManager.shared.session = try await RequestManager.shared.post(",
        f'            url: "/{name}/session", input: input, query: query',
        "        )",
        "        return SessionManager.shared.session!",
        "    }",
        '\n',
        _data_query_request_common(cdef, is_sign_in=True),
        '}'
    ], 1)


def _data_client(cdef: CDef, aconf: AConf) -> str:
    return join_lines([
        f'public struct {to_client(cdef)} {"{"}',
        '\n',
        '    fileprivate init() { }',
        '\n',
        join_lines([
            _data_client_creates(cdef, aconf),
            _data_client_updates(cdef, aconf),
            _data_client_delete(cdef, aconf),
            _data_client_ids(cdef, aconf),
            _data_client_finds(cdef, aconf),
            _data_client_upsert(cdef, aconf),
            _data_client_create_many(cdef, aconf),
            _data_client_update_many(cdef, aconf),
            _data_client_delete_many(cdef, aconf),
            _data_client_sign_in(cdef),
        ], 2),
        '}'
    ], 1)


def _data_client_create_2(cdef: CDef, items: list[CodableClassItem]) -> str:
    if len(items) == 0:
        return join_lines([
            f'    public func create() -> {to_create_request(cdef)} {"{"}',
            f'        let input = {to_create_input(cdef)}()',
            '        return create(input)',
            '    }'
        ], 1)
    last = len(items) - 1
    return join_lines([
        f'    public func create(',
        *map(lambda i: f"        {i[1][2]}: {i[1][3]}{'? = nil' if i[1][4] else ''}{'' if i[0] == last else ', '}", enumerate(items)),
        f'    ) -> {to_create_request(cdef)} {"{"}',
        f'        let input = {to_create_input(cdef)}(',
        *map(lambda i: f"            {i[1][2]}: {i[1][2]}{'' if i[0] == last else ','}", enumerate(items)),
        '        )',
        '        return create(input)',
        '    }'
    ], 1)


def _data_client_create_4(cdef: CDef, items: list[CodableClassItem]) -> str:
    if len(items) == 0:
        return join_lines([
            f'    public func create() async throws -> {to_result(cdef)} {"{"}',
            f'        let request: {to_create_request(cdef)} = self.create()',
            '        return try await request.exec()',
            '    }'
        ], 1)
    last = len(items) - 1
    return join_lines([
        f'    public func create(',
        *map(lambda i: f"        {i[1][2]}: {i[1][3]}{'? = nil' if i[1][4] else ''}{'' if i[0] == last else ', '}", enumerate(items)),
        f'    ) async throws -> {to_result(cdef)} {"{"}',
        f'        let request: {to_create_request(cdef)} = self.create(',
        *map(lambda i: f"            {i[1][2]}: {i[1][2]}{'' if i[0] == last else ','}", enumerate(items)),
        '        )',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_creates(cdef: CDef, aconf: AConf) -> str:
    if 'C' not in aconf.actions:
        return ''
    input_items = class_create_input_items(cdef)
    return join_lines([
        f'    public func create(_ input: {to_create_input(cdef)}) -> {to_create_request(cdef)} {"{"}',
        f'        return {to_create_request(cdef)}(input: input)',
        '    }',
        '\n',
        _data_client_create_2(cdef, input_items),
        '\n',
        f'    public func create(_ input: {to_create_input(cdef)}) async throws -> {to_result(cdef)} {"{"}',
        f'        let request: {to_create_request(cdef)} = self.create(input)',
        '        return try await request.exec()',
        '    }',
        '\n',
        _data_client_create_4(cdef, input_items)
    ], 1)


def _data_client_update_2(cdef: CDef, items: list[CodableClassItem]) -> str:
    if len(items) == 0:
        return join_lines([
            f'    public func update(_ id: String) -> {to_update_request(cdef)} {"{"}',
            f'        let input = {to_update_input(cdef)}()',
            '        return update(id, input)',
            '    }'
        ], 1)
    last = len(items) - 1
    return join_lines([
        f'    public func update(',
        '        _ id: String,',
        *map(lambda i: f"        {i[1][2]}: {i[1][3]}{'? = nil' if i[1][4] else ''}{'' if i[0] == last else ', '}", enumerate(items)),
        f'    ) -> {to_update_request(cdef)} {"{"}',
        f'        let input = {to_update_input(cdef)}(',
        *map(lambda i: f"            {i[1][2]}: {i[1][2]}{'' if i[0] == last else ','}", enumerate(items)),
        '        )',
        '        return update(id, input)',
        '    }'
    ], 1)


def _data_client_update_4(cdef: CDef, items: list[CodableClassItem]) -> str:
    if len(items) == 0:
        return join_lines([
            f'    public func update(_ id: String) async throws -> {to_result(cdef)} {"{"}',
            f'        let request: {to_update_request(cdef)} = self.update(id)',
            '        return try await request.exec()',
            '    }'
        ], 1)
    last = len(items) - 1
    return join_lines([
        f'    public func update(',
        '        _ id: String,',
        *map(lambda i: f"        {i[1][2]}: {i[1][3]}{'? = nil' if i[1][4] else ''}{'' if i[0] == last else ', '}", enumerate(items)),
        f'    ) async throws -> {to_result(cdef)} {"{"}',
        f'        let request: {to_update_request(cdef)} = self.update(',
        '            id,',
        *map(lambda i: f"            {i[1][2]}: {i[1][2]}{'' if i[0] == last else ','}", enumerate(items)),
        '        )',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_updates(cdef: CDef, aconf: AConf) -> str:
    if 'U' not in aconf.actions:
        return ''
    input_items = class_update_input_items(cdef)
    return join_lines([
        f'    public func update(_ id: String, _ input: {to_update_input(cdef)}) -> {to_update_request(cdef)} {"{"}',
        f'        return {to_update_request(cdef)}(id: id, input: input)',
        '    }',
        '\n',
        _data_client_update_2(cdef, input_items),
        '\n',
        f'    public func update(_ id: String, _ input: {to_update_input(cdef)}) async throws -> {to_result(cdef)} {"{"}',
        f'        let request: {to_update_request(cdef)} = self.update(id, input)',
        '        return try await request.exec()',
        '    }',
        '\n',
        _data_client_update_4(cdef, input_items)
    ], 1)


def _data_client_delete(cdef: CDef, aconf: AConf) -> str:
    if 'D' not in aconf.actions:
        return ''
    return join_lines([
        '    public func delete(_ id: String) async throws {',
        f'        let request = {to_delete_request(cdef)}(id: id)',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_ids(cdef: CDef, aconf: AConf) -> str:
    if 'R' not in aconf.actions:
        return ''
    return join_lines([
        f'    public func id(_ id: String) -> {to_id_request(cdef)} {"{"}',
        f'        return {to_id_request(cdef)}(id: id)',
        '    }',
        f'    public func id(_ id: String) async throws -> {to_result(cdef)} {"{"}',
        f'        let request = {to_id_request(cdef)}(id: id)',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_find_2(cdef: CDef, items: list[tuple[str, str]]) -> str:
    last = len(items) - 1
    return join_lines([
        '    public func find(',
        *map(lambda i: f"        {i[1][0]}: {i[1][1]}? = nil{'' if i[0] == last else ','}", enumerate(items)),
        f'    ) -> {to_list_request(cdef)} {"{"}',
        f'        let query = {to_list_query(cdef)}()',
        *map(lambda i: f"        query.{i[0]} = {i[0]}", items),
        f'        return {to_list_request(cdef)}(query: query)',
        '    }'
    ], 1)


def _data_client_find_4(cdef: CDef, items: list[tuple[str, str]]) -> str:
    last = len(items) - 1
    return join_lines([
        '    public func find(',
        *map(lambda i: f"        {i[1][0]}: {i[1][1]}? = nil{'' if i[0] == last else ','}", enumerate(items)),
        f'    ) async throws -> {to_list_result(cdef)} {"{"}',
        f'        let query = {to_list_query(cdef)}()',
        *map(lambda i: f"        query.{i[0]} = {i[0]}", items),
        f'        let request = {to_list_request(cdef)}(query: query)',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_finds(cdef: CDef, aconf: AConf) -> str:
    if 'L' not in aconf.actions:
        return ''
    query_items = list_query_items(cdef)
    return join_lines([
        f'    public func find(_ query: {to_list_query(cdef)}? = nil) -> {to_list_request(cdef)} {"{"}',
        f'        return {to_list_request(cdef)}(query: query)',
        '    }',
        '\n',
        _data_client_find_2(cdef, query_items),
        '\n',
        f'    public func find(_ query: {to_list_query(cdef)}? = nil) async throws -> {to_list_result(cdef)} {"{"}',
        f'        let request = {to_list_request(cdef)}(query: query)',
        '        return try await request.exec()',
        '    }',
        '\n',
        _data_client_find_4(cdef, query_items)
    ], 1)


def _data_client_upsert(cdef: CDef, aconf: AConf) -> str:
    if not all( element in aconf.actions for element in ['C','U']):
        return ''
    return join_lines([
        f'    public func upsert(query: {to_seek_query(cdef)}, data: {to_update_input(cdef)}) async throws -> {to_result(cdef)} {"{"}',
        f'        let input = {to_query_data(cdef)}(_query: query, _data: data)',
        f'        let request = {to_upsert_request(cdef)}(input: input)',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_create_many(cdef: CDef, aconf: AConf) -> str:
    if 'C' not in aconf.actions:
        return ''
    return join_lines([
        f'    public func createMany(input: [{to_create_input(cdef)}], query: {to_single_query(cdef)}? = nil) -> {to_create_many_request(cdef)} {"{"}',
        f'        return {to_create_many_request(cdef)}(input: input, query: query)',
        '    }',
        '\n',
        f'    public func createMany(input: [{to_create_input(cdef)}], query: {to_single_query(cdef)}? = nil) async throws -> [{to_result(cdef)}] {"{"}',
        f'        let request = {to_create_many_request(cdef)}(input: input, query: query)',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_update_many(cdef: CDef, aconf: AConf) -> str:
    if 'U' not in aconf.actions:
        return ''
    return join_lines([
        f'    public func updateMany(query: {to_seek_query(cdef)}, data: {to_update_input(cdef)}) async throws -> [{to_result(cdef)}] {"{"}',
        f'        let input = {to_query_data(cdef)}(_query: query, _data: data)',
        f'        let request = {to_update_many_request(cdef)}(input: input)',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_delete_many(cdef: CDef, aconf: AConf) -> str:
    if 'D' not in aconf.actions:
        return ''
    return join_lines([
        f'    public func delete(_ query: {to_seek_query(cdef)}? = nil) async throws {"{"}',
        f'        let request = {to_delete_many_request(cdef)}(query: query)',
        '        return try await request.exec()',
        '    }'
    ], 1)


def _data_client_sign_in(cdef: CDef) -> str:
    if not class_needs_session(cdef):
        return ''
    return join_lines([
        f'    public func signIn(input: {to_session_input(cdef)}, query: {to_single_query(cdef)}? = nil) async throws -> {to_session(cdef, "swift")} {"{"}',
        f'        let request = {to_sign_in_request(cdef)}(input: input, query: query)',
        '        return try await request.exec()',
        '    }'
    ], 1)
