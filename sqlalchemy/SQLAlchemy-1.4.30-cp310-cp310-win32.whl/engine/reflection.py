# engine/reflection.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""Provides an abstraction for obtaining database schema information.

Usage Notes:

Here are some general conventions when accessing the low level inspector
methods such as get_table_names, get_columns, etc.

1. Inspector methods return lists of dicts in most cases for the following
   reasons:

   * They're both standard types that can be serialized.
   * Using a dict instead of a tuple allows easy expansion of attributes.
   * Using a list for the outer structure maintains order and is easy to work
     with (e.g. list comprehension [d['name'] for d in cols]).

2. Records that contain a name, such as the column name in a column record
   use the key 'name'. So for most return values, each record will have a
   'name' attribute..
"""

import contextlib

from .base import Connectable
from .base import Connection
from .base import Engine
from .. import exc
from .. import inspection
from .. import sql
from .. import util
from ..sql import operators
from ..sql import schema as sa_schema
from ..sql.type_api import TypeEngine
from ..util import topological


@util.decorator
def cache(fn, self, con, *args, **kw):
    info_cache = kw.get("info_cache", None)
    if info_cache is None:
        return fn(self, con, *args, **kw)
    key = (
        fn.__name__,
        tuple(a for a in args if isinstance(a, util.string_types)),
        tuple((k, v) for k, v in kw.items() if k != "info_cache"),
    )
    ret = info_cache.get(key)
    if ret is None:
        ret = fn(self, con, *args, **kw)
        info_cache[key] = ret
    return ret


@inspection._self_inspects
class Inspector(object):
    """Performs database schema inspection.

    The Inspector acts as a proxy to the reflection methods of the
    :class:`~sqlalchemy.engine.interfaces.Dialect`, providing a
    consistent interface as well as caching support for previously
    fetched metadata.

    A :class:`_reflection.Inspector` object is usually created via the
    :func:`_sa.inspect` function, which may be passed an
    :class:`_engine.Engine`
    or a :class:`_engine.Connection`::

        from sqlalchemy import inspect, create_engine
        engine = create_engine('...')
        insp = inspect(engine)

    Where above, the :class:`~sqlalchemy.engine.interfaces.Dialect` associated
    with the engine may opt to return an :class:`_reflection.Inspector`
    subclass that
    provides additional methods specific to the dialect's target database.

    """

    @util.deprecated(
        "1.4",
        "The __init__() method on :class:`_reflection.Inspector` "
        "is deprecated and "
        "will be removed in a future release.  Please use the "
        ":func:`.sqlalchemy.inspect` "
        "function on an :class:`_engine.Engine` or "
        ":class:`_engine.Connection` "
        "in order to "
        "acquire an :class:`_reflection.Inspector`.",
    )
    def __init__(self, bind):
        """Initialize a new :class:`_reflection.Inspector`.

        :param bind: a :class:`~sqlalchemy.engine.Connectable`,
          which is typically an instance of
          :class:`~sqlalchemy.engine.Engine` or
          :class:`~sqlalchemy.engine.Connection`.

        For a dialect-specific instance of :class:`_reflection.Inspector`, see
        :meth:`_reflection.Inspector.from_engine`

        """
        return self._init_legacy(bind)

    @classmethod
    def _construct(cls, init, bind):

        if hasattr(bind.dialect, "inspector"):
            cls = bind.dialect.inspector

        self = cls.__new__(cls)
        init(self, bind)
        return self

    def _init_legacy(self, bind):
        if hasattr(bind, "exec_driver_sql"):
            self._init_connection(bind)
        else:
            self._init_engine(bind)

    def _init_engine(self, engine):
        self.bind = self.engine = engine
        engine.connect().close()
        self._op_context_requires_connect = True
        self.dialect = self.engine.dialect
        self.info_cache = {}

    def _init_connection(self, connection):
        self.bind = connection
        self.engine = connection.engine
        self._op_context_requires_connect = False
        self.dialect = self.engine.dialect
        self.info_cache = {}

    @classmethod
    @util.deprecated(
        "1.4",
        "The from_engine() method on :class:`_reflection.Inspector` "
        "is deprecated and "
        "will be removed in a future release.  Please use the "
        ":func:`.sqlalchemy.inspect` "
        "function on an :class:`_engine.Engine` or "
        ":class:`_engine.Connection` "
        "in order to "
        "acquire an :class:`_reflection.Inspector`.",
    )
    def from_engine(cls, bind):
        """Construct a new dialect-specific Inspector object from the given
        engine or connection.

        :param bind: a :class:`~sqlalchemy.engine.Connectable`,
          which is typically an instance of
          :class:`~sqlalchemy.engine.Engine` or
          :class:`~sqlalchemy.engine.Connection`.

        This method differs from direct a direct constructor call of
        :class:`_reflection.Inspector` in that the
        :class:`~sqlalchemy.engine.interfaces.Dialect` is given a chance to
        provide a dialect-specific :class:`_reflection.Inspector` instance,
        which may
        provide additional methods.

        See the example at :class:`_reflection.Inspector`.

        """
        return cls._construct(cls._init_legacy, bind)

    @inspection._inspects(Connectable)
    def _connectable_insp(bind):
        # this method should not be used unless some unusual case
        # has subclassed "Connectable"

        return Inspector._construct(Inspector._init_legacy, bind)

    @inspection._inspects(Engine)
    def _engine_insp(bind):
        return Inspector._construct(Inspector._init_engine, bind)

    @inspection._inspects(Connection)
    def _connection_insp(bind):
        return Inspector._construct(Inspector._init_connection, bind)

    @contextlib.contextmanager
    def _operation_context(self):
        """Return a context that optimizes for multiple operations on a single
        transaction.

        This essentially allows connect()/close() to be called if we detected
        that we're against an :class:`_engine.Engine` and not a
        :class:`_engine.Connection`.

        """
        if self._op_context_requires_connect:
            conn = self.bind.connect()
        else:
            conn = self.bind
        try:
            yield conn
        finally:
            if self._op_context_requires_connect:
                conn.close()

    @contextlib.contextmanager
    def _inspection_context(self):
        """Return an :class:`_reflection.Inspector`
        from this one that will run all
        operations on a single connection.

        """

        with self._operation_context() as conn:
            sub_insp = self._construct(self.__class__._init_connection, conn)
            sub_insp.info_cache = self.info_cache
            yield sub_insp

    @property
    def default_schema_name(self):
        """Return the default schema name presented by the dialect
        for the current engine's database user.

        E.g. this is typically ``public`` for PostgreSQL and ``dbo``
        for SQL Server.

        """
        return self.dialect.default_schema_name

    def get_schema_names(self):
        """Return all schema names."""

        if hasattr(self.dialect, "get_schema_names"):
            with self._operation_context() as conn:
                return self.dialect.get_schema_names(
                    conn, info_cache=self.info_cache
                )
        return []

    def get_table_names(self, schema=None):
        """Return all table names in referred to within a particular schema.

        The names are expected to be real tables only, not views.
        Views are instead returned using the
        :meth:`_reflection.Inspector.get_view_names`
        method.


        :param schema: Schema name. If ``schema`` is left at ``None``, the
         database's default schema is
         used, else the named schema is searched.  If the database does not
         support named schemas, behavior is undefined if ``schema`` is not
         passed as ``None``.  For special quoting, use :class:`.quoted_name`.

        .. seealso::

            :meth:`_reflection.Inspector.get_sorted_table_and_fkc_names`

            :attr:`_schema.MetaData.sorted_tables`

        """

        with self._operation_context() as conn:
            return self.dialect.get_table_names(
                conn, schema, info_cache=self.info_cache
            )

    def has_table(self, table_name, schema=None):
        """Return True if the backend has a table of the given name.


        :param table_name: name of the table to check
        :param schema: schema name to query, if not the default schema.

        .. versionadded:: 1.4 - the :meth:`.Inspector.has_table` method
           replaces the :meth:`_engine.Engine.has_table` method.

        """
        # TODO: info_cache?
        with self._operation_context() as conn:
            return self.dialect.has_table(conn, table_name, schema)

    def has_sequence(self, sequence_name, schema=None):
        """Return True if the backend has a table of the given name.

        :param sequence_name: name of the table to check
        :param schema: schema name to query, if not the default schema.

        .. versionadded:: 1.4

        """
        # TODO: info_cache?
        with self._operation_context() as conn:
            return self.dialect.has_sequence(conn, sequence_name, schema)

    def get_sorted_table_and_fkc_names(self, schema=None):
        """Return dependency-sorted table and foreign key constraint names in
        referred to within a particular schema.

        This will yield 2-tuples of
        ``(tablename, [(tname, fkname), (tname, fkname), ...])``
        consisting of table names in CREATE order grouped with the foreign key
        constraint names that are not detected as belonging to a cycle.
        The final element
        will be ``(None, [(tname, fkname), (tname, fkname), ..])``
        which will consist of remaining
        foreign key constraint names that would require a separate CREATE
        step after-the-fact, based on dependencies between tables.

        .. versionadded:: 1.0.-

        .. seealso::

            :meth:`_reflection.Inspector.get_table_names`

            :func:`.sort_tables_and_constraints` - similar method which works
            with an already-given :class:`_schema.MetaData`.

        """

        with self._operation_context() as conn:
            tnames = self.dialect.get_table_names(
                conn, schema, info_cache=self.info_cache
            )

        tuples = set()
        remaining_fkcs = set()

        fknames_for_table = {}
        for tname in tnames:
            fkeys = self.get_foreign_keys(tname, schema)
            fknames_for_table[tname] = set([fk["name"] for fk in fkeys])
            for fkey in fkeys:
                if tname != fkey["referred_table"]:
                    tuples.add((fkey["referred_table"], tname))
        try:
            candidate_sort = list(topological.sort(tuples, tnames))
        except exc.CircularDependencyError as err:
            for edge in err.edges:
                tuples.remove(edge)
                remaining_fkcs.update(
                    (edge[1], fkc) for fkc in fknames_for_table[edge[1]]
                )

            candidate_sort = list(topological.sort(tuples, tnames))
        return [
            (tname, fknames_for_table[tname].difference(remaining_fkcs))
            for tname in candidate_sort
        ] + [(None, list(remaining_fkcs))]

    def get_temp_table_names(self):
        """Return a list of temporary table names for the current bind.

        This method is unsupported by most dialects; currently
        only SQLite implements it.

        .. versionadded:: 1.0.0

        """

        with self._operation_context() as conn:
            return self.dialect.get_temp_table_names(
                conn, info_cache=self.info_cache
            )

    def get_temp_view_names(self):
        """Return a list of temporary view names for the current bind.

        This method is unsupported by most dialects; currently
        only SQLite implements it.

        .. versionadded:: 1.0.0

        """
        with self._operation_context() as conn:
            return self.dialect.get_temp_view_names(
                conn, info_cache=self.info_cache
            )

    def get_table_options(self, table_name, schema=None, **kw):
        """Return a dictionary of options specified when the table of the
        given name was created.

        This currently includes some options that apply to MySQL tables.

        :param table_name: string name of the table.  For special quoting,
         use :class:`.quoted_name`.

        :param schema: string schema name; if omitted, uses the default schema
         of the database connection.  For special quoting,
         use :class:`.quoted_name`.

        """
        if hasattr(self.dialect, "get_table_options"):
            with self._operation_context() as conn:
                return self.dialect.get_table_options(
                    conn, table_name, schema, info_cache=self.info_cache, **kw
                )
        return {}

    def get_view_names(self, schema=None):
        """Return all view names in `schema`.

        :param schema: Optional, retrieve names from a non-default schema.
         For special quoting, use :class:`.quoted_name`.

        """

        with self._operation_context() as conn:
            return self.dialect.get_view_names(
                conn, schema, info_cache=self.info_cache
            )

    def get_sequence_names(self, schema=None):
        """Return all sequence names in `schema`.

        :param schema: Optional, retrieve names from a non-default schema.
         For special quoting, use :class:`.quoted_name`.

        """

        with self._operation_context() as conn:
            return self.dialect.get_sequence_names(
                conn, schema, info_cache=self.info_cache
            )

    def get_view_definition(self, view_name, schema=None):
        """Return definition for `view_name`.

        :param schema: Optional, retrieve names from a non-default schema.
         For special quoting, use :class:`.quoted_name`.

        """

        with self._operation_context() as conn:
            return self.dialect.get_view_definition(
                conn, view_name, schema, info_cache=self.info_cache
            )

    def get_columns(self, table_name, schema=None, **kw):
        """Return information about columns in `table_name`.

        Given a string `table_name` and an optional string `schema`, return
        column information as a list of dicts with these keys:

        * ``name`` - the column's name

        * ``type`` - the type of this column; an instance of
          :class:`~sqlalchemy.types.TypeEngine`

        * ``nullable`` - boolean flag if the column is NULL or NOT NULL

        * ``default`` - the column's server default value - this is returned
          as a string SQL expression.

        * ``autoincrement`` - indicates that the column is auto incremented -
          this is returned as a boolean or 'auto'

        * ``comment`` - (optional) the comment on the column. Only some
          dialects return this key

        * ``computed`` - (optional) when present it indicates that this column
          is computed by the database. Only some dialects return this key.
          Returned as a dict with the keys:

          * ``sqltext`` - the expression used to generate this column returned
            as a string SQL expression

          * ``persisted`` - (optional) boolean that indicates if the column is
            stored in the table

          .. versionadded:: 1.3.16 - added support for computed reflection.

        * ``identity`` - (optional) when present it indicates that this column
          is a generated always column. Only some dialects return this key.
          For a list of keywords on this dict see :class:`_schema.Identity`.

          .. versionadded:: 1.4 - added support for identity column reflection.

        * ``dialect_options`` - (optional) a dict with dialect specific options

        :param table_name: string name of the table.  For special quoting,
         use :class:`.quoted_name`.

        :param schema: string schema name; if omitted, uses the default schema
         of the database connection.  For special quoting,
         use :class:`.quoted_name`.

        :return: list of dictionaries, each representing the definition of
         a database column.

        """

        with self._operation_context() as conn:
            col_defs = self.dialect.get_columns(
                conn, table_name, schema, info_cache=self.info_cache, **kw
            )
        for col_def in col_defs:
            # make this easy and only return instances for coltype
            coltype = col_def["type"]
            if not isinstance(coltype, TypeEngine):
                col_def["type"] = coltype()
        return col_defs

    def get_pk_constraint(self, table_name, schema=None, **kw):
        """Return information about primary key constraint on `table_name`.

        Given a string `table_name`, and an optional string `schema`, return
        primary key information as a dictionary with these keys:

        * ``constrained_columns`` -
          a list of column names that make up the primary key

        * ``name`` -
          optional name of the primary key constraint.

        :param table_name: string name of the table.  For special quoting,
         use :class:`.quoted_name`.

        :param schema: string schema name; if omitted, uses the default schema
         of the database connection.  For special quoting,
         use :class:`.quoted_name`.

        """
        with self._operation_context() as conn:
            return self.dialect.get_pk_constraint(
                conn, table_name, schema, info_cache=self.info_cache, **kw
            )

    def get_foreign_keys(self, table_name, schema=None, **kw):
        """Return information about foreign_keys in `table_name`.

        Given a string `table_name`, and an optional string `schema`, return
        foreign key information as a list of dicts with these keys:

        * ``constrained_columns`` -
          a list of column names that make up the foreign key

        * ``referred_schema`` -
          the name of the referred schema

        * ``referred_table`` -
          the name of the referred table

        * ``referred_columns`` -
          a list of column names in the referred table that correspond to
          constrained_columns

        * ``name`` -
          optional name of the foreign key constraint.

        :param table_name: string name of the table.  For special quoting,
         use :class:`.quoted_name`.

        :param schema: string schema name; if omitted, uses the default schema
         of the database connection.  For special quoting,
         use :class:`.quoted_name`.

        """

        with self._operation_context() as conn:
            return self.dialect.get_foreign_keys(
                conn, table_name, schema, info_cache=self.info_cache, **kw
            )

    def get_indexes(self, table_name, schema=None, **kw):
        """Return information about indexes in `table_name`.

        Given a string `table_name` and an optional string `schema`, return
        index information as a list of dicts with these keys:

        * ``name`` -
          the index's name

        * ``column_names`` -
          list of column names in order

        * ``unique`` -
          boolean

        * ``column_sorting`` -
          optional dict mapping column names to tuple of sort keywords,
          which may include ``asc``, ``desc``, ``nulls_first``, ``nulls_last``.

          .. versionadded:: 1.3.5

        * ``dialect_options`` -
          dict of dialect-specific index options.  May not be present
          for all dialects.

          .. versionadded:: 1.0.0

        :param table_name: string name of the table.  For special quoting,
         use :class:`.quoted_name`.

        :param schema: string schema name; if omitted, uses the default schema
         of the database connection.  For special quoting,
         use :class:`.quoted_name`.

        """

        with self._operation_context() as conn:
            return self.dialect.get_indexes(
                conn, table_name, schema, info_cache=self.info_cache, **kw
            )

    def get_unique_constraints(self, table_name, schema=None, **kw):
        """Return information about unique constraints in `table_name`.

        Given a string `table_name` and an optional string `schema`, return
        unique constraint information as a list of dicts with these keys:

        * ``name`` -
          the unique constraint's name

        * ``column_names`` -
          list of column names in order

        :param table_name: string name of the table.  For special quoting,
         use :class:`.quoted_name`.

        :param schema: string schema name; if omitted, uses the default schema
         of the database connection.  For special quoting,
         use :class:`.quoted_name`.

        """

        with self._operation_context() as conn:
            return self.dialect.get_unique_constraints(
                conn, table_name, schema, info_cache=self.info_cache, **kw
            )

    def get_table_comment(self, table_name, schema=None, **kw):
        """Return information about the table comment for ``table_name``.

        Given a string ``table_name`` and an optional string ``schema``,
        return table comment information as a dictionary with these keys:

        * ``text`` -
            text of the comment.

        Raises ``NotImplementedError`` for a dialect that does not support
        comments.

        .. versionadded:: 1.2

        """

        with self._operation_context() as conn:
            return self.dialect.get_table_comment(
                conn, table_name, schema, info_cache=self.info_cache, **kw
            )

    def get_check_constraints(self, table_name, schema=None, **kw):
        """Return information about check constraints in `table_name`.

        Given a string `table_name` and an optional string `schema`, return
        check constraint information as a list of dicts with these keys:

        * ``name`` -
          the check constraint's name

        * ``sqltext`` -
          the check constraint's SQL expression

        * ``dialect_options`` -
          may or may not be present; a dictionary with additional
          dialect-specific options for this CHECK constraint

          .. versionadded:: 1.3.8

        :param table_name: string name of the table.  For special quoting,
         use :class:`.quoted_name`.

        :param schema: string schema name; if omitted, uses the default schema
         of the database connection.  For special quoting,
         use :class:`.quoted_name`.

        .. versionadded:: 1.1.0

        """

        with self._operation_context() as conn:
            return self.dialect.get_check_constraints(
                conn, table_name, schema, info_cache=self.info_cache, **kw
            )

    @util.deprecated_20(
        ":meth:`_reflection.Inspector.reflecttable`",
        "The :meth:`_reflection.Inspector.reflecttable` "
        "method was renamed to "
        ":meth:`_reflection.Inspector.reflect_table`. This deprecated alias "
        "will be removed in a future release.",
    )
    def reflecttable(self, *args, **kwargs):
        "See reflect_table. This method name is deprecated"
        return self.reflect_table(*args, **kwargs)

    def reflect_table(
        self,
        table,
        include_columns,
        exclude_columns=(),
        resolve_fks=True,
        _extend_on=None,
    ):
        """Given a :class:`_schema.Table` object, load its internal
        constructs based on introspection.

        This is the underlying method used by most dialects to produce
        table reflection.  Direct usage is like::

            from sqlalchemy import create_engine, MetaData, Table
            from sqlalchemy import inspect

            engine = create_engine('...')
            meta = MetaData()
            user_table = Table('user', meta)
            insp = inspect(engine)
            insp.reflect_table(user_table, None)

        .. versionchanged:: 1.4 Renamed from ``reflecttable`` to
           ``reflect_table``

        :param table: a :class:`~sqlalchemy.schema.Table` instance.
        :param include_columns: a list of string column names to include
          in the reflection process.  If ``None``, all columns are reflected.

        """

        if _extend_on is not None:
            if table in _extend_on:
                return
            else:
                _extend_on.add(table)

        dialect = self.bind.dialect

        with self._operation_context() as conn:
            schema = conn.schema_for_object(table)

        table_name = table.name

        # get table-level arguments that are specifically
        # intended for reflection, e.g. oracle_resolve_synonyms.
        # these are unconditionally passed to related Table
        # objects
        reflection_options = dict(
            (k, table.dialect_kwargs.get(k))
            for k in dialect.reflection_options
            if k in table.dialect_kwargs
        )

        # reflect table options, like mysql_engine
        tbl_opts = self.get_table_options(
            table_name, schema, **table.dialect_kwargs
        )
        if tbl_opts:
            # add additional kwargs to the Table if the dialect
            # returned them
            table._validate_dialect_kwargs(tbl_opts)

        if util.py2k:
            if isinstance(schema, str):
                schema = schema.decode(dialect.encoding)
            if isinstance(table_name, str):
                table_name = table_name.decode(dialect.encoding)

        found_table = False
        cols_by_orig_name = {}

        for col_d in self.get_columns(
            table_name, schema, **table.dialect_kwargs
        ):
            found_table = True

            self._reflect_column(
                table,
                col_d,
                include_columns,
                exclude_columns,
                cols_by_orig_name,
            )

        # NOTE: support tables/views with no columns
        if not found_table and not self.has_table(table_name, schema):
            raise exc.NoSuchTableError(table_name)

        self._reflect_pk(
            table_name, schema, table, cols_by_orig_name, exclude_columns
        )

        self._reflect_fk(
            table_name,
            schema,
            table,
            cols_by_orig_name,
            exclude_columns,
            resolve_fks,
            _extend_on,
            reflection_options,
        )

        self._reflect_indexes(
            table_name,
            schema,
            table,
            cols_by_orig_name,
            include_columns,
            exclude_columns,
            reflection_options,
        )

        self._reflect_unique_constraints(
            table_name,
            schema,
            table,
            cols_by_orig_name,
            include_columns,
            exclude_columns,
            reflection_options,
        )

        self._reflect_check_constraints(
            table_name,
            schema,
            table,
            cols_by_orig_name,
            include_columns,
            exclude_columns,
            reflection_options,
        )

        self._reflect_table_comment(
            table_name, schema, table, reflection_options
        )

    def _reflect_column(
        self, table, col_d, include_columns, exclude_columns, cols_by_orig_name
    ):

        orig_name = col_d["name"]

        table.metadata.dispatch.column_reflect(self, table, col_d)
        table.dispatch.column_reflect(self, table, col_d)

        # fetch name again as column_reflect is allowed to
        # change it
        name = col_d["name"]
        if (include_columns and name not in include_columns) or (
            exclude_columns and name in exclude_columns
        ):
            return

        coltype = col_d["type"]

        col_kw = dict(
            (k, col_d[k])
            for k in [
                "nullable",
                "autoincrement",
                "quote",
                "info",
                "key",
                "comment",
            ]
            if k in col_d
        )

        if "dialect_options" in col_d:
            col_kw.update(col_d["dialect_options"])

        colargs = []
        if col_d.get("default") is not None:
            default = col_d["default"]
            if isinstance(default, sql.elements.TextClause):
                default = sa_schema.DefaultClause(default, _reflected=True)
            elif not isinstance(default, sa_schema.FetchedValue):
                default = sa_schema.DefaultClause(
                    sql.text(col_d["default"]), _reflected=True
                )

            colargs.append(default)

        if "computed" in col_d:
            computed = sa_schema.Computed(**col_d["computed"])
            colargs.append(computed)

        if "identity" in col_d:
            computed = sa_schema.Identity(**col_d["identity"])
            colargs.append(computed)

        if "sequence" in col_d:
            self._reflect_col_sequence(col_d, colargs)

        cols_by_orig_name[orig_name] = col = sa_schema.Column(
            name, coltype, *colargs, **col_kw
        )

        if col.key in table.primary_key:
            col.primary_key = True
        table.append_column(col, replace_existing=True)

    def _reflect_col_sequence(self, col_d, colargs):
        if "sequence" in col_d:
            # TODO: mssql and sybase are using this.
            seq = col_d["sequence"]
            sequence = sa_schema.Sequence(seq["name"], 1, 1)
            if "start" in seq:
                sequence.start = seq["start"]
            if "increment" in seq:
                sequence.increment = seq["increment"]
            colargs.append(sequence)

    def _reflect_pk(
        self, table_name, schema, table, cols_by_orig_name, exclude_columns
    ):
        pk_cons = self.get_pk_constraint(
            table_name, schema, **table.dialect_kwargs
        )
        if pk_cons:
            pk_cols = [
                cols_by_orig_name[pk]
                for pk in pk_cons["constrained_columns"]
                if pk in cols_by_orig_name and pk not in exclude_columns
            ]

            # update pk constraint name
            table.primary_key.name = pk_cons.get("name")

            # tell the PKConstraint to re-initialize
            # its column collection
            table.primary_key._reload(pk_cols)

    def _reflect_fk(
        self,
        table_name,
        schema,
        table,
        cols_by_orig_name,
        exclude_columns,
        resolve_fks,
        _extend_on,
        reflection_options,
    ):
        fkeys = self.get_foreign_keys(
            table_name, schema, **table.dialect_kwargs
        )
        for fkey_d in fkeys:
            conname = fkey_d["name"]
            # look for columns by orig name in cols_by_orig_name,
            # but support columns that are in-Python only as fallback
            constrained_columns = [
                cols_by_orig_name[c].key if c in cols_by_orig_name else c
                for c in fkey_d["constrained_columns"]
            ]
            if exclude_columns and set(constrained_columns).intersection(
                exclude_columns
            ):
                continue
            referred_schema = fkey_d["referred_schema"]
            referred_table = fkey_d["referred_table"]
            referred_columns = fkey_d["referred_columns"]
            refspec = []
            if referred_schema is not None:
                if resolve_fks:
                    sa_schema.Table(
                        referred_table,
                        table.metadata,
                        schema=referred_schema,
                        autoload_with=self.bind,
                        _extend_on=_extend_on,
                        **reflection_options
                    )
                for column in referred_columns:
                    refspec.append(
                        ".".join([referred_schema, referred_table, column])
                    )
            else:
                if resolve_fks:
                    sa_schema.Table(
                        referred_table,
                        table.metadata,
                        autoload_with=self.bind,
                        schema=sa_schema.BLANK_SCHEMA,
                        _extend_on=_extend_on,
                        **reflection_options
                    )
                for column in referred_columns:
                    refspec.append(".".join([referred_table, column]))
            if "options" in fkey_d:
                options = fkey_d["options"]
            else:
                options = {}
            table.append_constraint(
                sa_schema.ForeignKeyConstraint(
                    constrained_columns,
                    refspec,
                    conname,
                    link_to_name=True,
                    **options
                )
            )

    _index_sort_exprs = [
        ("asc", operators.asc_op),
        ("desc", operators.desc_op),
        ("nulls_first", operators.nulls_first_op),
        ("nulls_last", operators.nulls_last_op),
    ]

    def _reflect_indexes(
        self,
        table_name,
        schema,
        table,
        cols_by_orig_name,
        include_columns,
        exclude_columns,
        reflection_options,
    ):
        # Indexes
        indexes = self.get_indexes(table_name, schema)
        for index_d in indexes:
            name = index_d["name"]
            columns = index_d["column_names"]
            column_sorting = index_d.get("column_sorting", {})
            unique = index_d["unique"]
            flavor = index_d.get("type", "index")
            dialect_options = index_d.get("dialect_options", {})

            duplicates = index_d.get("duplicates_constraint")
            if include_columns and not set(columns).issubset(include_columns):
                util.warn(
                    "Omitting %s key for (%s), key covers omitted columns."
                    % (flavor, ", ".join(columns))
                )
                continue
            if duplicates:
                continue
            # look for columns by orig name in cols_by_orig_name,
            # but support columns that are in-Python only as fallback
            idx_cols = []
            for c in columns:
                try:
                    idx_col = (
                        cols_by_orig_name[c]
                        if c in cols_by_orig_name
                        else table.c[c]
                    )
                except KeyError:
                    util.warn(
                        "%s key '%s' was not located in "
                        "columns for table '%s'" % (flavor, c, table_name)
                    )
                    continue
                c_sorting = column_sorting.get(c, ())
                for k, op in self._index_sort_exprs:
                    if k in c_sorting:
                        idx_col = op(idx_col)
                idx_cols.append(idx_col)

            sa_schema.Index(
                name,
                *idx_cols,
                _table=table,
                **dict(list(dialect_options.items()) + [("unique", unique)])
            )

    def _reflect_unique_constraints(
        self,
        table_name,
        schema,
        table,
        cols_by_orig_name,
        include_columns,
        exclude_columns,
        reflection_options,
    ):

        # Unique Constraints
        try:
            constraints = self.get_unique_constraints(table_name, schema)
        except NotImplementedError:
            # optional dialect feature
            return

        for const_d in constraints:
            conname = const_d["name"]
            columns = const_d["column_names"]
            duplicates = const_d.get("duplicates_index")
            if include_columns and not set(columns).issubset(include_columns):
                util.warn(
                    "Omitting unique constraint key for (%s), "
                    "key covers omitted columns." % ", ".join(columns)
                )
                continue
            if duplicates:
                continue
            # look for columns by orig name in cols_by_orig_name,
            # but support columns that are in-Python only as fallback
            constrained_cols = []
            for c in columns:
                try:
                    constrained_col = (
                        cols_by_orig_name[c]
                        if c in cols_by_orig_name
                        else table.c[c]
                    )
                except KeyError:
                    util.warn(
                        "unique constraint key '%s' was not located in "
                        "columns for table '%s'" % (c, table_name)
                    )
                else:
                    constrained_cols.append(constrained_col)
            table.append_constraint(
                sa_schema.UniqueConstraint(*constrained_cols, name=conname)
            )

    def _reflect_check_constraints(
        self,
        table_name,
        schema,
        table,
        cols_by_orig_name,
        include_columns,
        exclude_columns,
        reflection_options,
    ):
        try:
            constraints = self.get_check_constraints(table_name, schema)
        except NotImplementedError:
            # optional dialect feature
            return

        for const_d in constraints:
            table.append_constraint(sa_schema.CheckConstraint(**const_d))

    def _reflect_table_comment(
        self, table_name, schema, table, reflection_options
    ):
        try:
            comment_dict = self.get_table_comment(table_name, schema)
        except NotImplementedError:
            return
        else:
            table.comment = comment_dict.get("text", None)
