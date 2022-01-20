def wrap_cursor(connection):
    """Wrap cursor for logging sql queries."""
    if not hasattr(connection, "_logged_cursor"):  # noqa: WPS421
        connection._logged_cursor = connection.cursor
        connection._logged_chunked_cursor = connection.chunked_cursor
        connection.queries_count = 0

        def cursor(*args, **kwargs):  # noqa: WPS430
            # Per the DB API cursor() does not accept any arguments. There"s
            # some code in the wild which does not follow that convention,
            # so we pass on the arguments even though it"s not clean.
            # See:
            # https://github.com/jazzband/django-debug-toolbar/pull/615
            # https://github.com/jazzband/django-debug-toolbar/pull/896
            return NormalCursorWrapper(
                connection._logged_cursor(*args, **kwargs),
                connection,
            )

        def chunked_cursor(*args, **kwargs):  # noqa: WPS430
            return NormalCursorWrapper(
                connection._logged_chunked_cursor(*args, **kwargs),
                connection,
            )

        connection.cursor = cursor
        connection.chunked_cursor = chunked_cursor
        return cursor


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

    def __getattr__(self, attr):
        return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def _record(self, method, sql, params):
        self.db.queries_count += 1
        return method(sql, params)
