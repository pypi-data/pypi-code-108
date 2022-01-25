from urllib.parse import urlparse, unquote, urlunparse, quote
import re


def connect_to_database(uri: str, library: str=None, for_write: bool=False, **kwargs):
    """
    Try, by various means, to connect to a database.

    :param uri:        URI of database.
    :param library:     A specific library to use, if available
    :param for_write:   Whether to enable write operations.
    :returns:  a DBI driver
    """
    # determine flavor of connection and work out which libraries to try
    libraries = []
    if library:
        libraries.append(library)
    uri_parts = uri.split(":")
    if uri_parts[0] == "jdbc":
        uri_parts = uri_parts[1:]
    if uri_parts[0] in ("postgres", "postgresql"):
        libraries.append("psycopg2")
    if uri_parts[0] == "mysql":
        libraries.append("pymysql")
    if uri_parts[0] == "mssql":
        libraries.append("pymssql")
    if uri_parts[0] == "sqlite":
        libraries.append("sqlite")
    params = _process_params(uri, **kwargs)
    params.pop("scheme", None)
    for lib in libraries:
        if lib in METHODS:
            conn = METHODS[lib](**params, for_write=for_write)
            if conn:
                return conn
    raise ValueError(f"No driver installed/supported for {uri_parts[0]}")


def _process_params(uri: str, **kwargs):
    """
    Use a URI to provide most of the needed values for connecting to a database.  'kwargs' supplies overrides.
    :param uri:         A URI which can supply most of the needed values.
    :param kwargs:      Additional overrides.
    :return:        A {} with all the extracted, named connection parameters.
    """
    if uri.startswith("jdbc:"):
        uri = uri[5:]
    if ":" not in uri:
        host, path = uri, ""
    else:
        parsed = urlparse(uri)
        host = parsed.netloc
        path = parsed.path
        if path.startswith("/"):
            path = path[1:]
    user = pwd = ""
    if "@" in host:
        # NOTE: '@' can occur in 'user', i.e. for Google's git repositories
        u_p, host = re.split(r'@(?!.*@)', host)
        if ":" in u_p:
            user, pwd = u_p.split(":")
        else:
            user, pwd = u_p, ""
    if ":" in host:
        host, port = host.split(":", maxsplit=1)
    else:
        port = None
    params = {
        "host": host,
        "port": int(port) if port else None,
        "database": path,
        "username": user,
        "password": pwd
    }
    params.update(kwargs)
    return params


def connect_pymysql(host, port=None, username=None, password=None, database=None, autocommit=True, for_write: bool=False, **kwargs):
    try:
        import pymysql
    except ImportError:
        return
    port = port or 3306
    conn = pymysql.connect(user=username, password=password, host=host, port=port, database=database or None, autocommit=autocommit, **kwargs)
    if not for_write:
        _set_conn_read_only(conn)
    conn._flavor = "mysql"
    return conn


def connect_pymssql(host, port=None, username=None, password=None, database=None, autocommit=True, for_write: bool=False, **kwargs):
    try:
        import pymssql
    except ImportError:
        raise Exception("MS SQL library not installed")
    more = {}
    if "timeout" in kwargs:
        more["timeout"] = int(kwargs["timeout"])
    conn = pymssql.connect(
        server=host,
        user=username,
        password=password,
        database=database,
        autocommit=autocommit,
        **more
    )
    if not for_write:
        _set_conn_read_only(conn)
    conn._flavor = "mssql"
    return conn


def connect_psycopg2(host, port=None, username=None, password=None, database=None, autocommit=True, for_write: bool=False, **kwargs):
    try:
        import psycopg2
        import psycopg2.extensions
    except ImportError:
        return
    dsn_parts = {"host": host, "port": port or 5432, "dbname": database or "postgres"}
    if username:
        dsn_parts["user"] = username
    if password:
        dsn_parts["password"] = password
    pg_args_str = " ".join("%s=%s" % (k, v) for k, v in sorted(dsn_parts.items()))
    conn = psycopg2.connect(pg_args_str, **kwargs)
    if autocommit:
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    if not for_write:
        _set_conn_read_only(conn)
    conn._flavor = "postgres"
    return conn


def connect_sqlite(host, database=None, for_write: bool=False, **kwargs):
    try:
        import sqlite3
    except ImportError:
        return
    for ignore in ["port", "username", "password", "database", "autocommit"]:
        kwargs.pop(ignore, None)
    if not for_write:
        return sqlite3.connect(f'file:{host or database}?mode=ro', uri=True, **kwargs)
    conn = sqlite3.connect(host, **kwargs)
    conn._flavor = "sqlite"
    return conn


def _set_conn_read_only(conn):
    """
    Try to enforce a read-only connection
    """
    try:
        conn.cursor().execute("set transaction read only")
    except:
        print(f"couldn't set read-only mode on connection: {conn.__class__.__name__}")


def dataframe_to_sql(dataframe, table_name: str, append: bool=False):
    """
    Generate SQL statements to create a table and add data.
    :returns a generator of (sql, parameter list)
    """
    def enquote(name):
        name = str(name)
        if re.search(r'[^A-Za-z0-9_]', name) or name[:1].isdigit():
            return f'"{name}"'
        return name
    if not append:
        yield "DROP TABLE IF EXISTS %s" % enquote(table_name), []
    dtype_to_sql = {"int64": "INTEGER", "float64": "DOUBLE PRECISION"}
    cols = list(dataframe.columns)
    types = []
    for col, dtype in zip(cols, dataframe.dtypes):
        sql_type = dtype_to_sql.get(str(dtype)) or f"VARCHAR({dataframe[col].str.len().max()+3})"
        types.append(sql_type)
    rows = dataframe.itertuples(index=False, name=None)
    fields = ", ".join("%s %s" % (enquote(col), t) for col, t in zip(cols, types))
    yield "CREATE TABLE IF NOT EXISTS %s (%s)" % (enquote(table_name), fields), []
    ins0 = "INSERT INTO %s (%s) VALUES " % (enquote(table_name), ", ".join(map(enquote, cols)))
    sqls = []
    params = []
    for row in (rows or []):
        sql = "(%s)" % ", ".join(map(lambda v: "%s", row))
        sqls.append(sql)
        params += list(row)
        if len(sqls) >= 1000:
            yield "%s%s" % (ins0, ", ".join(sqls)), params
            sqls.clear()
            params.clear()
    if sqls:
        yield "%s%s" % (ins0, ", ".join(sqls)), params


METHODS = {
    "pymysql": connect_pymysql,
    "psycopg2": connect_psycopg2,
    "pymssql": connect_pymssql,
    "sqlite": connect_sqlite
}

# TODO BigQuery
