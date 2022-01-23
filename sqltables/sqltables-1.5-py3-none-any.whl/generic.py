from collections import namedtuple, deque
import weakref
import re
import logging

from .sqltables import Table, RowIterator

logger = logging.getLogger(__name__)


# We are forced to implement a garbage collection mechanism in Database since
# "Attempting to DROP a table gets an SQLITE_LOCKED error if there are any active statements
# belonging to the same database connection"
# https://sqlite.org/forum/forumpost/433d2fdb07?raw
class Database:
    """Connection to a Generic SQL database.

    Args:
        conn: DB-API 2.0 connection object

    """
    
    def __init__(self, conn):
        self._conn = conn
        self._next_temp_id = 0
        self._active_iterators = weakref.WeakSet()
        self._gc_statements = deque()
        self.default_column_type = "text"
        self.value_placeholder = "?"
        self.temporary_prefix = "temp_"
        self.temporary_modifier = "temporary"

    def _generate_temp_name(self, prefix=None):
        if prefix is None:
            prefix = self.temporary_prefix
        name = f"{prefix}{self._next_temp_id}"
        self._next_temp_id += 1
        return name

    def quote_name(self, name):
        return ".".join(['"' + part.replace('"', '""') + '"' for part in name.split(".")])

    def _transaction(self):
        return self._conn
    
    def _cursor(self, cursor_type):
        return self._conn.cursor()

    def _execute_query(self, *args, **kwargs):
        return self._execute(*args, **kwargs)

    def _execute(self, statement, parameters=None, cursor_type="client"):
        with self._transaction():
            cursor = self._cursor(cursor_type)
            try:
                if parameters is not None:
                    logger.debug(f"[{self!r}] Executing {statement!r} with parameters {parameters!r}")
                    cursor.execute(statement, parameters)
                else:
                    logger.debug(f"[{self!r}] Executing {statement!r}")
                    cursor.execute(statement)
            except:
                cursor.close()
                raise
            return cursor

    def _iterate(self, table):
        statement = f"select * from {table.name}"
        result_iterator = RowIterator(statement, table)
        self._active_iterators.add(result_iterator)
        weakref.finalize(result_iterator, self._garbage_collect)
        return result_iterator

    def _drop(self, statement):
        self.execute(statement)

    def _garbage_collect(self):
        self._active_iterators = weakref.WeakSet(x for x in self._active_iterators if x.active)
        if not self._active_iterators and self._gc_statements:
            logger.debug(f"[{self!r}] Starting GC on database {self.name!r} {self!r}")            
            while self._gc_statements:
                statement = self._gc_statements.popleft()
                self.execute(statement)
    
    def query(self, select_stmt, kind="view", parameters=None, bindings={}):
        """Execute an SQL select statement.

        Args:
            select_stmt (str): The SQL select statement to execute. 
                Does not support "with" clauses.
            kind (str): The underlying temporary object to create. Either "view" 
                or "table".
            parameters (list or dict): Query parameters for the SQL statement.
                Only supported if kind is "table"
            bindings (dict(str, Table)): For each key name, make the table available within
                the query as name.
            
        Returns:
            Table: A Table object that represents the result of the query
            
            
        """
        if re.match(r"\s*with\b", select_stmt):
            raise ValueError("sqltables: with clause not supported in query, please use the bindings parameter instead")
        preamble = []
        with_clauses = [
            f"{name} as (select * from {table.name})"
            for name, table in bindings.items() if table.name is not None
        ]
        with_stmt = "with " + ", ".join(with_clauses) if with_clauses else ""
        result_name = self._generate_temp_name()
        statement = f"create {self.temporary_modifier} {kind} {result_name} as {with_stmt} {select_stmt}"
        self.execute(statement, parameters)
        result = Table(name=result_name, db=self)
        result.bindings = bindings
        weakref.finalize(result, self._drop, f"drop {kind} {result_name}")
        return result

    def execute(self, statement, parameters=None):
        cur = self._execute(statement, parameters)
        cur.close()

    def create_table(self, rows=None, column_names=[], column_types={}, name=None):
        """Create a new table.
        
        Args:
            values (iterable(sequence)): The values to insert into the new table, as
                an iterable of rows.
            column_names (list(str)): The column names of the new table.
            column_types (dict(str, str)): Data types for the columns. Note that SQLite mostly uses 
                column types for documentation purposes.
            name (str): The name of the table inside the database. The default value 
                `None` causes a name to be automatically generated.
                
        Returns:
            Table: A new Table object that can be used to manipulate the created table.
        """
        is_temporary = True
        temporary = self.temporary_modifier
        if name is None:
            name = self._generate_temp_name()
        else:
            temporary = ""
            is_temporary = False
        quoted_column_names = ['"' + n.replace('"', '""') + '"' 
                               for n in column_names]
        column_spec = ",".join([f'{q} {column_types.get(x, self.default_column_type)}' for q,x in zip(quoted_column_names, column_names)])
        with self._transaction():
            self.execute(f"create {temporary} table {name} ({column_spec})")
            result = Table(name=name, db=self)
            if rows is not None:
                self._insert_values(result, rows, column_names=column_names)
        if is_temporary:
            weakref.finalize(result, self._drop, f"drop table {name}")
        return result

    def open_table(self, name):
        return Table(name=name, db=self)
    
    # Deprecated, use create_table instead
    def load_values(self, values, *, column_names, name=None):
        return self.create_table(rows=values, column_names=column_names, name=name)
    
    def drop_table(self, table_name):
        """Drop a table from the database.
        
        Args:
            table_name: The name of the table to drop.
        """
        quoted_name = self.quote_name(table_name)
        self.execute(f"drop table {quoted_name}")

    def close(self):
        self._conn.close()
        
    def _insert_values(self, table, values, column_names=None):
        if column_names is None:
            it = iter(table)
            column_names = it.column_names
            it.close()
        name = self.quote_name(table.name)
        with self._transaction():
            cursor = self._cursor("client")
            try:
                if isinstance(values, Table):
                    values_name = self.quote_name(values.name)
                    cursor.execute(f"insert into {name} select * from {values_name}")
                else:
                    value_spec = ",".join(self.value_placeholder for _ in column_names)            
                    cursor.executemany(f"insert into {name} values ({value_spec})", values)
            finally:
                cursor.close()
