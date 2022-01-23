import sqlite3
from collections import namedtuple, deque
from io import StringIO
import weakref
import re
import logging


logger = logging.getLogger(__name__)


class RowIterator:
    """An iterator over the rows in a view or table. 
    Never instantiate this directly, created by iterating over a Table object.
    
    Attributes:
        column_names (list(str)): The names of the columns in the table or view.
        Row (class): The :py:class:`collections.namedtuple` class used for representing the rows.
        
    """
    def __init__(self, statement, table):
        self.statement = statement
        self.active = True
        self.table = table
        cur = table.db._execute_query(statement, cursor_type="server")
        self._cur = cur
        self.column_names = [x[0] for x in cur.description]
        self.Row = namedtuple("Row", self.column_names, rename=True)

    def __iter__(self):
        return self
        
    def __next__(self):
        if not self.active:
            raise StopIteration        
        try:
            return self.Row._make(next(self._cur))
        except StopIteration:
            self.close()
            raise

    def close(self):
        self._cur.close()
        self.active = False
        self.table.db._garbage_collect()
        
    def __del__(self):
        if hasattr(self, "_cur"):
            self._cur.close()
        else:
            logger.debug(f"In __del__ of {self!r}:{self.statement}: _cur attribute uninitialized")

class Table:
    """Represents a table or view. 
    Returned by :py:meth:`Database.query`, :py:meth:`Table.view` or :py:meth:`Table.table`. Not to be instantiated directly.
    
    """
    def __init__(self, name, db):
        self.name = name
        self.db = db
        self.bindings = None

    def view(self, select_stmt, *, bindings={}):
        """Create a new view by running a SQL select statement.
        
        Args:
            select_stmt (str): SQL select statement. The special table name `_` 
                (underscore) represents the table associated with `self`.
            bindings (dict(str, Table)): Additional tables to be made accessible
                in the SQL statement.
                
        Returns:
            Table: A new table object representing the result of the query.
                
        """
        return self.db.query(select_stmt, kind="view", bindings=dict(_=self, **bindings))

    def table(self, select_stmt=None, parameters=None, *, bindings={}):
        """Create a new view by running a SQL select statement.
        
        Args:
            select_stmt (str): SQL select statement. The special table name `_` 
                (underscore) represents the table associated with `self`. If `None`,
                defaults to `select * from _`.
            parameters (list or dict): Values for SQL query parameters
            bindings (dict(str, Table)): Additional tables to be made accessible
                in the SQL statement.
                
        Returns:
            Table: A new table object representing the result of the query.

        """

        if select_stmt is None:
            select_stmt = "select * from _"
        return self.db.query(select_stmt, kind="table", parameters=parameters, bindings=dict(_=self, **bindings))
    
    def insert(self, values):
        self.db._insert_values(self, values)

    def __iter__(self):
        """Iterate over the rows from this table.
        
        Returns:
            RowIterator: An iterator over the rows in this table.
            
        """
        return self.db._iterate(self)

    def _repr_markdown_(self, limit=16):
        ascii_punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
        def q(x):
            return "".join("\\" + c if c in ascii_punctuation else c for c in x)
        out = StringIO()
        it = iter(self.view(f"select * from _ limit {limit+1}"))
        out.write("|" + "|".join(q(x) for x in it.column_names) + "|\n")
        out.write("|" + "|".join("-" for _ in it.column_names) + "|\n")
        for i,row in enumerate(it):
            if i < limit:
                data = [q(f"{x!r}") for x in row]
            else:
                data = ["..." for _ in row]
            out.write("|" + "|".join(data) + "|\n")
        return out.getvalue()
