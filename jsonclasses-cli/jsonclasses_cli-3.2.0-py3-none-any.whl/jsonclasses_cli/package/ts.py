from pathlib import Path
from typing import Literal, cast
from inflection import camelize, underscore, dasherize
from jsonclasses.cdef import Cdef
from jsonclasses.cgraph import CGraph
from jsonclasses.fdef import FStore, Fdef, FType, Nullability, Queryability, ReadRule, WriteRule
from jsonclasses.jfield import JField
from jsonclasses.modifiers.required_modifier import RequiredModifier
from jsonclasses.modifiers.default_modifier import DefaultModifier
from jsonclasses_server.api_object import APIObject


def ts(dest: Path, cgraph: CGraph):
    dest = dest / 'packages' / 'ts'
    if not dest.is_dir():
        dest.mkdir(parents=True)
    # src/index.ts main program file
    import_line = _import_line()
    interfaces = _gen_interfaces(cgraph, cgraph._map)
    module = _gen_code(cgraph)
    file_content = "\n".join([import_line, interfaces, module])
    src_dir = dest / 'src'
    if not src_dir.is_dir():
        src_dir.mkdir(parents=True)
    with open(str(dest / 'src/index.ts'), 'w') as file:
        file.write(file_content)
    # package.json
    pkgjson_content = _gen_package_json(dest)
    with open(str(dest / 'package.json'), 'w') as file:
        file.write(pkgjson_content)
    # tsconfig.json
    tsconfig_content = _gen_tsconfig_json()
    with open(str(dest / 'tsconfig.json'), 'w') as file:
        file.write(tsconfig_content)
    # .gitignore
    gitignore_content = _gen_gitignore()
    with open(str(dest / '.gitignore'), 'w') as file:
        file.write(gitignore_content)


def _gen_idref_modify(idtype: str) -> str:
    add = 'interface RefListAdd {\n' + f'    _add: {idtype}' + '}'
    rem = 'interface RefListDel {\n' + f'    _del: {idtype}' + '}'
    typ = 'type RefListItem = RefListAdd | RefListDel'
    return add + '\n\n' + rem + '\n\n' + typ + '\n\n'


def _gen_interface(name: str, items: dict[str, str]) -> str:
    return 'interface ' + name + ' {\n' + "\n".join(["    " + k + ": " + v for k, v in items.items()]) + '\n}\n\n'


def _gen_query_interface(name: str, items: dict[str, str]) -> str:
    items.update({ # order, include, pick, omit
        '_pageSize?': 'number',
        '_pageNumber?': 'number',
        '_skip?': 'number',
        '_limit?': 'number'
    })
    return _gen_interface(name, items)


def _gen_queries(query_names: list[str]) -> str:
    retval = ''
    if 'StringQuery' in query_names:
        retval += _string_query() + '\n'
    if 'NumberQuery' in query_names:
        retval += _number_query() + '\n'
    if 'BooleanQuery' in query_names:
        retval += _boolean_query() + '\n'
    if 'DateQuery' in query_names:
        retval += _date_query() + '\n'
    return retval


def _gen_interfaces(cgraph: CGraph, cmap: dict[str, Cdef]) -> str:
    required_enums: list[str] = []
    required_queries: list[str] = []
    session_names: list[str] = []
    use_idref_modify: bool = False
    retval = ''
    interfaces = ''
    for (name, cdef) in cmap.items():
        if not hasattr(cdef.cls, 'aconf'):
            continue
        result_name = name
        result = {}
        create_name = name + 'CreateInput'
        create = {}
        update_name = name + 'UpdateInput'
        update = {}
        query_name = name + 'Query'
        query = {}
        use_session = hasattr(cdef.cls, 'auth_conf')
        srname = cdef.cls.auth_conf.info.srname if use_session else ''
        session_name = name + 'Session'
        session_input_name = name + 'SessionInput'
        session_identities = {}
        session_bys = {}
        for field in cdef.fields:
            required = next((True for v in field.types.modifier.vs if isinstance(v, RequiredModifier)), False)
            has_default = next((True for v in field.types.modifier.vs if isinstance(v, DefaultModifier)), False)
            nonnull = False
            if field.fdef.ftype == FType.ENUM:
                required_enums.append(field.fdef.enum_class.__name__)
            if field.fdef.ftype == FType.LIST:
                if field.fdef.fstore == FStore.LOCAL_KEY or field.fdef.fstore == FStore.FOREIGN_KEY:
                    if field.fdef.collection_nullability == Nullability.NONNULL:
                        required = True
                        has_default = True
                        nonnull = True
            if field.fdef.read_rule != ReadRule.NO_READ:
                if field.fdef.fstore != FStore.TEMP:
                    result[field.json_name + ('' if required else '?')] = _ts_type(field.fdef, 'R')
                    if field.fdef.fstore == FStore.LOCAL_KEY:
                        rkes = cdef.jconf.ref_key_encoding_strategy
                        idname = cdef.jconf.key_encoding_strategy(rkes(field))
                        idtype = _ts_type(cdef.primary_field.fdef, 'R') + ('[]' if field.fdef.ftype == FType.LIST else '')
                        result[idname] = idtype
            if field.fdef.write_rule != WriteRule.NO_WRITE:
                only_create = required and field.fdef.write_rule == WriteRule.WRITE_ONCE
                create_optional = (not required) or has_default
                no_input = field.fdef.fstore == FStore.CALCULATED and field.fdef.setter is None
                if not no_input:
                    create[field.json_name + ('?' if create_optional else '')] = _ts_type(field.fdef, 'C')
                    if field.fdef.fstore == FStore.LOCAL_KEY:
                        rkes = cdef.jconf.ref_key_encoding_strategy
                        idname = cdef.jconf.key_encoding_strategy(rkes(field))
                        idtype = _ts_type(cdef.primary_field.fdef, 'C') + ('[]' if field.fdef.ftype == FType.LIST else '')
                        create[idname] = idtype
                    if not only_create:
                        update[field.json_name + '?'] = _ts_type(field.fdef, 'U') + ('' if required or nonnull else ' | null')
                        if field.fdef.fstore == FStore.LOCAL_KEY:
                            rkes = cdef.jconf.ref_key_encoding_strategy
                            idname = cdef.jconf.key_encoding_strategy(rkes(field))
                            idtype = _ts_type(cdef.primary_field.fdef, 'U') + ('[]' if field.fdef.ftype == FType.LIST else ('' if required else ' | null'))
                            update[idname] = idtype
            if field.fdef.queryability != Queryability.UNQUERYABLE:
                temp_field = field.fdef.fstore == FStore.TEMP
                calc_field = field.fdef.fstore == FStore.CALCULATED
                ref_field = field.fdef.fstore == FStore.LOCAL_KEY or field.fdef.fstore == FStore.FOREIGN_KEY
                if temp_field or calc_field:
                    pass
                elif ref_field:
                    pass
                else:
                    qtype = _ts_type(field.fdef, 'Q')
                    query[field.json_name + '?'] = qtype
                    if qtype.endswith('Query'):
                        if qtype not in required_queries:
                            required_queries.append(qtype)
            if use_session:
                if field.fdef.auth_identity:
                    session_identities[field.json_name] = _ts_type(field.fdef, 'C')
                elif field.fdef.auth_by:
                    session_bys[field.json_name] = _ts_type(field.fdef, 'C')
        result_interface = _gen_interface(result_name, result)
        create_interface = _gen_interface(create_name, create)
        update_interface = _gen_interface(update_name, update)
        query_interface = _gen_query_interface(query_name, query)
        if use_session:
            if len(session_identities) > 1:
                session_identities = {k + '?': v for k, v in session_identities.items()}
            if len(session_bys) > 1:
                session_bys = {k + '?': v for k, v in session_bys.items()}
            session_input_interface = _gen_interface(session_input_name, session_identities | session_bys) + '\n'
            session_result_interface = _gen_interface(session_name, {
                'token': 'string',
                srname: query_name
            })
            session_interface = session_input_interface + '\n' + session_result_interface
            session_names.append(session_name)
        else:
            session_interface = ''
        interfaces = interfaces + result_interface + '\n' + create_interface + '\n' + update_interface + '\n' + query_interface + '\n' + session_interface
    retval = retval + _gen_enum_interfaces(cgraph, required_enums) + '\n'
    retval = retval + _gen_queries(required_queries) + '\n'
    retval = retval + interfaces
    if len(session_names) > 0:
        retval += "\ntype Session = " + " | ".join(session_names) + "\n\n"
    return retval


def _gen_enum_interfaces(cgraph: CGraph, enum_names: list[str]) -> str:
    interfaces: list[str] = []
    for name in enum_names:
        enum_cls = cgraph._enum_map[name]
        line_one = 'enum ' + name + ' {\n'
        last_line = '}\n'
        lines: list[str] = []
        for option in enum_cls:
            ts_val = option.name
            ts_name = camelize(option.name.lower())
            lines.append('    ' + ts_name + ' = ' + "'" + ts_val + "',\n")
        interfaces.append(line_one + "".join(lines) + last_line)
    return "\n".join(interfaces)


def _ts_type(fdef: Fdef, mode: Literal['C', 'U', 'R', 'Q']) -> str:
    match fdef.ftype:
        case FType.STR:
            if mode == 'Q':
                return 'StringQuery'
            else:
                return 'string'
        case FType.INT:
            if mode == 'Q':
                return 'NumberQuery'
            else:
                return 'number'
        case FType.FLOAT:
            if mode == 'Q':
                return 'NumberQuery'
            else:
                return 'number'
        case FType.BOOL:
            if mode == 'Q':
                return 'BooleanQuery'
            else:
                return 'boolean'
        case FType.DATE:
            if mode == 'Q':
                return 'DateQuery'
            elif mode == 'R':
                return 'string'
            else:
                return 'Date'
        case FType.DATETIME:
            if mode == 'Q':
                return 'DateQuery'
            elif mode == 'R':
                return 'string'
            else:
                return 'Date'
        case FType.ENUM:
            return fdef.enum_class.__name__
        case FType.LIST:
            return _ts_type(fdef.item_types.fdef, mode) + '[]'
        case FType.DICT:
            return '{[key: string]: ' + _ts_type(fdef.item_types.fdef, mode) + '}'
        case FType.INSTANCE:
            if mode == 'R':
                return fdef.inst_cls.__name__
            elif mode == 'C':
                return fdef.inst_cls.__name__ + 'CreateInput'
            elif mode == 'U':
                return fdef.inst_cls.__name__ + 'UpdateInput'
            else:
                return 'never'
        case FType.ANY:
            return 'any'
        case FType.UNION:
            return " | ".join([_ts_type(t.fdef, mode) for t in fdef.raw_union_types])
        case None:
            return "never"


def _string_query() -> str:
    return ('interface StringContainsQuery {\n'
        '    _contains: string\n'
        '}\n'
        '\n'
        'interface StringPrefixQuery {\n'
        '    _prefix: string\n'
        '}\n'
        '\n'
        'interface StringSuffixQuery {\n'
        '    _suffix: string\n'
        '}\n'
        '\n'
        'interface StringMatchQuery {\n'
        '    _match: string\n'
        '}\n'
        '\n'
        'interface StringContainsiQuery {\n'
        '    _containsi: string\n'
        '}\n'
        '\n'
        'interface StringPrefixiQuery {\n'
        '    _prefixi: string\n'
        '}\n'
        '\n'
        'interface StringSuffixiQuery {\n'
        '    _suffixi: string\n'
        '}\n'
        '\n'
        'interface StringMatchiQuery {\n'
        '    _matchi: string\n'
        '}\n'
        '\n'
        'export type StringQuery = string | StringContainsQuery | StringPrefixQuery | StringSuffixQuery | StringMatchQuery | StringContainsiQuery | StringPrefixiQuery | StringSuffixiQuery | StringMatchiQuery\n'
        )


def _number_query() -> str:
    return ('interface NumberValueQuery {\n'
        '    _gt?: number\n'
        '    _gte?: number\n'
        '    _lt?: number\n'
        '    _lte?: number\n'
        '}\n'
        '\n'
        'export type NumberQuery = number | NumberValueQuery\n'
        )


def _boolean_query() -> str:
    return (
        'export type BooleanQuery = boolean\n'
        )


def _date_query() -> str:
    return ('interface DateValueQuery {\n'
        '    _gt?: Date\n'
        '    _gte?: Date\n'
        '    _lt?: Date\n'
        '    _lte?: Date\n'
        '    _on?: Date\n'
        '}\n'
        '\n'
        'export type DateQuery = Date | DateValueQuery\n'
        )


def _import_line() -> str:
    return """import axios from 'axios'\nimport { stringify } from 'qsparser-js'\n\n"""


def _gen_session_manager() -> str:
    return """
class SessionManager {

    #sessionKey = '_jsonclasses_session'
    #session: Session | undefined

    constructor() {
        const item = localStorage.getItem(this.#sessionKey)
        if (item && item !== null && item !== '') {
            this.#session = JSON.parse(item)
        } else {
            this.#session = undefined
        }
    }

    setSession(session: Session | undefined | null) {
        if (session) {
            this.#session = session
            localStorage.setItem(this.#sessionKey, JSON.stringify(session))
        } else {
            this.#session = undefined
            localStorage.removeItem(this.#sessionKey)
        }
    }

    hasSession(): boolean {
        return this.#session !== undefined
    }

    getToken(): string | undefined {
        return this.#session?.token
    }

    getSession(): Session | undefined {
        return this.#session
    }

    clearSession() {
        this.#session = undefined
    }
}
    """.strip() + "\n"


def _gen_request_manager() -> str:
    return """
class RequestManager {

    #sessionManager: SessionManager
    #baseURL: string

    constructor(sessionManager: SessionManager, baseURL: string) {
        this.#sessionManager = sessionManager
        this.#baseURL = baseURL
    }

    get headers() {
        const token = this.#sessionManager.hasSession() ? this.#sessionManager.getToken() : undefined
        return token ? {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        } : undefined
    }

    get sessionManager(): SessionManager {
        return this.#sessionManager
    }

    qs(val: any): string | undefined {
        if (!val) {
            return undefined
        }
        if (Object.keys(val).length === 0) {
            return undefined
        }
        return '?' + stringify(val)
    }

    async post<T, U, V>(url: string, input: T, query: V | undefined = undefined): Promise<U> {
        const response = await axios.post(this.#baseURL + url + this.qs(query), input, this.headers)
        return response.data.data
    }

    async patch<T, U, V>(url: string, input: T, query: V | undefined = undefined): Promise<U> {
        const response = await axios.patch(this.#baseURL + url + this.qs(query), input, this.headers)
        return response.data.data
    }

    async delete(url: string): Promise<void> {
        await axios.delete(this.#baseURL + url, this.headers)
        return
    }

    async get<U, V>(url: string, query: V | undefined = undefined): Promise<U> {
        const response = await axios.get(this.#baseURL + url + this.qs(query), this.headers)
        return response.data.data
    }
}
    """.strip() + '\n'


def _gen_api_private_vars(models: list[str]) -> str:
    retval = ''
    for model in models:
        retval += '    #' + camelize(model, False) + 'Client: ' + camelize(model) + 'Client\n'
    return retval


def _gen_api_clients(models: list[str]) -> str:
    retval = ''
    for model in models:
        retval += '        this.#' + camelize(model, False) + 'Client = new ' + camelize(model) + 'Client(this.#requestManager)\n'
    return retval


def _gen_api_accessors(classes: list[type[APIObject]]) -> str:
    retval = ''
    for cls in classes:
        retval += ('    get ' + camelize(underscore(cls.aconf.name or cls.aconf.cname_to_pname(cls.__name__)), False) + '(): ' + cls.__name__ + 'Client {\n'
        '        return this.#' + camelize(cls.__name__, False) + 'Client\n'
        '    }\n\n'
        )
    return retval

def _gen_api(cgraph: CGraph) -> str:
    models = [cdef.name for cdef in cgraph._map.values() if hasattr(cdef.cls, 'aconf')]
    classes = [cdef.cls for cdef in cgraph._map.values() if hasattr(cdef.cls, 'aconf')]
    return """
class API {

    #sessionManager: SessionManager
    #requestManager: RequestManager
""" + _gen_api_private_vars(models) + """\n    constructor() {
        this.#sessionManager = new SessionManager()
        this.#requestManager = new RequestManager(this.#sessionManager, 'http://localhost:5000')
""" + _gen_api_clients(models) + """    }\n\n""" + _gen_api_accessors(classes) + """    signOut(): void {
        this.#sessionManager.clearSession()
    }
}

const api = new API()

export default api\n
    """


def _gen_model_client(cdef: Cdef) -> str:
    if not hasattr(cdef.cls, 'aconf'):
        return ''
    aconf = cast(type[APIObject], cdef.cls).aconf
    list = False
    read = False
    create = False
    update = False
    delete = False
    if 'L' in aconf.actions:
        list = True
    if 'R' in aconf.actions:
        read = True
    if 'C' in aconf.actions:
        create = True
    if 'U' in aconf.actions:
        update = True
    if 'D' in aconf.actions:
        delete = True
    sign_in = hasattr(cdef.cls, 'auth_conf')
    cls_name = cdef.cls.__name__
    client_name = cls_name + 'Client'
    url_name = aconf.name or aconf.cname_to_pname(cls_name)
    head = ('class ' + client_name + ' {\n'
        """
    #requestManager: RequestManager

    constructor(requestManager: RequestManager) {
        this.#requestManager = requestManager
    }\n\n""")
    tail = '}\n\n'
    middle = ''
    if create:
        middle += (
            "    async create(input: " + cls_name + 'CreateInput, query?: ' + cls_name + 'Query): Promise<' + cls_name + '> {\n'
            "        return this.#requestManager.post('/" + url_name + "', input, query)\n"
            "    }\n\n"
        )
    if update:
        middle += (
            "    async update(id: string, input: " + cls_name + 'UpdateInput, query?: ' + cls_name + 'Query): Promise<' + cls_name + '> {\n'
            "        return this.#requestManager.patch(`/" + url_name + "/${id}`, input, query)\n"
            "    }\n\n"
        )
    if delete:
        middle += (
            "    async delete(id: string): Promise<void> {\n"
            "        return this.#requestManager.delete(`/" + url_name + "/${id}`)\n"
            "    }\n\n"
        )
    if read:
        middle += (
            "    async read(id: string, query?: " + cls_name + 'Query): Promise<' + cls_name + '> {\n'
            "        return this.#requestManager.get(`/" + url_name + "/${id}`, query)\n"
            "    }\n\n"
        )
    if list:
        middle += (
            "    async list(query?: " + cls_name + 'Query): Promise<' + cls_name + '[]> {\n'
            "        return this.#requestManager.get('/" + url_name + "', query)\n"
            "    }\n\n"
        )
    if sign_in:
        middle += (
            "    async signIn(input: " + cls_name + 'SessionInput): Promise<' + cls_name + 'Session> {\n'
            "        const session = await this.#requestManager.post<" + cls_name + 'SessionInput' + ", " + cls_name + 'Session' + ", " + cls_name  + "Query>('/" + url_name + "', input)\n"
            "        this.#requestManager.sessionManager.setSession(session)\n"
            "        return session\n"
            "    }\n\n"
        )
    return head + middle + tail


def _gen_code(cgraph: CGraph) -> str:
    model_clients = [_gen_model_client(v) for _, v in cgraph._map.items()]
    sm = _gen_session_manager()
    rm = _gen_request_manager()
    api = _gen_api(cgraph)
    model_clients.extend([sm, rm, api])
    return "\n".join(model_clients)


def _gen_package_json(dest: Path) -> str:
    pkg_name = dasherize(underscore(dest.name))
    return ('''
{
    "name": "''' + pkg_name + '''",
    "version": "0.1.0",
    "private": true,
    "description": "This API client package is generated by JSONClasses CLI.",
    "main": "lib/index.js",
    "types": "lib/index.d.ts",
    "author": "",
    "dependencies": {
        "axios": "^0.24.0",
        "qsparser-js": "^1.0.1"
    },
    "devDependencies": {
        "typescript": "^4.4.4"
    }
}''').strip() + '\n'


def _gen_tsconfig_json() -> str:
    return """
{
    "compilerOptions": {
        "baseUrl": ".",
        "outDir": "./lib",
        "declaration": true,
        "target": "es2016",
        "module": "commonjs",
        "jsx": "react",
        "lib": ["ESNext", "DOM"],
        "strict": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "forceConsistentCasingInFileNames": true,
        "resolveJsonModule": true
    },
    "include": ["src", "index.ts"],
    "exclude": ["node_modules", "**/__tests__/*"]
}
    """.strip() + '\n'


def _gen_gitignore() -> str:
    return """
lib

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Diagnostic reports (https://nodejs.org/api/report.html)
report.[0-9]*.[0-9]*.[0-9]*.[0-9]*.json

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
node_modules/
jspm_packages/

# TypeScript v1 declaration files
typings/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test

# parcel-bundler cache (https://parceljs.org/)
.cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
# Comment in the public line in if your project uses Gatsby and *not* Next.js
# https://nextjs.org/blog/next-9-1#public-directory-support
# public

# vuepress build output
.vuepress/dist

# Serverless directories
.serverless/

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/

# TernJS port file
.tern-port
    """.strip() + '\n'
