from typing import cast
from jsonclasses.cdef import CDef
from jsonclasses_server.aconf import AConf
from ...utils.package_utils import (class_needs_session, to_include, to_result_picks,
                                    to_session_input, to_sign_in_request, to_session, to_single_query)
from .shared_utils import interface_required_include

def sign_in_request(cdef: CDef) -> str:
    if not class_needs_session(cdef):
        return ''
    name = cast(AConf, cdef.cls.aconf).name
    return f"""
class {to_sign_in_request(cdef)}<T extends Partial<{to_session(cdef)}>> extends Promise<T> {'{'}

    #input: {to_session_input(cdef)}
    #query?: {to_single_query(cdef)}

    constructor(input: {to_session_input(cdef)}, query?:{to_single_query(cdef)}){'{'}
        super(() => {'{'}{'}'})
        this.#input = input
        this.#query = query
    {'}'}

    {_data_query_request_common(cdef, to_sign_in_request(cdef))}
    {_data_query_request_includes(cdef, to_sign_in_request(cdef)) if interface_required_include(cdef) else ''}
    async exec(): Promise<{to_session(cdef)}> {'{'}
        const session = await RequestManager.share.post('/{name}/session', this.#input, this.#query) as {to_session(cdef)}
        SessionManager.share.setSession(session)
        return session
    {'}'}
{'}'}
    """.strip() + "\n"


def _data_query_request_includes(cdef: CDef, request: str) -> str:
    return f"""
    include(includes: {to_include(cdef)}[]): {request}<T> {'{'}
        this.#query = {'{'}...this.#query, _includes: includes {'}'}
        return this
    {'}'}
        """.strip() + "\n"


def _data_query_request_common(cdef: CDef, request: str) -> str:
    return f"""
    pick(picks: {to_result_picks(cdef)}[]): {request}<T> {'{'}
        this.#query = {'{'}...this.#query, _pick: picks{'}'}
        return this
    {'}'}

    omit(omits: {to_result_picks(cdef)}[]): {request}<T> {'{'}
        this.#query = {'{'}...this.#query, _omit: omits{'}'}
        return this
    {'}'}
    """.strip() + "\n"
