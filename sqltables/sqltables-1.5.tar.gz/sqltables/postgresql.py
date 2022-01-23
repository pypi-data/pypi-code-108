from contextlib import contextmanager
import io
import psycopg2
from . import generic

class Database (generic.Database):
    """Connection to a PostgreSQL database.

    Args:
        name: Name of the database, passed to :py:func:`psycopg2.connect`.

    """
    
    def __init__(self, name):
        conn = psycopg2.connect(name)
        super().__init__(conn)
        self.name = name
        self.value_placeholder = "%s"
        self._in_transaction = False

    @contextmanager
    def _transaction(self):
        if self._in_transaction:
            yield None
        else:
            self._in_transaction = True
            try:
                with self._conn:
                    yield None
            finally:
                self._in_transaction = False
        
    def _cursor(self, cursor_type):
        if cursor_type == "client":
            return self._conn.cursor()
        elif cursor_type == "server":
            cursor_name = self._generate_temp_name(prefix="cursor")
            return self._conn.cursor(name=cursor_name, withhold=True)
        else:
            raise ValueError(f"Invalid cursor type: {cursor_type!r}")

    def _execute_query(self, statement, parameters=None, cursor_type="client"):
        cur = self._execute(statement, parameters, cursor_type=cursor_type)
        if cursor_type == "server":
            cur.fetchmany(0) # Force PostgreSQL to populate cur.description
        return cur

    def _insert_values(self, table, values, column_names=None):
        def quote_copy_text(value):
            if value is None:
                return r"\N"
            return (str(value)
                    .replace("\\", "\\\\")
                    .replace("\t", r"\t")
                    .replace("\n", r"\n")
                    .replace("\r", r"\r"))

        def encode_rows(rows):
            buf = io.StringIO()
            for row in rows:
                buf.write("\t".join(quote_copy_text(x) for x in row))
                buf.write("\n")
            buf.seek(0)
            return buf
        
        buf = encode_rows(values)
        # quoted_name = self.quote_name(table.name)
        # FIXME: behaviour changed in psycopg 2.9, need to use copy_expert to allow schema and consistent behaviour
        quoted_name = table.name
        with self._transaction():
            cursor = self._conn.cursor()
            try:
                cursor.copy_from(buf, quoted_name)
            finally:
                cursor.close()


