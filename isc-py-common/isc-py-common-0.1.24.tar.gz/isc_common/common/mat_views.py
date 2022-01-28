import logging
import sys
from typing import Text

from django.conf import settings
from django.db import connection

from isc_common.common import uuid4
from sheduler import make_shedurer_tasks

logger = logging.getLogger(__name__)


def exists_base_object(table_name, schem_aname='public'):
    sql_text = '''SELECT n.nspname, c.relname
                    FROM pg_catalog.pg_class c
                             JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = %s
                      AND n.nspname = %s'''

    with connection.cursor() as cursor:
        cursor.execute(sql_text, [table_name, schem_aname])
        rows = cursor.fetchone()
        if rows is None:
            return False
        else:
            return len(rows) > 0


def create_tmp_mat_view(sql_str, params=[], indexes=[], mat_view_name=None, check_exists=False) -> Text:
    if check_exists is True and check_exists is not None and exists_base_object(mat_view_name):
        return mat_view_name

    key = f'create_tmp_mat_view_{mat_view_name}'
    if mat_view_name is not None:
        settings.LOCKS.acquire(key)
    else:
        mat_view_name = f'tmp_{uuid4()}'

    if isinstance(indexes, list):
        indexes = [f'''CREATE INDEX {mat_view_name}_{index}_idx ON {mat_view_name} USING btree ("{index}")''' for index in indexes]
        suffix = ';'.join(indexes)
    sql_txt = f'''CREATE MATERIALIZED VIEW {mat_view_name} AS {sql_str} WITH DATA; {suffix}'''
    try:
        with connection.cursor() as cursor:
            logger.debug(f'Creating: {mat_view_name}')
            cursor.execute(sql_txt, params)
            logger.debug(f'Created: {mat_view_name}')
        if mat_view_name is not None:
            settings.LOCKS.release(key)
        return mat_view_name
    except Exception as ex:
        exc_info = sys.exc_info()
        logger.error(msg=ex, exc_info=exc_info)
        if mat_view_name is not None:
            settings.LOCKS.release(key)
        return None


def create_view(sql_str, params=[], view_name=None) -> None:
    if view_name is None:
        raise Exception(f'View must have name')

    if exists_base_object(view_name):
        return view_name

    key = f'createt_view_{view_name}'
    settings.LOCKS.acquire(key)

    sql_txt = f'''DROP VIEW IF EXISTS {view_name} CASCADE;'''
    sql_txt += f'''CREATE VIEW {view_name} AS {sql_str};'''
    try:
        with connection.cursor() as cursor:
            logger.debug(f'Creating: {view_name}')
            cursor.execute(sql_txt, params)
            logger.debug(f'Created: {view_name}')
        settings.LOCKS.release(key)
    except Exception as ex:
        exc_info = sys.exc_info()
        logger.error(msg=ex, exc_info=exc_info)
        settings.LOCKS.release(key)


def create_insert_update_delete_function_of_table(
        table_name,
        table_schema='public',
        exclude_fields=[],
        func_params=[('id', 'bigint')],
        pk_names=['id']
):
    settings.LOCKS.acquire(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)
    try:
        columns_sql_str = f'''select column_name, data_type, ordinal_position
                                    from information_schema.columns
                                        where table_schema = %s
                                    and table_name = %s
                                    order by ordinal_position'''

        def insert_proc_body_str(fields, where_clause):
            return f'''insert into {table_name}_tbl ({fields}) select {fields} from {table_name}_view where {where_clause}'''

        with connection.cursor() as cursor:
            cursor.execute(columns_sql_str, [table_schema, f'{table_name}_view'])
            all_rows = cursor.fetchall()

            pk_names.extend(exclude_fields)
            rows_without_pk_field = [row for row in all_rows if row[0] not in pk_names]

            def func_param_str(param_item):
                return f'{param_item[0]} {param_item[1]}'

            def func_where_clause_str(param_item, prefix=None):
                return f'''{f'{prefix}.' if prefix else ''}"{param_item[0]}"=f{param_item[0]}'''

            def func_where_clause_str1(param_item, prefix1=None, prefix2=None):
                prefix2 = '' if prefix2 is None else f'{prefix2}.'
                return f'''{f'{prefix1}.' if prefix1 else ''}"{param_item[0]}"={prefix2}"{param_item[0]}"'''

            func_params1 = ','.join(f'f{func_param_str(a)}' for a in func_params)
            func_params2 = ','.join(f'f{a[0]}' for a in func_params)
            func_params_types = ','.join(f'{a[1]}' for a in func_params)

            where_clause = ' and '.join(f'{func_where_clause_str(a)}' for a in func_params)
            where_clause_prefix_s = ' and '.join(f'''{func_where_clause_str(param_item=a, prefix='s')}''' for a in func_params)
            where_clause_prefix_tbl = ' and '.join(f'''{func_where_clause_str1(param_item=a, prefix1=f'{table_name}_tbl', prefix2='s')}''' for a in func_params)

            fields = ','.join([f'"{row[0]}"' for row in all_rows])
            fields_without_pk_field = ','.join([f'"{row[0]}"' for row in rows_without_pk_field])

            fields_update = ','.join([f'"{row[0]}"=s."{row[0]}"' for row in rows_without_pk_field])

            insert_func_name = f'insert_into_{table_name}'
            insert_proc_str = f'''drop function if exists {insert_func_name}({func_params_types}) cascade;
                                      create function {insert_func_name}({func_params1}) returns bigint
                                            language plpgsql
                                        as
                                        $$
                                        BEGIN
                                            {insert_proc_body_str(fields=fields, where_clause=where_clause)};
                                            return fid;
                                        END;
                                        $$;'''

            cursor.execute(insert_proc_str)

            insert_proc_str = f'''drop function if exists {insert_func_name}_s(bigint[]) cascade;
                                                  create function {insert_func_name}_s(ids bigint[]) returns bigint
                                                        language plpgsql
                                                    as
                                                    $$
                                                    BEGIN
                                                        {insert_proc_body_str(fields=fields, where_clause='id=any(ids)')};
                                                        return 0;
                                                    END;
                                                    $$;'''

            cursor.execute(insert_proc_str)

            delete_proc_str = f'''drop function if exists delete_{table_name}_s(bigint[]) cascade;
                                                            create function delete_{table_name}_s(ids bigint[]) returns bigint
                                                                language plpgsql
                                                            as
                                                            $$
                                                            BEGIN
                                                                delete from {table_name}_tbl where id=any(ids);
                                                                return 0;
                                                            END;
                                                            $$;
                                                            '''

            cursor.execute(delete_proc_str)

            update_proc_str = f'''drop function if exists update_{table_name}_s(bigint[]) cascade;
                                            create function update_{table_name}_s(ids bigint[])  RETURNS bigint
                                                language plpgsql
                                            as
                                            $$
                                            BEGIN
                                                update {table_name}_tbl
                                                set 
                                                   {fields_update}
                                                from (select {fields}
                                                      from {table_name}_view) as s
                                                        where  {where_clause_prefix_tbl}
                                                        and s.id = any(ids);
                                                        return 0;                                        

                                            END;
                                            $$;'''

            cursor.execute(update_proc_str)

            update_proc_str = f'''drop function if exists update_{table_name}({func_params_types}) cascade;
                                create function update_{table_name}({func_params1})  RETURNS bigint
                                    language plpgsql
                                as
                                $$
                                declare
                                    cnt numeric;
                                BEGIN
                                
                                    select count(*)
                                    into cnt
                                    from {table_name}_tbl as s 
                                    where {where_clause_prefix_s};
                                
                                    if cnt = 0 then
                                        return {insert_func_name}({func_params2});
                                    else
                                        update {table_name}_tbl
                                        set 
                                           {fields_update}
                                        from (select {fields}
                                              from {table_name}_view) as s
                                                where  {where_clause_prefix_tbl}
                                                and {where_clause_prefix_s};
                                                return fid;                                        
                                    end if;
                                   
                                END;
                                $$;'''

            cursor.execute(update_proc_str)

            delete_proc_str = f'''drop function if exists delete_{table_name}({func_params_types}) cascade;
                                    create function delete_{table_name}({func_params1}) returns void
                                        language plpgsql
                                    as
                                    $$
                                    BEGIN
                                        delete from {table_name}_tbl where {where_clause};
                                    END;
                                    $$;
                                    '''

            cursor.execute(delete_proc_str)

            settings.LOCKS.release(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)
    except Exception as ex:
        settings.LOCKS.release(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)
        logger.error(ex)


def create_table(
        fields_str=None,
        sql_str=None,
        temporary='',
        on_commit=None,
        params=[],
        indexes=[],
        unique_indexes=[],
        primary_key=None,
        table_name=None,
        any_constraints=[],
        drop=True) -> None:
    if table_name is None:
        raise Exception(f'Table must have name')

    key = f'create_tmp_table{table_name}'
    settings.LOCKS.acquire(key)

    pk_str = ''
    if primary_key is not None:
        if not isinstance(primary_key, list):
            primary_key = [primary_key]

        # pk_str = f'''ALTER TABLE {table_name}
        #             ADD CONSTRAINT {table_name}_pk
        #                 PRIMARY KEY ({','.join(primary_key)});'''

        pk_str = f'''ALTER TABLE {table_name}
                            ADD CONSTRAINT {table_name}_pk
                                UNIQUE ({','.join(primary_key)});'''

    indexes_str = ''
    if isinstance(indexes, list):
        indexes = [f'''CREATE INDEX {table_name}_{index}_idx ON {table_name} USING btree ("{index}")''' for index in indexes]
        indexes_str = ';'.join(indexes)

    unique_indexes_str = ''
    if isinstance(unique_indexes, list):
        if len(unique_indexes):
            qt_fld = list(map(lambda x: f'"{x}"', unique_indexes[0:len(unique_indexes) - 1]))
            unique_indexes_str = ';\n' + f'''CREATE UNIQUE INDEX {table_name}_{'_'.join(unique_indexes)}_idx ON {table_name} USING btree ({','.join(qt_fld)}) WHERE ("{unique_indexes[len(unique_indexes) - 1]}" is null);'''

    sql_txt = ''
    if drop:
        sql_txt = f'''DROP TABLE IF EXISTS {table_name} CASCADE;'''

    on_commit_str = f'ON COMMIT {on_commit}'
    if on_commit is None:
        on_commit_str = ''

    if sql_str is None:
        sql_txt += f'''CREATE {temporary} TABLE {table_name} ({fields_str}) {on_commit_str}'''
    else:
        sql_txt += f'''CREATE {temporary} TABLE {table_name} as ({sql_str}); {on_commit_str}'''

    sql_txt += pk_str
    sql_txt += ';\n'.join(any_constraints)
    sql_txt += indexes_str
    sql_txt += unique_indexes_str

    try:
        with connection.cursor() as cursor:
            logger.debug(f'Creating: {table_name}')
            cursor.execute(sql_txt, params)
            logger.debug(f'Created: {table_name}')
        settings.LOCKS.release(key)
    except Exception as ex:
        exc_info = sys.exc_info()
        logger.error(msg=ex, exc_info=exc_info)
        settings.LOCKS.release(key)
        raise ex


def create_table1(
        fields_str=None,
        sql_str=None,
        temporary='',
        on_commit=None,
        params=[],
        indexes=[],
        unique_indexes=[],
        primary_key=None,
        table_name=None,
        any_constraints=[],
        drop=True) -> None:
    if table_name is None:
        raise Exception(f'Table must have name')

    key = f'create_tmp_table{table_name}'
    settings.LOCKS.acquire(key)

    pk_str = ''
    if primary_key is not None:
        if not isinstance(primary_key, list):
            primary_key = [primary_key]

        # pk_str = f'''ALTER TABLE {table_name}
        #             ADD CONSTRAINT {table_name}_pk
        #                 PRIMARY KEY ({','.join(primary_key)});'''

        pk_str = f'''ALTER TABLE {table_name}
                            ADD CONSTRAINT {table_name}_pk
                                UNIQUE ({','.join(primary_key)});'''

    indexes_str = ''
    if isinstance(indexes, list):
        indexes = [f'''CREATE INDEX {table_name}_{index}_idx ON {table_name} USING btree ("{index}")''' for index in indexes]
        indexes_str = ';'.join(indexes)

    unique_indexes_str = ''
    if isinstance(unique_indexes, list):
        if len(unique_indexes):
            qt_fld = list(map(lambda x: f'"{x}"', unique_indexes[0:len(unique_indexes) - 1]))
            unique_indexes_str = ';\n' + f'''CREATE UNIQUE INDEX {table_name}_{'_'.join(unique_indexes)}_idx ON {table_name} USING btree ({','.join(qt_fld)}) WHERE ("{unique_indexes[len(unique_indexes) - 1]}" is null);'''

    sql_txt = ''
    if drop:
        sql_txt = f'''DROP TABLE IF EXISTS {table_name} CASCADE;'''

    on_commit_str = f'ON COMMIT {on_commit}'
    if on_commit is None:
        on_commit_str = ''

    if sql_str is None:
        sql_txt += f'''CREATE {temporary} TABLE {table_name} ({fields_str}) {on_commit_str};'''
    else:
        sql_txt += f'''CREATE {temporary} TABLE {table_name} as ({sql_str}); {on_commit_str};'''

    sql_txt += pk_str
    sql_txt += ';\n'.join(any_constraints)
    sql_txt += indexes_str
    sql_txt += unique_indexes_str

    try:

        with connection.cursor() as cursor:
            logger.debug(f'Creating: {table_name}')
            cursor.execute(sql_txt, params)
            logger.debug(f'Created: {table_name}')
            view_name = table_name.replace("tbl", "view")

            sql_txt = f'insert into {table_name} select * from {view_name} where id=%s'

            sql_txt1 = f'select count(*) from planing_production_order_lt_view'
            cursor.execute(sql_txt1, params)
            cnt, = cursor.fetchone()
            i = 0

            sql_txt1 = f'select id from planing_production_order_lt_view'

            cursor.execute(sql_txt1, params)
            rows = cursor.fetchall()
            for row in rows:
                logger.debug(f'Inserting ({i} form {cnt}): Where id={row[0]}')
                cursor.execute(sql_txt, row)
                i += 1

        settings.LOCKS.release(key)
    except Exception as ex:
        exc_info = sys.exc_info()
        logger.error(msg=ex, exc_info=exc_info)
        settings.LOCKS.release(key)
        raise ex


def create_tmp_table(fields_str=None, sql_str=None, on_commit='delete rows', params=[], indexes=[], unique_indexes=[], table_name=None, drop=True) -> None:
    create_table(
        drop=drop,
        fields_str=fields_str,
        indexes=indexes,
        on_commit=on_commit,
        params=params,
        sql_str=sql_str,
        table_name=table_name,
        temporary='TEMPORARY',
        unique_indexes=unique_indexes,
    )


def drop_mat_view(mat_view_name) -> bool:
    if not exists_base_object(mat_view_name):
        return False

    sql_txt = f'DROP MATERIALIZED VIEW IF EXISTS {mat_view_name} CASCADE;'
    try:
        if exists_base_object(mat_view_name) == False:
            return False

        key = f'drop_mat_view_{mat_view_name}'
        settings.LOCKS.acquire(key)
        with connection.cursor() as cursor:
            logger.debug(f'Droping: {mat_view_name}')
            cursor.execute(sql_txt)
        settings.LOCKS.release(key)
        logger.debug(f'Droped: {mat_view_name}')
        return True
    except Exception as ex:
        exc_info = sys.exc_info()
        logger.error(msg=ex, exc_info=exc_info)
        settings.LOCKS.release(key)
        return False


def refresh_mat_view(mat_view_name, username=None):
    from isc_common.ws.webSocket import WebSocket

    if not exists_base_object(mat_view_name):
        return

    def _refresh():
        sql_txt = f'REFRESH MATERIALIZED VIEW {mat_view_name};'
        key = f'refresh_mat_view_{mat_view_name}'
        settings.LOCKS.acquire(key)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_txt)
            settings.LOCKS.release(key)

            if username is not None:
                WebSocket.send_info_message(
                    host=settings.WS_HOST,
                    port=settings.WS_PORT,
                    channel=f'common_{username}',
                    message=f'Обновление {mat_view_name} выполнено.',
                    logger=logger
                )

        except Exception as ex:
            exc_info = sys.exc_info()
            logger.error(msg=ex, exc_info=exc_info)
            settings.LOCKS.release(key)

    make_shedurer_tasks(_refresh, when='1s')

    return True
