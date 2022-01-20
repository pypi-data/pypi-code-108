import datetime
import json
from contextlib import suppress
from math import floor
from time import time

from django.template.defaultfilters import truncatechars
from django.utils.encoding import force_str
from opentracing import global_tracer


def wrap_cursor(connection):
    """Wrap cursor for logging sql queries into jaeger."""
    if not hasattr(connection, "_traced_cursor"):  # noqa: WPS421
        connection._traced_cursor = connection.cursor
        connection._traced_chunked_cursor = connection.chunked_cursor

        def cursor(*args, **kwargs):  # noqa: WPS430
            # Per the DB API cursor() does not accept any arguments. There"s
            # some code in the wild which does not follow that convention,
            # so we pass on the arguments even though it"s not clean.
            # See:
            # https://github.com/jazzband/django-debug-toolbar/pull/615
            # https://github.com/jazzband/django-debug-toolbar/pull/896
            return NormalCursorWrapper(
                connection._traced_cursor(*args, **kwargs),
                connection,
            )

        def chunked_cursor(*args, **kwargs):  # noqa: WPS430
            return NormalCursorWrapper(
                connection._traced_chunked_cursor(*args, **kwargs),
                connection,
            )

        connection.cursor = cursor
        connection.chunked_cursor = chunked_cursor
        return cursor


def unwrap_cursor(connection):
    """Unwrap cursor."""
    if hasattr(connection, "_traced_cursor"):  # noqa: WPS421
        del connection._traced_cursor  # noqa: WPS420
        del connection.cursor  # noqa: WPS420
        del connection.chunked_cursor  # noqa: WPS420


class NormalCursorWrapper:
    """Wraps a cursor and logs queries."""

    def __init__(self, cursor, db):
        """Initialize."""
        self.cursor = cursor
        # Instance of a BaseDatabaseWrapper subclass
        self.db = db

    def callproc(self, procname, params=None):
        """Wrap callproc."""
        return self._record(self.cursor.callproc, procname, params)

    def execute(self, sql, params=None):
        """Wrap execute."""
        return self._record(self.cursor.execute, sql, params)

    def executemany(self, sql, param_list):
        """Wrap executemany."""
        return self._record(self.cursor.executemany, sql, param_list)

    def __exit__(self, type_, value, traceback):
        self.close()

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def __enter__(self):
        return self

    def _quote_expr(self, element):
        if isinstance(element, str):
            return "'{0}'".format(element.replace("'", "''"))

        return repr(element)

    def _quote_params(self, params):
        if not params:
            return params
        if isinstance(params, dict):
            return {
                key: self._quote_expr(value) for key, value in params.items()
            }
        return [self._quote_expr(p) for p in params]

    def _decode(self, param):
        # If a sequence type, decode each element separately
        if isinstance(param, (tuple, list)):
            return [self._decode(element) for element in param]

        # If a dictionary type, decode each value separately
        if isinstance(param, dict):
            return {key: self._decode(value) for key, value in param.items()}

        # make sure datetime, date and time are converted to string by force_str
        convert_types = (datetime.datetime, datetime.date, datetime.time)
        try:
            return force_str(
                param,
                strings_only=not isinstance(param, convert_types),
            )
        except UnicodeDecodeError:
            return "(encoded string)"

    def _record(self, method, sql, params):
        start_time = time()

        # Sql might be an object (such as psycopg Composed).
        # For logging purposes, make sure it"s str.
        sql_str = str(sql)

        with global_tracer().start_active_span(
            truncatechars(sql_str, 90),
            start_time=start_time,
            tags={"scope": "sql"},
            child_of=global_tracer().active_span,
        ) as scope:

            try:  # noqa:WPS501
                return method(sql, params)

            finally:
                stop_time = time()
                duration = (stop_time - start_time) * 1000
                serialized_params = ""

                with suppress(TypeError):
                    serialized_params = json.dumps(self._decode(params))

                alias = getattr(self.db, "alias", "default")
                conn = self.db.connection
                vendor = getattr(conn, "vendor", "unknown")

                scope.span.log_kv(
                    {
                        "vendor": vendor,
                        "alias": alias,
                        "sql": self.db.ops.last_executed_query(
                            self.cursor,
                            sql_str,
                            self._quote_params(params),
                        ),
                        "duration": "{0} ms".format(floor(duration)),
                        "raw_sql": sql_str,
                        "params": serialized_params,
                        "raw_params": params,
                        "start_time": start_time,
                        "stop_time": stop_time,
                        "is_select": sql_str.lower()
                        .strip()
                        .startswith("select"),
                        "encoding": conn.encoding,
                        "trans_status": conn.get_transaction_status(),
                    },
                )
