from typing import cast
from jsonclasses.cdef import CDef
from .sign_in_request import sign_in_request
from jsonclasses_server.aconf import AConf
from .shared_utils import interface_required_include
from ...utils.join_lines import join_lines
from ...utils.package_utils import (
    class_needs_api, class_needs_session, to_client, to_create_input, to_create_request, to_delete_request, to_id_request,
    to_list_query, to_list_request, to_query_data, to_result, to_result_picks, to_seek_query, to_session, to_session_input,
    to_sign_in_request, to_single_query, to_update_input, to_update_request, to_sort_orders, to_include, to_upsert_request,
    to_create_many_request, to_update_many_request, to_delete_many_request
)


def data_requests_and_clients(cdef: CDef) -> str:
    if not class_needs_api(cdef):
        return ''
    aconf = cast(AConf, cdef.cls.aconf)
    return join_lines([
        _data_create_requet(cdef, aconf.name) if 'C' in aconf.actions else '',
        _data_update_request(cdef, aconf.name) if 'U' in aconf.actions else '',
        _data_delete_request(cdef, aconf.name) if 'D' in aconf.actions else '',
        _data_id_request(cdef, aconf.name) if 'R' in aconf.actions else '',
        _data_upsert_request(cdef, aconf.name) if all(element in aconf.actions for element in ['C','U']) else '',
        _data_create_many_request(cdef, aconf.name) if 'C' in aconf.actions else '',
        _data_update_many_request(cdef, aconf.name) if 'U' in aconf.actions else '',
        _data_delete_many_request(cdef, aconf.name) if 'D' in aconf.actions else '',
        _data_list_request(cdef, aconf.name) if 'L' in aconf.actions else '',
        sign_in_request(cdef),
        _data_client(cdef, aconf)
    ], 2)


def _data_query_request_common(cdef: CDef, request: str) -> str:
    return f"""
    pick(picks: {to_result_picks(cdef)}[]): {request}<Pick<T, typeof picks[number]>> {'{'}
        this.#query = {'{'}...this.#query, _pick: picks{'}'}
        return this
    {'}'}

    omit(omits: {to_result_picks(cdef)}[]): {request}<Omit<T, typeof omits[number]>> {'{'}
        this.#query = {'{'}...this.#query, _omit: omits{'}'}
        return this
    {'}'}
    """.strip() + "\n"


def _data_query_request_includes(cdef: CDef, request: str) -> str:
    if interface_required_include(cdef):
        return f"""
    include(includes: {to_include(cdef)}[]): {request}<T> {'{'}
        this.#query = {'{'}...this.#query, _includes: includes {'}'}
        return this
    {'}'}
        """.strip() + "\n"

    return ''


def _data_create_requet(cdef:CDef, name:str) -> str:
    return f"""
class {to_create_request(cdef)}<T extends Partial<{to_result(cdef)}>> extends Promise<T> {'{'}

    #input: {to_create_input(cdef)}
    #query?: {to_single_query(cdef)}

    constructor(input: {to_create_input(cdef)}, query?:{to_single_query(cdef)}){'{'}
        super(() => {'{'}{'}'})
        this.#input = input
        this.#query = query
    {'}'}

    {_data_query_request_common(cdef,to_create_request(cdef))}
    {_data_query_request_includes(cdef, to_create_request(cdef))}
    async exec(): Promise<T> {'{'}
        return await RequestManager.share.post('/{name}', this.#input, this.#query)
    {'}'}
{'}'}
    """.strip() + "\n"


def _data_upsert_request(cdef:CDef, name:str) -> str:
    return  f"""
class {to_upsert_request(cdef)}<T extends Partial<{to_result(cdef)}>> extends Promise<T> {'{'}

    #input: {to_query_data(cdef)}

    constructor(input: {to_query_data(cdef)}){'{'}
        super(() => {'{'}{'}'})
        this.#input = input
    {'}'}

    async exec(): Promise<T> {'{'}
        return await RequestManager.share.post('/{name}', {'{'} '_upsert': this.#input {'}'})
    {'}'}
{'}'}
    """


def _data_create_many_request(cdef: CDef, name:str) -> str:
    return f"""
class {to_create_many_request(cdef)}<T extends Partial<{to_result(cdef)}>> extends Promise<T> {'{'}

    #input: {to_create_input(cdef)}[]
    #query?: {to_single_query(cdef)}

     constructor(input: {to_create_input(cdef)}[], query?:{to_single_query(cdef)}){'{'}
        super(() => {'{'}{'}'})
        this.#input = input
        this.#query = query
    {'}'}

    {_data_query_request_common(cdef, to_create_many_request(cdef))}
    {_data_query_request_includes(cdef, to_create_many_request(cdef))}
    async exec(): Promise<T[]> {'{'}
        return await RequestManager.share.post('/{name}', {'{'} '_create': this.#input {'}'})
    {'}'}
{'}'}
    """


def _data_update_many_request(cdef:CDef, name:str) -> str:
    return f"""
class {to_update_many_request(cdef)}<T extends Partial<{to_result(cdef)}>> extends Promise<T> {'{'}

    #input: {to_query_data(cdef)}
    #query?: {to_single_query(cdef)}

    constructor(input: {to_query_data(cdef)}, query?:{to_single_query(cdef)}) {'{'}
        super(() => {'{'}{'}'})
        this.#input = input
        this.#query = query
    {'}'}

    {_data_query_request_common(cdef, to_update_many_request(cdef))}
    {_data_query_request_includes(cdef, to_update_many_request(cdef))}
    async exec(): Promise<{to_result(cdef)}> {'{'}
        return await RequestManager.share.patch('/{name}', {'{'} '_update': this.#input {'}'})
    {'}'}
{'}'}
    """


def _data_update_request(cdef:CDef, name:str) -> str:
    return f"""
class {to_update_request(cdef)}<T extends Partial<{to_result(cdef)}>> extends Promise<T> {'{'}

    #id: string
    #input: {to_update_input(cdef)}
    #query?: {to_single_query(cdef)}

    constructor(id:string, input: {to_update_input(cdef)}, query?: {to_single_query(cdef)},) {'{'}
        super(() => {'{'}{'}'})
        this.#id = id
        this.#input = input
        this.#query = query
    {'}'}

    {_data_query_request_common(cdef, to_update_request(cdef))}
    {_data_query_request_includes(cdef, to_update_request(cdef))}
    async exec(): Promise<{to_result(cdef)}> {'{'}
        return await RequestManager.share.patch(`/{name}/${'{'}this.#id{'}'}`, this.#input, this.#query)
    {'}'}
{'}'}
""".strip() + "\n"


def _data_delete_request(cdef:CDef, name:str) -> str:
    return f"""
class {to_delete_request(cdef)} extends Promise<void> {'{'}

    #id: string

    constructor(id: string) {'{'}
        super(() => {'{'}{'}'})
        this.#id = id
    {'}'}
    async exec(): Promise<void> {'{'}
        return await RequestManager.share.delete(`/{name}/${'{'}this.#id{'}'}`)
    {'}'}
{'}'}
""".strip() + "\n"


def _data_delete_many_request(cdef:CDef, name:str) -> str:
    return f"""
class {to_delete_many_request(cdef)} extends Promise<void> {'{'}

    #query?: {to_seek_query(cdef)}

    constructor(query?: {to_seek_query(cdef)}) {'{'}
        super(() => {'{'}{'}'})
        this.#query = query
    {'}'}

    async exec(): Promise<void> {'{'}
        return await RequestManager.share.delete('/{name}', this.#query)
    {'}'}
{'}'}
    """


def _data_id_request(cdef:CDef, name:str) -> str:
    return f"""
class {to_id_request(cdef)}<T extends Partial<{to_result(cdef)}>> extends Promise<T> {'{'}

    #id: string
    #query?: {to_single_query(cdef)}

    constructor(id: string, query?: {to_single_query(cdef)}) {'{'}
        super(() => {'{'}{'}'})
        this.#id = id,
        this.#query = query
    {'}'}

    {_data_query_request_common(cdef, to_id_request(cdef))}
    { _data_query_request_includes(cdef, to_id_request(cdef))}
    async exec(): Promise<{to_result(cdef)}> {'{'}
        return await RequestManager.share.get(`/{name}/${'{'}this.#id{'}'}`, this.#query)
    {'}'}
{'}'}
""".strip() + "\n"


def _data_list_request(cdef:CDef, name:str) -> str:
    return f"""
class {to_list_request(cdef)}<T extends Partial<{to_result(cdef)}>> extends Promise<T[]> {'{'}

    #query?: {to_list_query(cdef)}

    constructor(query?: {to_list_query(cdef)}) {'{'}
        super(() => {'{'}{'}'})
        this.#query = query
    {'}'}

    order(order: {to_sort_orders(cdef)} | {to_sort_orders(cdef)}[]): {to_list_request(cdef)}<T> {'{'}
        this.#query = {'{'}...this.#query, _order: order{'}'}
        return this
    {'}'}

    skip(skip: number): {to_list_request(cdef)}<T> {'{'}
        this.#query = {'{'}...this.#query, _skip: skip{'}'}
        return this
    {'}'}

    limt(limit: number): {to_list_request(cdef)}<T> {'{'}
        this.#query = {'{'}...this.#query, _limit:limit{'}'}
        return this
    {'}'}

    pageSize(pageSize: number): {to_list_request(cdef)}<T> {'{'}
        this.#query = {'{'}...this.#query, _pageSize: pageSize{'}'}
        return this
    {'}'}

    pageNo(pageNo: number): {to_list_request(cdef)}<T> {'{'}
        this.#query = {'{'}...this.#query, _pageNo: pageNo{'}'}
        return this
    {'}'}

    {_data_query_request_common(cdef, to_list_request(cdef))}
    {_data_query_request_includes(cdef, to_list_request(cdef))}
    async exec(): Promise<{to_result(cdef)}[]> {'{'}
        return await RequestManager.share.get('/{name}',this.#query)
    {'}'}
{'}'}
""".strip() + "\n"


def _data_client(cdef: CDef, aconf: AConf) -> str:
    return join_lines([
        f'class {to_client(cdef)} {"{"}',
        _data_client_create(cdef, aconf),
        _data_client_id(cdef, aconf),
        _data_client_update(cdef, aconf),
        _data_client_upsert(cdef, aconf),
        _data_client_find(cdef, aconf),
        _data_client_delete(cdef, aconf),
        _sign_in(cdef),
        '}'
    ], 2)


def _data_client_create(cdef: CDef, aconf: AConf) -> str:
    if 'C' not in aconf.actions:
        return ''
    return join_lines([
        f'    create(input: {to_create_input(cdef)}, query?: {to_single_query(cdef)}): {to_create_request(cdef)}<{cdef.name}> {"{"}',
        f'        return new {to_create_request(cdef)}(input, query)',
        '    }',
        '\n',
        f'    createMany(input: {to_create_input(cdef)}[]): {to_create_many_request(cdef)}<{cdef.name}> {"{"}',
        f'        return new {to_create_many_request(cdef)}(input)',
        '    }',
    ])


def _data_client_id(cdef: CDef, aconf: AConf) -> str:
    if 'R' not in aconf.actions:
        return ''
    return join_lines([
        f'    id(id: string, query?: {to_single_query(cdef)}) {"{"}',
        f'        return new {to_id_request(cdef)}(id, query)',
        '    }',
    ])


def _data_client_update(cdef: CDef, aconf: AConf) -> str:
    if 'U' not in aconf.actions:
        return ''
    return join_lines([
        f'    update(id: string, input: {to_update_input(cdef)}, query?: {to_single_query(cdef)}): {to_update_request(cdef)}<{cdef.name}> {"{"}',
        f'        return new {to_update_request(cdef)}(id, input, query)',
        '    }',
        '\n',
        f'    updateMany(input: {to_query_data(cdef)}): {to_update_many_request(cdef)}<{cdef.name}> {"{"}',
        f'        return new {to_update_many_request(cdef)}(input)',
        '    }'
    ])


def _data_client_upsert(cdef: CDef, aconf: AConf) -> str:
    if not all( element in aconf.actions for element in ['C','U']):
        return ''
    return join_lines([
        f'    upsert(input: {to_query_data(cdef)}): {to_upsert_request(cdef)}<{cdef.name}> {"{"}',
        f'        return new {to_upsert_request(cdef)}(input)',
        '    }',
    ])



def _data_client_find(cdef: CDef, aconf: AConf) -> str:
    if 'L' not in aconf.actions:
        return ''
    return join_lines([
        f'    find(query?: {to_list_query(cdef)}): {to_list_request(cdef)}<{cdef.name}> {"{"}',
        f'        return new {to_list_request(cdef)}(query)',
        '    }',
    ])


def _data_client_delete(cdef: CDef, aconf: AConf) -> str:
    if 'D' not in aconf.actions:
        return ''
    return join_lines([
        f'    delete(id: string): {to_delete_request(cdef)} {"{"}',
        f'        return new {to_delete_request(cdef)}(id)',
        '    }',
        '\n',
        f'    deleteMany(query?: {to_seek_query(cdef)}): {to_delete_many_request(cdef)} {"{"}',
        f'        return new {to_delete_many_request(cdef)}(query)',
        '    }',
    ])


def _sign_in(cdef: CDef) -> str:
    if not class_needs_session(cdef):
        return ''
    return join_lines([
        '\n',
        f'    signIn(input: {to_session_input(cdef)}, query?: {to_single_query(cdef)}): {to_sign_in_request(cdef)}<{to_session(cdef)}>{"{"}',
        f'       return new {to_sign_in_request(cdef)}(input, query)',
        '    }'
    ])
