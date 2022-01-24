import time
from typing import Dict

import snowflake
import yaml

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def get_column_value(cursor_record, column_name: str):
    column_value = cursor_record.get(column_name.upper(), None)
    if column_value is None:
        column_value = cursor_record.get(column_name.lower(), None)
    return column_value


def new_connection_from_yaml_file(connection_yaml_file: str):
    connection_params = None
    with open(connection_yaml_file, "r") as connection_params_stream:
        try:
            connection_params = yaml.safe_load(connection_params_stream)
        except yaml.YAMLError as exc:
            print(exc)
    if connection_params is not None:
        return connection_params['account'], new_connection_from_dict(connection_params)
    return None


def new_connection_from_dict(connection_params: Dict[str, str]):
    snowflake.connector.paramstyle = 'numeric'
    for param in ['account', 'db', 'schema', 'role', 'warehouse', 'user']:
        _ensure_param_present(connection_params, param)

    if 'password' in connection_params:
        return snowflake.connector.connect(
            account=connection_params['account'],
            user=connection_params['user'],
            password=connection_params['password'],
            role=connection_params['role'],
            database=connection_params['db'],
            schema=connection_params['schema'],
            warehouse=connection_params['warehouse'],
        )
    elif 'key_path' in connection_params and 'key_pass' in connection_params:
        with open("%s" % connection_params['key_path'], "rb") as key:
            p_key = serialization.load_pem_private_key(
                key.read(),
                password=connection_params['key_pass'].encode(),
                backend=default_backend()
            )

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())

        return snowflake.connector.connect(
            account=connection_params['account'],
            user=connection_params['user'],
            role=connection_params['role'],
            database=connection_params['db'],
            schema=connection_params['schema'],
            warehouse=connection_params['warehouse'],
            private_key=pkb,
        )
    else:
        print("Either password or key_path/key_pass need to be set up in the configuration.")
        return None


def _ensure_param_present(connection_params: Dict[str, str], param: str):
    param_value = connection_params.get(param, None)
    if param_value is None:
        raise ValueError("parameter '%s' not found in connection params" % param)


def run_query(sf_conn, sql, params=None):
    print(sql)

    query_param_values = []
    if params is not None:
        print(params)
        for idx, param in enumerate(params):
            sql = sql.replace(":%s:" % param[0], ':%s' % (idx + 1))
            query_param_values.append(param[1])
        print(sql)
        print(query_param_values)
    cur = sf_conn.cursor()
    cur.execute(sql, query_param_values)
    cur.close()


def fetch_one_query(sf_conn, sql, params=None):
    cur = sf_conn.cursor()
    result = cur.execute(sql, params).fetchone()
    cur.close()

    return result


def run_async_query(sf_conn, sql, params):
    print(sql)
    print(params)

    query_param_values = []
    param_idx = 1
    for param, param_value in params.items():
        sql = sql.replace(":%s:" % param, ':%s' % param_idx)
        query_param_values.append(param_value)

    cur = sf_conn.cursor()
    cur.execute_async(sql, query_param_values)
    query_id = cur.sfqid
    cur.close()

    is_query_successful = False
    try:
        while sf_conn.is_still_running(sf_conn.get_query_status_throw_if_error(query_id)):
            time.sleep(5)
        is_query_successful = True
    except snowflake.connector.ProgrammingError as err:
        print('Query Execution Error: {0}'.format(err))

    if is_query_successful:
        pass
