#!/usr/bin/env python3
"""
Sub-Package DBTOOLS of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package implements a simplified interface for
working with the Python DB API.
"""

import os
from collections import defaultdict, OrderedDict
from functools import partial, wraps

try:
    from plib.stdlib.coll import namedtuple, typed_namedtuple
except ImportError:
    from collections import namedtuple
    typed_namedtuple = None

try:
    import yaml
except ImportError:
    yaml = None


__version__ = "1.3"


def maybe(t, null_values=None, null_fields=None,
          null_default_values=(None,), null_default_fields={bool: False, int: 0, str: "", bytes: b"", float: 0.0}):
    
    def _f(v):
        if v in (null_values or null_default_values):
            return (null_fields or null_default_fields)[t]
        return t(v)
    _f.__name__ = 'maybe_{0}'.format(t.__name__)
    return _f


def smart_type(fieldtype, null_values=None, null_fields=None, use_unicode=False):
    return maybe(
        bool if 'bool' in fieldtype else
        int if 'int' in fieldtype else
        float if any (t in fieldtype for t in ('float', 'double', 'decimal')) else
        str if use_unicode else
        bytes,
        null_values, null_fields
    )


def cursor_method(f):
    @wraps(f)
    def _m(self, *args, **kwargs):
        # This forces a new transaction on the connection, which ensures
        # that queries don't return stale results
        if self.auto_refresh:
            self.commit()
        # Don't have to include cursor in method calls, it automatically
        # gets bound, similar to self
        return f(self, self.cursor, *args, **kwargs)
    return _m


class DBInterface(object):
    """Make it easier to work with database.
    """
    
    param_strings = {
        'qmark': "?",
        'format': "%s"
    }
    
    db_mod = None
    paramstr = ""  # non-supported paramstyle will raise exception on any SQL with params
    
    conn_methods = ('commit', 'rollback')
    
    auto_refresh = True  # commit before each cursor method call to ensure fresh results
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        if self.db_mod:
            self.paramstr = self.param_strings.get(self.db_mod.paramstyle, self.paramstr)
        
        self.conn = self._get_connection(*args, **kwargs)
        self._cur = self.conn.cursor()
        
        for method in self.conn_methods:
            setattr(self, method, getattr(self.conn, method))
    
    def __del__(self):
        self.close()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    @property
    def cursor(self):
        # For convenience and use in cursor_method decorator
        return self._cur
    
    def _get_connection(self, *args, **kwargs):
        raise NotImplementedError
    
    def _get_fieldspec(self, field):
        raise NotImplementedError
    
    def get_fieldspecs(self, fields):
        return ', '.join(
            self._get_fieldspec(field) for field in fields
        )
    
    tables_sql = None
    tables_index = None
    
    @cursor_method
    def get_tables(self, cursor):
        cursor.execute(self.tables_sql)
        return [row[self.tables_index] for row in cursor.fetchall()]
    
    fields_sql = None
    fields_iter = None
    
    def _get_fieldvalue(self, row):
        raise NotImplementedError
    
    def _get_tablename(self, row):
        raise NotImplementedError
    
    def _get_fieldvalues(self, row):
        raise NotImplementedError
    
    @cursor_method
    def get_fieldmap(self, cursor):
        if self.fields_iter:
            result = {}
            for tablename in self.get_tables():
                sql = self.fields_sql.format(tablename)
                cursor.execute(sql)
                rows = cursor.fetchall()
                result[tablename] = [self._get_fieldvalue(row) for row in rows]
        else:
            sql = self.fields_sql
            cursor.execute(sql)
            rows = cursor.fetchall()
            result = {self._get_tablename(row): self._get_fieldvalues(row) for row in rows}
        return result
    
    def get_map_fields(self, tablename):
        fmap = self.get_fieldmap()
        return (
            fmap[tablename] if isinstance(tablename, str) else
                # Use OrderedDict here so that fields common to multiple tables appear
                # where they are first encountered
                list(OrderedDict(
                (fieldname, None)
                for table in tablename
                for fieldname in fmap[table]
            ).keys())
        )
    
    index_sql = None
    
    @cursor_method
    def get_indexes(self, cursor):
        result = {}
        for tablename in self.get_tables():
            sql = self.index_sql.format(tablename)
            cursor.execute(sql)
            result[tablename] = cursor.fetchall()
        return result
    
    db_structure = None
    
    @classmethod
    def get_tablespecs(cls, tablename):
        tables = cls.db_structure['tables']
        return (
            tables[tablename] if isinstance(tablename, str) else
            list(OrderedDict(
                (fieldspec, None)
                for table in tablename
                for fieldspec in tables[table]
            ).keys())
        )
    
    @classmethod
    def get_fields(cls, tablename):
        return [fieldspec.split(' ')[0] for fieldspec in cls.get_tablespecs(tablename)]
    
    @classmethod
    def get_fieldtypes(cls, tablename):
        return [fieldspec.split(' ')[1] for fieldspec in cls.get_tablespecs(tablename)]
    
    null_values = null_fields = None
    use_unicode = False
    
    @classmethod
    def get_tuple(cls, tablename, untyped=False):
        tuple_name = tablename if isinstance(tablename, str) else '_'.join(tablename)
        if untyped:
            return namedtuple(tuple_name, tuple(cls.get_fields(tablename)))
        if typed_namedtuple is not None:
            return typed_namedtuple(
                tuple_name,
                tuple(
                    (fieldname, smart_type(fieldtype, cls.null_values, cls.null_fields, cls.use_unicode))
                    for fieldname, fieldtype in zip(cls.get_fields(tablename), cls.get_fieldtypes(tablename))
                )
            )
        raise RuntimeError("typed_namedtuple not available")
    
    @cursor_method
    def clear_table(self, cursor, tablename, commit=True, verbose=True):
        if verbose:
            print("Dropping table {0}...".format(tablename))
        result = cursor.execute("DROP TABLE {0};".format(tablename))
        if commit:
            self.commit()
        return result
    
    def clear_tables(self, commit=True, verbose=True):
        results = []
        if verbose:
            print("Clearing tables...")
        for tablename in self.get_tables():
            results.append(self.clear_table(tablename, commit=False, verbose=verbose))
        if commit:
            self.commit()
        if verbose:
            print("Clear tables complete.")
        return results
    
    @classmethod
    def get_table_fields(cls, tablename):
        return cls.db_structure['tables'][tablename]
    
    def _table_sql(self, tablename, fields):
        raise NotImplementedError
    
    @cursor_method
    def create_table(self, cursor, tablename, fields=None, commit=True, verbose=True):
        if fields is None:
            fields = self.get_table_fields(tablename)
        fieldspecs = self.get_fieldspecs(fields)
        sql = self._table_sql(tablename, fieldspecs)
        if verbose:
            print(sql)
        result = cursor.execute(sql)
        if commit:
            self.commit()
        return result
    
    def create_tables(self, clear=False, commit=True, verbose=True):
        results = []
        if clear:
            self.clear_tables()
        existing_tables = self.get_tables()
        tables = self.db_structure['tables']
        if all(tablename in existing_tables for tablename in tables):
            if verbose:
                print("Tables already created.")
            return None
        if any(tablename in existing_tables for tablename in tables):
            if verbose:
                print("Tables partially created, aborting!")
            return False
        if verbose:
            print("Creating tables...")
        for tablename, fields in tables.items():
            results.append(self.create_table(tablename, fields, commit=False, verbose=verbose))
        if commit:
            self.commit()
        if verbose:
            print("Table creation complete.")
        return results
    
    def _index_sql(self, tablename, column_str, primary=False):
        raise NotImplementedError
    
    @cursor_method
    def create_index(self, cursor, tablename, columns, primary=False, commit=True, verbose=True):
        column_str = columns if isinstance(columns, str) else ", ".join(columns)
        sql = self._index_sql(tablename, column_str, primary)
        if not sql:
            return None
        if verbose:
            print(sql)
        result = cursor.execute(sql)
        if commit:
            self.commit()
        return result
    
    def _create_indexes(self, index_map, primary, commit=True, verbose=True):
        results = []
        for tablename, indexspec in index_map.items():
            indexes = (indexspec,) if isinstance(indexspec, str) else indexspec
            for columns in indexes:
                results.append(self.create_index(tablename, columns, primary=primary, commit=False, verbose=verbose))
        if commit:
            self.commit()
        return results
    
    def create_keys(self, commit=True, verbose=True):
        index_map = self.db_structure['keys']
        results = self._create_indexes(index_map, primary=True, commit=commit, verbose=verbose)
        if verbose and any(results):
            print("Primary key creation complete.")
        return results
    
    def create_indexes(self, commit=True, verbose=True):
        index_map = self.db_structure['indexes']
        results = self._create_indexes(index_map, primary=False, commit=commit, verbose=verbose)
        if verbose:
            print("Index creation complete.")
        return results
    
    def _get_sql_values(self, values):
        return ", ".join(self.paramstr for _ in range(len(values)))
    
    @cursor_method
    def add_row(self, cursor, tablename, values, commit=True, verbose=True):
        sql_values = self._get_sql_values(values)
        sql = "INSERT INTO {0} VALUES({1});".format(
            tablename,
            sql_values
        )
        if verbose:
            print(sql, values)
        result = cursor.execute(sql, values)
        if commit:
            self.commit()
        return result
    
    def add_rows(self, tablename, valuelist, commit=True, verbose=True):
        results = []
        if verbose:
            print("Adding rows to {0}...".format(tablename))
        for values in valuelist:
            results.append(self.add_row(tablename, values, commit=False, verbose=verbose))
        if commit:
            self.commit()
        if verbose:
            print("{0}: rows added.".format(tablename.capitalize()))
        return results
    
    @staticmethod
    def _parse_keymap(keymap,
                        ops=('>=', '<=', '!=', '>', '<'), orders={'+': " ASC", '-': " DESC", '*': ""},
                        in_ops={'=': ' IN ', '!=': ' NOT IN '}):
        
        fields = []
        values = []
        order_field = None
        order_spec = None
        for key, value in keymap.items():
            op = first(o for o in ops if key.endswith(o))
            if op:
                key = key[:-len(op)]
            else:
                op = '='
            order = first(s for s in orders if key.startswith(s))
            if order:
                key = key[len(order):]
                order_field = key
                order_spec = orders[order]
            if value is not None:
                if isinstance(value, (tuple, list)):
                    if op not in in_ops:
                        raise ValueError("Invalid operator for SQL IN clause: " + op)
                    op = in_ops[op]
                    num = len(value)
                    values.extend(value)
                else:
                    num = None
                    values.append(value)
                fields.append((op, key, num))
        return fields, order_field, order_spec, values
    
    def _numstr(self, num):
        if num:
            return "({})".format(", ".join([self.paramstr] * num))
        return self.paramstr
    
    def _get_sql_where(self, keymap):
        limit = keymap.pop('_limit', None)
        fields, order_field, order_spec, values = self._parse_keymap(keymap)
        return (
            "{0}{1}{2}{3}".format(
                " WHERE " if fields else "",  # the next clause will also be an empty string if no fields
                " AND ".join("{0}{1}{2}".format(field, op, self._numstr(num)) for op, field, num in fields),
                " ORDER BY {0}{1}".format(order_field, order_spec) if order_field else "",
                " LIMIT {0}".format(limit) if limit is not None else ""
            ),
            tuple(values)
        )
    
    def _get_sql_set(self, valuemap):
        return (
            ", ".join("{0}={1}".format(field, self.paramstr) for field in valuemap.keys()),
            tuple(valuemap.values())
        )
    
    @cursor_method
    def update_row(self, cursor, tablename, keymap, valuemap, commit=True, verbose=True):
        if not (keymap and valuemap):
            return  # makes it easier to feed value sequences to update_rows
        sql_where, keys = self._get_sql_where(keymap)
        sql_set, values = self._get_sql_set(valuemap)
        sql = "UPDATE {0} SET {1}{2};".format(
            tablename,
            sql_set,
            sql_where
        )
        args = values + keys
        if verbose:
            print(sql, args)
        result = cursor.execute(sql, args)
        if commit:
            self.commit()
        return result
    
    def update_rows(self, tablename, values, commit=True, verbose=True):
        results = []
        if verbose:
            print("Updating {0}...".format(tablename))
        for keymap, valuemap in values:
            results.append(self.update_row(tablename, keymap, valuemap, commit=False, verbose=verbose))
        if commit:
            self.commit()
        if verbose:
            print("{0} updated.".format(tablename.capitalize()))
        return results
    
    def _get_tablespec(self, tablename, include_nomatch):
        return (
            tablename if isinstance(tablename, str) else
            # assume tablename is iterable
            " {0} JOIN ".format("NATURAL LEFT" if include_nomatch else "NATURAL").join(tablename)
        )
    
    @cursor_method
    def get_rows(self, cursor, tablename, keymap=None, fields=None, use_structure=True, include_nomatch=False, verbose=True):
        sql_where, keys = self._get_sql_where(keymap) if keymap else ("", None)
        if verbose:
            print("Querying {0}...".format(tablename))
        sql = "SELECT {0} FROM {1}{2};".format(
            fields if isinstance(fields, str) else ", ".join(
                fields or (self.get_fields if use_structure else self.get_map_fields)(tablename)
            ),
            self._get_tablespec(tablename, include_nomatch),
            sql_where
        )
        if verbose:
            if keys:
                print(sql, keys)
            else:
                print(sql)
        if keys:
            cursor.execute(sql, keys)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    
    def query(self, tablename, keymap=None, include_nomatch=False, untyped=False, verbose=True):
        rows = self.get_rows(tablename, keymap, include_nomatch=include_nomatch, verbose=verbose)
        t = self.get_tuple(tablename, untyped=untyped)
        return [t(*row) for row in rows]
    
    def match(self, tablename, keymap=None, include_nomatch=False, raise_mismatch=False, untyped=False, verbose=True):
        rows = self.query(tablename, keymap, include_nomatch=include_nomatch, untyped=untyped, verbose=verbose)
        if len(rows) == 1:
            return rows[0]
        if raise_mismatch:
            raise RuntimeError("{0} row matching keys: {1}".format(
                "More than one" if rows else "No",
                repr(keymap)
            ))
    
    @cursor_method
    def delete_rows(self, cursor, tablename, keymap=None, commit=True, verbose=True):
        sql_where, keys = self._get_sql_where(keymap) if keymap else ("", None)
        if verbose:
            print("Deleting from {0}...".format(tablename))
        sql = "DELETE FROM {0}{1};".format(
            tablename,
            sql_where
        )
        if verbose:
            if keys:
                print(sql, keys)
            else:
                print(sql)
        if keys:
            result = cursor.execute(sql, keys)
        else:
            result = cursor.execute(sql)
        if commit:
            self.commit()
        return result
    
    def dump_table(self, tablename, use_structure=True, as_dict=False, verbose=True):
        if verbose:
            print("Dumping", tablename)
        result = self.get_rows(tablename, use_structure=use_structure)
        if as_dict:
            fields = (self.get_fields if use_structure else self.get_map_fields)(tablename)
            return [
                dict(zip(fields, row))
                for row in result
            ]
        return result
    
    def _get_included_tables(self, tables, exclude_tables):
        if exclude_tables and not tables:
            tables = self.get_tables()
            for t in exclude_tables:
                tables.remove(t)
        return tables
    
    def dump(self, tables=None, exclude_tables=None, use_structure=True, as_dict=False, verbose=True):
        tables = self._get_included_tables(tables, exclude_tables)
        return dict(
            (tablename, self.dump_table(tablename, use_structure=use_structure, as_dict=as_dict, verbose=verbose))
            for tablename in (tables or self.get_tables())
        )
    
    def load_table(self, tablename, rows, as_dict=False, clear=True, verbose=True):
        if clear:
            self.clear_table(tablename, commit=False, verbose=verbose)
            self.create_table(tablename, commit=False, verbose=verbose)
            self.create_keys(tablename, commit=False, verbose=verbose)
            self.create_indexes(tablename, commit=False, verbose=verbose)
            self.commit()
        if verbose:
            print("Loading", tablename)
        t = self.get_tuple(tablename)
        _init = partial(t.from_dict, plain=True) if as_dict else t.from_iterable
        return self.add_rows(tablename,
            [_init(d) for d in rows],
            verbose=verbose)
    
    def load(self, data, tables=None, exclude_tables=None, as_dict=False, clear=True, verbose=True):
        results = defaultdict(list)
        tables = self._get_included_tables(tables, exclude_tables)
        if clear:
            for tablename in (tables or data.keys()):
                results[tablename].append(self.clear_table(tablename, commit=False, verbose=verbose))
                results[tablename].append(self.create_table(tablename, commit=False, verbose=verbose))
                results[tablename].append(self.create_keys(tablename, commit=False, verbose=verbose))
                results[tablename].append(self.create_indexes(tablename, commit=False, verbose=verbose))
            self.commit()
        for tablename in (tables or data.keys()):
            rows = data.get(tablename)
            if rows:
                results[tablename].append(self.load_table(tablename, rows, as_dict=as_dict, clear=False, verbose=verbose))
        return results


DB_SQLITE3 = 1
DB_MYSQL = 2


def get_db_interface_class(dbname, dbtype, structure, params):
    if dbtype is DB_SQLITE3:
        from plib.dbtools.sqlite import SQLite3DBInterface
        intf_class = SQLite3DBInterface
    elif dbtype is DB_MYSQL:
        from plib.dbtools.mysql import MySQLDBInterface
        intf_class = MySQLDBInterface
    else:
        raise RuntimeError("Invalid database type: {0}".format(repr(dbtype)))
    
    if isinstance(structure, str):
        if yaml:
            structure = yaml.load(structure)
        else:
            raise RuntimeError("Database structure definition must be a dictionary.")
    
    return type(intf_class)(
        '{0}DBInterface'.format(dbname) if dbname else intf_class.__name__,
        (intf_class,),
        dict(
            db_structure=structure,
            **(params or {})
        )
    )


def get_db_interface_args(dbname, dbtype, argpath, kwds):
    kwargs = {}
    if dbtype is DB_SQLITE3:
        args = (os.path.join(argpath, "{0}.db".format(dbname.lower())),)
    elif dbtype is DB_MYSQL:
        args = ()
        kwargs.update(
            (kwds or {}),
            use_unicode=True,
            charset='utf8'  # no hyphen for MySQL, unlike Python, HTML, etc., etc... :p
        )
    else:
        raise RuntimeError("Invalid database type: {0}".format(repr(dbtype)))
    return args, kwargs


def get_db_interface(dbname, dbtype, structure, params, argpath, kwds):
    klass = get_db_interface_class(dbname, dbtype, structure, params)
    args, kwargs = get_db_interface_args(dbname, dbtype, argpath, kwds)
    return klass(*args, **kwargs)
