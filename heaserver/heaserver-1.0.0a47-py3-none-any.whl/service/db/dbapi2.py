"""
This module implements convenience functions for querying databases using the Python Database API Specification v2.0
(DB-API2). Documentation for DB-API2 is available from https://www.python.org/dev/peps/pep-0249/.
"""
import contextlib


@contextlib.contextmanager
def db_connect(db_driver, cn_params):
    """
    Manage a connection to a database.

    :param db_driver: the DB-API2 module (required).
    :param cn_params: a tuple or dict of connection parameters to pass to the driver's connect function (required).
    :return: the connection.
    :raise: any exception thrown by the database driver.
    """
    if isinstance(cn_params, dict):
        cn = db_driver.connect(**cn_params)
    else:
        cn = db_driver.connect(*cn_params)
    try:
        yield cn
        cn.close()
        cn = None
    finally:
        _close_quietly(cn)


@contextlib.contextmanager
def transaction(cn):
    """
    Context manager that automatically commits the current transaction before leaving the context. If an exception is
    raised, it will rollback the current transaction instead. Because DB-API2 only supports implicit transactions,
    transaction start is the first statement executed, or the first statement executed since the most recent commit or
    rollback. Therefore, this context manager does not define a transaction start -- it could continue a transaction
    that was started previously.

    :param cn: the connection (required).
    :return: the connection. Because you already must have the connection, this typically would be called omitting the
    'as' syntax.
    """
    try:
        yield cn
        cn.commit()
    except Exception as e:
        try:
            cn.rollback()
        except:
            pass
        raise e


def execute(cn, stmt, stmt_params=None, handle_result=None):
    """
    Execute the given statement in the database, and process the result in the handle_result method.

    :param cn: a database connection (required).
    :param stmt: the database operation to execute (required).
    :param stmt_params: parameters to bind to variables in the operation.
    :param handle_result: a callable that accepts one cursor argument (optional). The _execute method handles closing
    the cursor for you, so there is no need to close it in this callable.
    :return: the return value from calling handle_result, or None if handle_result is None.
    :raise: any exception thrown by the database driver.
    """
    with contextlib.closing(cn.cursor()) as cur:
        cur.execute(stmt, stmt_params)
        if handle_result:
            return handle_result(cur)
        else:
            return None


def execute_cn(db_driver, cn_params, stmt, stmt_params=None, handle_result=None):
    """
    Create a connection, execute the given statement in the database, and process the result in the handle_result
    method.

    :param db_driver: the DB-API2 module (required).
    :param cn_params: a tuple of connection parameters to pass to the driver's connect function (required).
    :param stmt: the database operation to execute (required).
    :param stmt_params: parameters to bind to variables in the operation.
    :param handle_result: a callable that accepts one cursor argument (optional). The _execute method handles closing
    the cursor for you, so there is no need to close it in this callable.
    :return: the return value from calling handle_result, or None if handle_result is None.
    :raise: any exception thrown by the database driver.
    """
    with db_connect(db_driver, cn_params) as cn:
        return execute(cn, stmt, stmt_params, handle_result)


def execute_many(cn, stmt, stmt_params):
    """
    Execute the given statement in the database many times with different parameters. SELECT statements cannot be
    executed with this function -- use _execute_one instead.

    :param cn: a database connection (required).
    :param stmt: the database operation to execute (required).
    :param stmt_params: a sequence of sequences of parameters to bind to variables in each operation.
    :return:
    """
    with contextlib.closing(cn.cursor()) as cur:
        cur.executemany(stmt, stmt_params)


def execute_many_cn(db_driver, cn_params, stmt, stmt_params=None):
    """
    Create a connection, and execute the given statement in the database many times with different parameters. SELECT
    statements cannot be executed with this function -- use _execute_one instead.

    :param db_driver: the DB-API2 module (required).
    :param cn_params: a tuple or dict of connection parameters to pass to the driver's connect function (required).
    :param stmt: the database operation to execute (required).
    :param stmt_params: a sequence of sequences of parameters to bind to variables in each operation.
    :return: the return value from calling handle_result, or None if handle_result is None.
    :raise: any exception thrown by the database driver.
    """
    with db_connect(db_driver, cn_params) as cn:
        with contextlib.closing(cn.cursor()) as cur:
            cur.executemany(stmt, stmt_params)


def generate(db_driver, cn_params, stmt, next_params, count, commit_freq=10000):
    """
    Generate parameters and use repeatedly in a database DML operation.

    :param db_driver: the DB-API2 module (required).
    :param cn_params: a tuple or dict of connection parameters to pass to the driver's connect function (required).
    :param stmt: the DML operation to execute (required).
    :param next_params: a generator of parameter tuples to include in the database operation.
    :param count: the number of times to call the generator.
    :param commit_freq: the frequency of commits (required; default is every 10,000 rows).
    """
    with db_connect(db_driver, cn_params) as cn:
        id_ = 0
        while id_ < count:
            with transaction(cn):
                locations = tuple(next_params() for i in range(commit_freq) if id_ + i < count)
                id_ += len(locations)
                execute_many(cn, stmt, locations)
        cn.commit()


def _close_quietly(obj):
    """
    If obj is not None, this function calls its close() method ignoring any exceptions that are
    raised. If obj is None, this function does nothing.

    :param obj: an object with a no-argument close method (optional).
    """
    if obj is not None:
        try:
            obj.close()
        except:
            pass
