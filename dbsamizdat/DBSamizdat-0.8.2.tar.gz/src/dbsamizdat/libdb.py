from json import loads as jsonloads
from typing import Iterable
from itertools import chain
from enum import IntFlag

from . import entitypes, SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger

COMMENT_MAGIC = """{"dbsamizdat": {"version":"""


class DBObjectType(IntFlag):
    SAMIZDAT = 1
    FOREIGN = 2


def get_dbstate(cursor, which: DBObjectType = DBObjectType.SAMIZDAT, entity_types: Iterable[entitypes] = (entitypes.VIEW, entitypes.MATVIEW, entitypes.FUNCTION, entitypes.TRIGGER)):
    """
    Capture and annotate the current DB state (functions, views and triggers)
    """

    def execfetch(sql):
        cursor.execute(sql)
        return cursor.fetchall()

    pg11_or_lower = cursor.connection.server_version < 110000
    function_filter = "NOT (p.proisagg OR p.proiswindow OR p.prosecdef)" if pg11_or_lower else "p.prokind NOT IN ('a', 'w', 'p')"

    fetches = {
        entitypes.VIEW: """
            SELECT n.nspname AS schemaname,
                c.relname AS viewname,
                'VIEW' as viewtype,
                pg_catalog.obj_description(c.oid, 'pg_class') AS commentcontent
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'v'
                AND n.nspname <> 'pg_catalog'
                AND n.nspname <> 'information_schema'
                AND n.nspname !~ '^pg_toast'
            """,
        entitypes.MATVIEW: """
            SELECT n.nspname AS schemaname,
                c.relname AS viewname,
                'MATVIEW' as viewtype,
                pg_catalog.obj_description(c.oid, 'pg_class') AS commentcontent
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind = 'm'
                AND n.nspname <> 'pg_catalog'
                AND n.nspname <> 'information_schema'
                AND n.nspname !~ '^pg_toast'
            """,
        entitypes.FUNCTION: f"""
            SELECT n.nspname AS "schemaname",
                p.proname AS "functionname",
                'FUNCTION',
                pg_catalog.pg_get_function_identity_arguments(p.oid) AS args,
                pg_catalog.obj_description(p.oid, 'pg_proc') AS commentcontent
            FROM pg_catalog.pg_proc p
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
            WHERE {function_filter}
                AND n.nspname <> 'pg_catalog'
                AND n.nspname <> 'information_schema'
            """,
        entitypes.TRIGGER: """
            SELECT
                pn.nspname AS schemaname,
                pt.tgname AS triggername,
                'TRIGGER',
                pc.relname AS tablename,
                pg_catalog.obj_description(pt.oid, 'pg_trigger') AS commentcontent
            FROM
                pg_trigger pt
                LEFT JOIN pg_class pc ON pt.tgrelid = pc.oid
                LEFT JOIN pg_catalog.pg_namespace pn ON pn.oid = pc.relnamespace
            WHERE
                pt.tgisinternal = False
            """
    }

    for *stuff, jinfo in chain(*map(execfetch, map(fetches.get, entity_types))):
        objtype = DBObjectType.SAMIZDAT if (jinfo and jinfo.startswith(COMMENT_MAGIC)) else DBObjectType.FOREIGN
        if objtype & which:
            definition_hash = None
            if objtype == DBObjectType.SAMIZDAT:
                meta = jsonloads(jinfo)['dbsamizdat']
                hashattr = {0: 'sql_template_hash', 1: 'definition_hash'}[meta['version']]
                definition_hash = meta[hashattr]
            yield tuple(stuff + [definition_hash])


def dbinfo_to_class(dbstate_info):
    """
    Reconstruct a class out of information found in the DB
    """
    typemap = {c.entity_type: c for c in (SamizdatView, SamizdatMaterializedView, SamizdatFunction, SamizdatTrigger)}
    schema, objectname, objecttype, *maybe_args, definition_hash = dbstate_info
    entity_type = entitypes[objecttype]
    classfields = dict(
        schema=schema,
        implanted_hash=definition_hash,
    )
    if entity_type == entitypes.FUNCTION:
        classfields.update(dict(
            function_arguments_signature=maybe_args[0],
            function_name=objectname,
        ))
    elif entity_type == entitypes.TRIGGER:
        classfields.update(dict(
            schema=None,
            on_table=(schema, maybe_args[0]),
        ))

    return type(objectname, (typemap[entitypes[objecttype]],), classfields)


def dbstate_equals_definedstate(cursor, samizdats):
    dbstate = {ds.head_id(): ds for ds in map(dbinfo_to_class, get_dbstate(cursor))}
    definedstate = {ds.head_id(): ds for ds in samizdats}
    return (
        dbstate.keys() == definedstate.keys(),
        {dbstate[k] for k in dbstate.keys() - definedstate.keys()},
        {definedstate[k] for k in definedstate.keys() - dbstate.keys()}
    )
