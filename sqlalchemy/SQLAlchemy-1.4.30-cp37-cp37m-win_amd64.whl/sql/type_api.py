# sql/types_api.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""Base types API.

"""


from . import operators
from .base import SchemaEventTarget
from .traversals import NO_CACHE
from .visitors import Traversible
from .visitors import TraversibleType
from .. import exc
from .. import util

# these are back-assigned by sqltypes.
BOOLEANTYPE = None
INTEGERTYPE = None
NULLTYPE = None
STRINGTYPE = None
MATCHTYPE = None
INDEXABLE = None
TABLEVALUE = None
_resolve_value_to_type = None


class TypeEngine(Traversible):
    """The ultimate base class for all SQL datatypes.

    Common subclasses of :class:`.TypeEngine` include
    :class:`.String`, :class:`.Integer`, and :class:`.Boolean`.

    For an overview of the SQLAlchemy typing system, see
    :ref:`types_toplevel`.

    .. seealso::

        :ref:`types_toplevel`

    """

    _sqla_type = True
    _isnull = False
    _is_tuple_type = False
    _is_table_value = False
    _is_array = False
    _is_type_decorator = False

    class Comparator(operators.ColumnOperators):
        """Base class for custom comparison operations defined at the
        type level.  See :attr:`.TypeEngine.comparator_factory`.


        """

        __slots__ = "expr", "type"

        default_comparator = None

        def __clause_element__(self):
            return self.expr

        def __init__(self, expr):
            self.expr = expr
            self.type = expr.type

        @util.preload_module("sqlalchemy.sql.default_comparator")
        def operate(self, op, *other, **kwargs):
            default_comparator = util.preloaded.sql_default_comparator
            o = default_comparator.operator_lookup[op.__name__]
            return o[0](self.expr, op, *(other + o[1:]), **kwargs)

        @util.preload_module("sqlalchemy.sql.default_comparator")
        def reverse_operate(self, op, other, **kwargs):
            default_comparator = util.preloaded.sql_default_comparator
            o = default_comparator.operator_lookup[op.__name__]
            return o[0](self.expr, op, other, reverse=True, *o[1:], **kwargs)

        def _adapt_expression(self, op, other_comparator):
            """evaluate the return type of <self> <op> <othertype>,
            and apply any adaptations to the given operator.

            This method determines the type of a resulting binary expression
            given two source types and an operator.   For example, two
            :class:`_schema.Column` objects, both of the type
            :class:`.Integer`, will
            produce a :class:`.BinaryExpression` that also has the type
            :class:`.Integer` when compared via the addition (``+``) operator.
            However, using the addition operator with an :class:`.Integer`
            and a :class:`.Date` object will produce a :class:`.Date`, assuming
            "days delta" behavior by the database (in reality, most databases
            other than PostgreSQL don't accept this particular operation).

            The method returns a tuple of the form <operator>, <type>.
            The resulting operator and type will be those applied to the
            resulting :class:`.BinaryExpression` as the final operator and the
            right-hand side of the expression.

            Note that only a subset of operators make usage of
            :meth:`._adapt_expression`,
            including math operators and user-defined operators, but not
            boolean comparison or special SQL keywords like MATCH or BETWEEN.

            """

            return op, self.type

        def __reduce__(self):
            return _reconstitute_comparator, (self.expr,)

    hashable = True
    """Flag, if False, means values from this type aren't hashable.

    Used by the ORM when uniquing result lists.

    """

    comparator_factory = Comparator
    """A :class:`.TypeEngine.Comparator` class which will apply
    to operations performed by owning :class:`_expression.ColumnElement`
    objects.

    The :attr:`.comparator_factory` attribute is a hook consulted by
    the core expression system when column and SQL expression operations
    are performed.   When a :class:`.TypeEngine.Comparator` class is
    associated with this attribute, it allows custom re-definition of
    all existing operators, as well as definition of new operators.
    Existing operators include those provided by Python operator overloading
    such as :meth:`.operators.ColumnOperators.__add__` and
    :meth:`.operators.ColumnOperators.__eq__`,
    those provided as standard
    attributes of :class:`.operators.ColumnOperators` such as
    :meth:`.operators.ColumnOperators.like`
    and :meth:`.operators.ColumnOperators.in_`.

    Rudimentary usage of this hook is allowed through simple subclassing
    of existing types, or alternatively by using :class:`.TypeDecorator`.
    See the documentation section :ref:`types_operators` for examples.

    """

    sort_key_function = None
    """A sorting function that can be passed as the key to sorted.

    The default value of ``None`` indicates that the values stored by
    this type are self-sorting.

    .. versionadded:: 1.3.8

    """

    should_evaluate_none = False
    """If True, the Python constant ``None`` is considered to be handled
    explicitly by this type.

    The ORM uses this flag to indicate that a positive value of ``None``
    is passed to the column in an INSERT statement, rather than omitting
    the column from the INSERT statement which has the effect of firing
    off column-level defaults.   It also allows types which have special
    behavior for Python None, such as a JSON type, to indicate that
    they'd like to handle the None value explicitly.

    To set this flag on an existing type, use the
    :meth:`.TypeEngine.evaluates_none` method.

    .. seealso::

        :meth:`.TypeEngine.evaluates_none`

    .. versionadded:: 1.1


    """

    def evaluates_none(self):
        """Return a copy of this type which has the :attr:`.should_evaluate_none`
        flag set to True.

        E.g.::

                Table(
                    'some_table', metadata,
                    Column(
                        String(50).evaluates_none(),
                        nullable=True,
                        server_default='no value')
                )

        The ORM uses this flag to indicate that a positive value of ``None``
        is passed to the column in an INSERT statement, rather than omitting
        the column from the INSERT statement which has the effect of firing
        off column-level defaults.   It also allows for types which have
        special behavior associated with the Python None value to indicate
        that the value doesn't necessarily translate into SQL NULL; a
        prime example of this is a JSON type which may wish to persist the
        JSON value ``'null'``.

        In all cases, the actual NULL SQL value can be always be
        persisted in any column by using
        the :obj:`_expression.null` SQL construct in an INSERT statement
        or associated with an ORM-mapped attribute.

        .. note::

            The "evaluates none" flag does **not** apply to a value
            of ``None`` passed to :paramref:`_schema.Column.default` or
            :paramref:`_schema.Column.server_default`; in these cases,
            ``None``
            still means "no default".

        .. versionadded:: 1.1

        .. seealso::

            :ref:`session_forcing_null` - in the ORM documentation

            :paramref:`.postgresql.JSON.none_as_null` - PostgreSQL JSON
            interaction with this flag.

            :attr:`.TypeEngine.should_evaluate_none` - class-level flag

        """
        typ = self.copy()
        typ.should_evaluate_none = True
        return typ

    def copy(self, **kw):
        return self.adapt(self.__class__)

    def compare_against_backend(self, dialect, conn_type):
        """Compare this type against the given backend type.

        This function is currently not implemented for SQLAlchemy
        types, and for all built in types will return ``None``.  However,
        it can be implemented by a user-defined type
        where it can be consumed by schema comparison tools such as
        Alembic autogenerate.

        A future release of SQLAlchemy will potentially implement this method
        for builtin types as well.

        The function should return True if this type is equivalent to the
        given type; the type is typically reflected from the database
        so should be database specific.  The dialect in use is also
        passed.   It can also return False to assert that the type is
        not equivalent.

        :param dialect: a :class:`.Dialect` that is involved in the comparison.

        :param conn_type: the type object reflected from the backend.

        .. versionadded:: 1.0.3

        """
        return None

    def copy_value(self, value):
        return value

    def literal_processor(self, dialect):
        """Return a conversion function for processing literal values that are
        to be rendered directly without using binds.

        This function is used when the compiler makes use of the
        "literal_binds" flag, typically used in DDL generation as well
        as in certain scenarios where backends don't accept bound parameters.

        Returns a callable which will receive a literal Python value
        as the sole positional argument and will return a string representation
        to be rendered in a SQL statement.

        .. note::

            This method is only called relative to a **dialect specific type
            object**, which is often **private to a dialect in use** and is not
            the same type object as the public facing one, which means it's not
            feasible to subclass a :class:`.types.TypeEngine` class in order to
            provide an alternate :meth:`_types.TypeEngine.literal_processor`
            method, unless subclassing the :class:`_types.UserDefinedType`
            class explicitly.

            To provide alternate behavior for
            :meth:`_types.TypeEngine.literal_processor`, implement a
            :class:`_types.TypeDecorator` class and provide an implementation
            of :meth:`_types.TypeDecorator.process_literal_param`.

            .. seealso::

                :ref:`types_typedecorator`


        """
        return None

    def bind_processor(self, dialect):
        """Return a conversion function for processing bind values.

        Returns a callable which will receive a bind parameter value
        as the sole positional argument and will return a value to
        send to the DB-API.

        If processing is not necessary, the method should return ``None``.

        .. note::

            This method is only called relative to a **dialect specific type
            object**, which is often **private to a dialect in use** and is not
            the same type object as the public facing one, which means it's not
            feasible to subclass a :class:`.types.TypeEngine` class in order to
            provide an alternate :meth:`_types.TypeEngine.bind_processor`
            method, unless subclassing the :class:`_types.UserDefinedType`
            class explicitly.

            To provide alternate behavior for
            :meth:`_types.TypeEngine.bind_processor`, implement a
            :class:`_types.TypeDecorator` class and provide an implementation
            of :meth:`_types.TypeDecorator.process_bind_param`.

            .. seealso::

                :ref:`types_typedecorator`


        :param dialect: Dialect instance in use.

        """
        return None

    def result_processor(self, dialect, coltype):
        """Return a conversion function for processing result row values.

        Returns a callable which will receive a result row column
        value as the sole positional argument and will return a value
        to return to the user.

        If processing is not necessary, the method should return ``None``.

        .. note::

            This method is only called relative to a **dialect specific type
            object**, which is often **private to a dialect in use** and is not
            the same type object as the public facing one, which means it's not
            feasible to subclass a :class:`.types.TypeEngine` class in order to
            provide an alternate :meth:`_types.TypeEngine.result_processor`
            method, unless subclassing the :class:`_types.UserDefinedType`
            class explicitly.

            To provide alternate behavior for
            :meth:`_types.TypeEngine.result_processor`, implement a
            :class:`_types.TypeDecorator` class and provide an implementation
            of :meth:`_types.TypeDecorator.process_result_value`.

            .. seealso::

                :ref:`types_typedecorator`

        :param dialect: Dialect instance in use.

        :param coltype: DBAPI coltype argument received in cursor.description.

        """
        return None

    def column_expression(self, colexpr):
        """Given a SELECT column expression, return a wrapping SQL expression.

        This is typically a SQL function that wraps a column expression
        as rendered in the columns clause of a SELECT statement.
        It is used for special data types that require
        columns to be wrapped in some special database function in order
        to coerce the value before being sent back to the application.
        It is the SQL analogue of the :meth:`.TypeEngine.result_processor`
        method.

        This method is called during the **SQL compilation** phase of a
        statement, when rendering a SQL string. It is **not** called
        against specific values.

        .. note::

            This method is only called relative to a **dialect specific type
            object**, which is often **private to a dialect in use** and is not
            the same type object as the public facing one, which means it's not
            feasible to subclass a :class:`.types.TypeEngine` class in order to
            provide an alternate :meth:`_types.TypeEngine.column_expression`
            method, unless subclassing the :class:`_types.UserDefinedType`
            class explicitly.

            To provide alternate behavior for
            :meth:`_types.TypeEngine.column_expression`, implement a
            :class:`_types.TypeDecorator` class and provide an implementation
            of :meth:`_types.TypeDecorator.column_expression`.

            .. seealso::

                :ref:`types_typedecorator`


        .. seealso::

            :ref:`types_sql_value_processing`

        """

        return None

    @util.memoized_property
    def _has_column_expression(self):
        """memoized boolean, check if column_expression is implemented.

        Allows the method to be skipped for the vast majority of expression
        types that don't use this feature.

        """

        return (
            self.__class__.column_expression.__code__
            is not TypeEngine.column_expression.__code__
        )

    def bind_expression(self, bindvalue):
        """Given a bind value (i.e. a :class:`.BindParameter` instance),
        return a SQL expression in its place.

        This is typically a SQL function that wraps the existing bound
        parameter within the statement.  It is used for special data types
        that require literals being wrapped in some special database function
        in order to coerce an application-level value into a database-specific
        format.  It is the SQL analogue of the
        :meth:`.TypeEngine.bind_processor` method.

        This method is called during the **SQL compilation** phase of a
        statement, when rendering a SQL string. It is **not** called
        against specific values.

        Note that this method, when implemented, should always return
        the exact same structure, without any conditional logic, as it
        may be used in an executemany() call against an arbitrary number
        of bound parameter sets.

        .. note::

            This method is only called relative to a **dialect specific type
            object**, which is often **private to a dialect in use** and is not
            the same type object as the public facing one, which means it's not
            feasible to subclass a :class:`.types.TypeEngine` class in order to
            provide an alternate :meth:`_types.TypeEngine.bind_expression`
            method, unless subclassing the :class:`_types.UserDefinedType`
            class explicitly.

            To provide alternate behavior for
            :meth:`_types.TypeEngine.bind_expression`, implement a
            :class:`_types.TypeDecorator` class and provide an implementation
            of :meth:`_types.TypeDecorator.bind_expression`.

            .. seealso::

                :ref:`types_typedecorator`

        .. seealso::

            :ref:`types_sql_value_processing`

        """
        return None

    @util.memoized_property
    def _has_bind_expression(self):
        """memoized boolean, check if bind_expression is implemented.

        Allows the method to be skipped for the vast majority of expression
        types that don't use this feature.

        """

        return util.method_is_overridden(self, TypeEngine.bind_expression)

    @staticmethod
    def _to_instance(cls_or_self):
        return to_instance(cls_or_self)

    def compare_values(self, x, y):
        """Compare two values for equality."""

        return x == y

    def get_dbapi_type(self, dbapi):
        """Return the corresponding type object from the underlying DB-API, if
        any.

        This can be useful for calling ``setinputsizes()``, for example.

        """
        return None

    @property
    def python_type(self):
        """Return the Python type object expected to be returned
        by instances of this type, if known.

        Basically, for those types which enforce a return type,
        or are known across the board to do such for all common
        DBAPIs (like ``int`` for example), will return that type.

        If a return type is not defined, raises
        ``NotImplementedError``.

        Note that any type also accommodates NULL in SQL which
        means you can also get back ``None`` from any type
        in practice.

        """
        raise NotImplementedError()

    def with_variant(self, type_, dialect_name):
        r"""Produce a new type object that will utilize the given
        type when applied to the dialect of the given name.

        e.g.::

            from sqlalchemy.types import String
            from sqlalchemy.dialects import mysql

            s = String()

            s = s.with_variant(mysql.VARCHAR(collation='foo'), 'mysql')

        The construction of :meth:`.TypeEngine.with_variant` is always
        from the "fallback" type to that which is dialect specific.
        The returned type is an instance of :class:`.Variant`, which
        itself provides a :meth:`.Variant.with_variant`
        that can be called repeatedly.

        :param type\_: a :class:`.TypeEngine` that will be selected
         as a variant from the originating type, when a dialect
         of the given name is in use.
        :param dialect_name: base name of the dialect which uses
         this type. (i.e. ``'postgresql'``, ``'mysql'``, etc.)

        """
        return Variant(self, {dialect_name: to_instance(type_)})

    def _resolve_for_literal(self, value):
        """adjust this type given a literal Python value that will be
        stored in a bound parameter.

        Used exclusively by _resolve_value_to_type().

        .. versionadded:: 1.4.30 or 2.0

        """
        return self

    @util.memoized_property
    def _type_affinity(self):
        """Return a rudimental 'affinity' value expressing the general class
        of type."""

        typ = None
        for t in self.__class__.__mro__:
            if t in (TypeEngine, UserDefinedType):
                return typ
            elif issubclass(t, (TypeEngine, UserDefinedType)):
                typ = t
        else:
            return self.__class__

    @util.memoized_property
    def _generic_type_affinity(self):
        best_camelcase = None
        best_uppercase = None

        if not isinstance(self, (TypeEngine, UserDefinedType)):
            return self.__class__

        for t in self.__class__.__mro__:
            if (
                t.__module__
                in (
                    "sqlalchemy.sql.sqltypes",
                    "sqlalchemy.sql.type_api",
                )
                and issubclass(t, TypeEngine)
                and t is not TypeEngine
                and t.__name__[0] != "_"
            ):
                if t.__name__.isupper() and not best_uppercase:
                    best_uppercase = t
                elif not t.__name__.isupper() and not best_camelcase:
                    best_camelcase = t

        return best_camelcase or best_uppercase or NULLTYPE.__class__

    def as_generic(self, allow_nulltype=False):
        """
        Return an instance of the generic type corresponding to this type
        using heuristic rule. The method may be overridden if this
        heuristic rule is not sufficient.

        >>> from sqlalchemy.dialects.mysql import INTEGER
        >>> INTEGER(display_width=4).as_generic()
        Integer()

        >>> from sqlalchemy.dialects.mysql import NVARCHAR
        >>> NVARCHAR(length=100).as_generic()
        Unicode(length=100)

        .. versionadded:: 1.4.0b2


        .. seealso::

            :ref:`metadata_reflection_dbagnostic_types` - describes the
            use of :meth:`_types.TypeEngine.as_generic` in conjunction with
            the :meth:`_sql.DDLEvents.column_reflect` event, which is its
            intended use.

        """
        if (
            not allow_nulltype
            and self._generic_type_affinity == NULLTYPE.__class__
        ):
            raise NotImplementedError(
                "Default TypeEngine.as_generic() "
                "heuristic method was unsuccessful for {}. A custom "
                "as_generic() method must be implemented for this "
                "type class.".format(
                    self.__class__.__module__ + "." + self.__class__.__name__
                )
            )

        return util.constructor_copy(self, self._generic_type_affinity)

    def dialect_impl(self, dialect):
        """Return a dialect-specific implementation for this
        :class:`.TypeEngine`.

        """
        try:
            return dialect._type_memos[self]["impl"]
        except KeyError:
            pass
        return self._dialect_info(dialect)["impl"]

    def _unwrapped_dialect_impl(self, dialect):
        """Return the 'unwrapped' dialect impl for this type.

        For a type that applies wrapping logic (e.g. TypeDecorator), give
        us the real, actual dialect-level type that is used.

        This is used by TypeDecorator itself as well at least one case where
        dialects need to check that a particular specific dialect-level
        type is in use, within the :meth:`.DefaultDialect.set_input_sizes`
        method.

        """
        return self.dialect_impl(dialect)

    def _cached_literal_processor(self, dialect):
        """Return a dialect-specific literal processor for this type."""
        try:
            return dialect._type_memos[self]["literal"]
        except KeyError:
            pass
        # avoid KeyError context coming into literal_processor() function
        # raises
        d = self._dialect_info(dialect)
        d["literal"] = lp = d["impl"].literal_processor(dialect)
        return lp

    def _cached_bind_processor(self, dialect):
        """Return a dialect-specific bind processor for this type."""

        try:
            return dialect._type_memos[self]["bind"]
        except KeyError:
            pass
        # avoid KeyError context coming into bind_processor() function
        # raises
        d = self._dialect_info(dialect)
        d["bind"] = bp = d["impl"].bind_processor(dialect)
        return bp

    def _cached_result_processor(self, dialect, coltype):
        """Return a dialect-specific result processor for this type."""

        try:
            return dialect._type_memos[self][coltype]
        except KeyError:
            pass
        # avoid KeyError context coming into result_processor() function
        # raises
        d = self._dialect_info(dialect)
        # key assumption: DBAPI type codes are
        # constants.  Else this dictionary would
        # grow unbounded.
        d[coltype] = rp = d["impl"].result_processor(dialect, coltype)
        return rp

    def _cached_custom_processor(self, dialect, key, fn):
        try:
            return dialect._type_memos[self][key]
        except KeyError:
            pass
        # avoid KeyError context coming into fn() function
        # raises
        d = self._dialect_info(dialect)
        impl = d["impl"]
        d[key] = result = fn(impl)
        return result

    def _dialect_info(self, dialect):
        """Return a dialect-specific registry which
        caches a dialect-specific implementation, bind processing
        function, and one or more result processing functions."""

        if self in dialect._type_memos:
            return dialect._type_memos[self]
        else:
            impl = self._gen_dialect_impl(dialect)
            if impl is self:
                impl = self.adapt(type(self))
            # this can't be self, else we create a cycle
            assert impl is not self
            dialect._type_memos[self] = d = {"impl": impl}
            return d

    def _gen_dialect_impl(self, dialect):
        return dialect.type_descriptor(self)

    @util.memoized_property
    def _static_cache_key(self):
        names = util.get_cls_kwargs(self.__class__)
        return (self.__class__,) + tuple(
            (
                k,
                self.__dict__[k]._static_cache_key
                if isinstance(self.__dict__[k], TypeEngine)
                else self.__dict__[k],
            )
            for k in names
            if k in self.__dict__ and not k.startswith("_")
        )

    def adapt(self, cls, **kw):
        """Produce an "adapted" form of this type, given an "impl" class
        to work with.

        This method is used internally to associate generic
        types with "implementation" types that are specific to a particular
        dialect.
        """
        return util.constructor_copy(self, cls, **kw)

    def coerce_compared_value(self, op, value):
        """Suggest a type for a 'coerced' Python value in an expression.

        Given an operator and value, gives the type a chance
        to return a type which the value should be coerced into.

        The default behavior here is conservative; if the right-hand
        side is already coerced into a SQL type based on its
        Python type, it is usually left alone.

        End-user functionality extension here should generally be via
        :class:`.TypeDecorator`, which provides more liberal behavior in that
        it defaults to coercing the other side of the expression into this
        type, thus applying special Python conversions above and beyond those
        needed by the DBAPI to both ides. It also provides the public method
        :meth:`.TypeDecorator.coerce_compared_value` which is intended for
        end-user customization of this behavior.

        """
        _coerced_type = _resolve_value_to_type(value)
        if (
            _coerced_type is NULLTYPE
            or _coerced_type._type_affinity is self._type_affinity
        ):
            return self
        else:
            return _coerced_type

    def _compare_type_affinity(self, other):
        return self._type_affinity is other._type_affinity

    def compile(self, dialect=None):
        """Produce a string-compiled form of this :class:`.TypeEngine`.

        When called with no arguments, uses a "default" dialect
        to produce a string result.

        :param dialect: a :class:`.Dialect` instance.

        """
        # arg, return value is inconsistent with
        # ClauseElement.compile()....this is a mistake.

        if not dialect:
            dialect = self._default_dialect()

        return dialect.type_compiler.process(self)

    @util.preload_module("sqlalchemy.engine.default")
    def _default_dialect(self):
        default = util.preloaded.engine_default
        return default.StrCompileDialect()

    def __str__(self):
        if util.py2k:
            return unicode(self.compile()).encode(  # noqa
                "ascii", "backslashreplace"
            )  # noqa
        else:
            return str(self.compile())

    def __repr__(self):
        return util.generic_repr(self)


class VisitableCheckKWArg(util.EnsureKWArgType, TraversibleType):
    pass


class ExternalType(object):
    """mixin that defines attributes and behaviors specific to third-party
    datatypes.

    "Third party" refers to datatypes that are defined outside the scope
    of SQLAlchemy within either end-user application code or within
    external extensions to SQLAlchemy.

    Subclasses currently include :class:`.TypeDecorator` and
    :class:`.UserDefinedType`.

    .. versionadded:: 1.4.28

    """

    cache_ok = None
    """Indicate if statements using this :class:`.ExternalType` are "safe to
    cache".

    The default value ``None`` will emit a warning and then not allow caching
    of a statement which includes this type.   Set to ``False`` to disable
    statements using this type from being cached at all without a warning.
    When set to ``True``, the object's class and selected elements from its
    state will be used as part of the cache key.  For example, using a
    :class:`.TypeDecorator`::

        class MyType(TypeDecorator):
            impl = String

            cache_ok = True

            def __init__(self, choices):
                self.choices = tuple(choices)
                self.internal_only = True

    The cache key for the above type would be equivalent to::

        >>> MyType(["a", "b", "c"])._static_cache_key
        (<class '__main__.MyType'>, ('choices', ('a', 'b', 'c')))

    The caching scheme will extract attributes from the type that correspond
    to the names of parameters in the ``__init__()`` method.  Above, the
    "choices" attribute becomes part of the cache key but "internal_only"
    does not, because there is no parameter named "internal_only".

    The requirements for cacheable elements is that they are hashable
    and also that they indicate the same SQL rendered for expressions using
    this type every time for a given cache value.

    To accommodate for datatypes that refer to unhashable structures such
    as dictionaries, sets and lists, these objects can be made "cacheable"
    by assigning hashable structures to the attributes whose names
    correspond with the names of the arguments.  For example, a datatype
    which accepts a dictionary of lookup values may publish this as a sorted
    series of tuples.   Given a previously un-cacheable type as::

        class LookupType(UserDefinedType):
            '''a custom type that accepts a dictionary as a parameter.

            this is the non-cacheable version, as "self.lookup" is not
            hashable.

            '''

            def __init__(self, lookup):
                self.lookup = lookup

            def get_col_spec(self, **kw):
                return "VARCHAR(255)"

            def bind_processor(self, dialect):
                # ...  works with "self.lookup" ...

    Where "lookup" is a dictionary.  The type will not be able to generate
    a cache key::

        >>> type_ = LookupType({"a": 10, "b": 20})
        >>> type_._static_cache_key
        <stdin>:1: SAWarning: UserDefinedType LookupType({'a': 10, 'b': 20}) will not
        produce a cache key because the ``cache_ok`` flag is not set to True.
        Set this flag to True if this type object's state is safe to use
        in a cache key, or False to disable this warning.
        symbol('no_cache')

    If we **did** set up such a cache key, it wouldn't be usable. We would
    get a tuple structure that contains a dictionary inside of it, which
    cannot itself be used as a key in a "cache dictionary" such as SQLAlchemy's
    statement cache, since Python dictionaries aren't hashable::

        >>> # set cache_ok = True
        >>> type_.cache_ok = True

        >>> # this is the cache key it would generate
        >>> key = type_._static_cache_key
        >>> key
        (<class '__main__.LookupType'>, ('lookup', {'a': 10, 'b': 20}))

        >>> # however this key is not hashable, will fail when used with
        >>> # SQLAlchemy statement cache
        >>> some_cache = {key: "some sql value"}
        Traceback (most recent call last): File "<stdin>", line 1,
        in <module> TypeError: unhashable type: 'dict'

    The type may be made cacheable by assigning a sorted tuple of tuples
    to the ".lookup" attribute::

        class LookupType(UserDefinedType):
            '''a custom type that accepts a dictionary as a parameter.

            The dictionary is stored both as itself in a private variable,
            and published in a public variable as a sorted tuple of tuples,
            which is hashable and will also return the same value for any
            two equivalent dictionaries.  Note it assumes the keys and
            values of the dictionary are themselves hashable.

            '''

            cache_ok = True

            def __init__(self, lookup):
                self._lookup = lookup

                # assume keys/values of "lookup" are hashable; otherwise
                # they would also need to be converted in some way here
                self.lookup = tuple(
                    (key, lookup[key]) for key in sorted(lookup)
                )

            def get_col_spec(self, **kw):
                return "VARCHAR(255)"

            def bind_processor(self, dialect):
                # ...  works with "self._lookup" ...

    Where above, the cache key for ``LookupType({"a": 10, "b": 20})`` will be::

        >>> LookupType({"a": 10, "b": 20})._static_cache_key
        (<class '__main__.LookupType'>, ('lookup', (('a', 10), ('b', 20))))

    .. versionadded:: 1.4.14 - added the ``cache_ok`` flag to allow
       some configurability of caching for :class:`.TypeDecorator` classes.

    .. versionadded:: 1.4.28 - added the :class:`.ExternalType` mixin which
       generalizes the ``cache_ok`` flag to both the :class:`.TypeDecorator`
       and :class:`.UserDefinedType` classes.

    .. seealso::

        :ref:`sql_caching`

    """  # noqa: E501

    @property
    def _static_cache_key(self):
        cache_ok = self.__class__.__dict__.get("cache_ok", None)

        if cache_ok is None:
            subtype_idx = self.__class__.__mro__.index(ExternalType)
            subtype = self.__class__.__mro__[max(subtype_idx - 1, 0)]

            util.warn(
                "%s %r will not produce a cache key because "
                "the ``cache_ok`` attribute is not set to True.  This can "
                "have significant performance implications including some "
                "performance degradations in comparison to prior SQLAlchemy "
                "versions.  Set this attribute to True if this type object's "
                "state is safe to use in a cache key, or False to "
                "disable this warning." % (subtype.__name__, self),
                code="cprf",
            )
        elif cache_ok is True:
            return super(ExternalType, self)._static_cache_key

        return NO_CACHE


class UserDefinedType(
    util.with_metaclass(VisitableCheckKWArg, ExternalType, TypeEngine)
):
    """Base for user defined types.

    This should be the base of new types.  Note that
    for most cases, :class:`.TypeDecorator` is probably
    more appropriate::

      import sqlalchemy.types as types

      class MyType(types.UserDefinedType):
          cache_ok = True

          def __init__(self, precision = 8):
              self.precision = precision

          def get_col_spec(self, **kw):
              return "MYTYPE(%s)" % self.precision

          def bind_processor(self, dialect):
              def process(value):
                  return value
              return process

          def result_processor(self, dialect, coltype):
              def process(value):
                  return value
              return process

    Once the type is made, it's immediately usable::

      table = Table('foo', metadata_obj,
          Column('id', Integer, primary_key=True),
          Column('data', MyType(16))
          )

    The ``get_col_spec()`` method will in most cases receive a keyword
    argument ``type_expression`` which refers to the owning expression
    of the type as being compiled, such as a :class:`_schema.Column` or
    :func:`.cast` construct.  This keyword is only sent if the method
    accepts keyword arguments (e.g. ``**kw``) in its argument signature;
    introspection is used to check for this in order to support legacy
    forms of this function.

    .. versionadded:: 1.0.0 the owning expression is passed to
       the ``get_col_spec()`` method via the keyword argument
       ``type_expression``, if it receives ``**kw`` in its signature.

    The :attr:`.UserDefinedType.cache_ok` class-level flag indicates if this
    custom :class:`.UserDefinedType` is safe to be used as part of a cache key.
    This flag defaults to ``None`` which will initially generate a warning
    when the SQL compiler attempts to generate a cache key for a statement
    that uses this type.  If the :class:`.UserDefinedType` is not guaranteed
    to produce the same bind/result behavior and SQL generation
    every time, this flag should be set to ``False``; otherwise if the
    class produces the same behavior each time, it may be set to ``True``.
    See :attr:`.UserDefinedType.cache_ok` for further notes on how this works.

    .. versionadded:: 1.4.28 Generalized the :attr:`.ExternalType.cache_ok`
       flag so that it is available for both :class:`.TypeDecorator` as well
       as :class:`.UserDefinedType`.

    """

    __visit_name__ = "user_defined"

    ensure_kwarg = "get_col_spec"

    def coerce_compared_value(self, op, value):
        """Suggest a type for a 'coerced' Python value in an expression.

        Default behavior for :class:`.UserDefinedType` is the
        same as that of :class:`.TypeDecorator`; by default it returns
        ``self``, assuming the compared value should be coerced into
        the same type as this one.  See
        :meth:`.TypeDecorator.coerce_compared_value` for more detail.

        """

        return self


class Emulated(object):
    """Mixin for base types that emulate the behavior of a DB-native type.

    An :class:`.Emulated` type will use an available database type
    in conjunction with Python-side routines and/or database constraints
    in order to approximate the behavior of a database type that is provided
    natively by some backends.  When a native-providing backend is in
    use, the native version of the type is used.  This native version
    should include the :class:`.NativeForEmulated` mixin to allow it to be
    distinguished from :class:`.Emulated`.

    Current examples of :class:`.Emulated` are:  :class:`.Interval`,
    :class:`.Enum`, :class:`.Boolean`.

    .. versionadded:: 1.2.0b3

    """

    def adapt_to_emulated(self, impltype, **kw):
        """Given an impl class, adapt this type to the impl assuming "emulated".

        The impl should also be an "emulated" version of this type,
        most likely the same class as this type itself.

        e.g.: sqltypes.Enum adapts to the Enum class.

        """
        return super(Emulated, self).adapt(impltype, **kw)

    def adapt(self, impltype, **kw):
        if hasattr(impltype, "adapt_emulated_to_native"):
            if self.native:
                # native support requested, dialect gave us a native
                # implementor, pass control over to it
                return impltype.adapt_emulated_to_native(self, **kw)
            else:
                # non-native support, let the native implementor
                # decide also, at the moment this is just to help debugging
                # as only the default logic is implemented.
                return impltype.adapt_native_to_emulated(self, **kw)
        else:
            if issubclass(impltype, self.__class__):
                return self.adapt_to_emulated(impltype, **kw)
            else:
                return super(Emulated, self).adapt(impltype, **kw)


class NativeForEmulated(object):
    """Indicates DB-native types supported by an :class:`.Emulated` type.

    .. versionadded:: 1.2.0b3

    """

    @classmethod
    def adapt_native_to_emulated(cls, impl, **kw):
        """Given an impl, adapt this type's class to the impl assuming
        "emulated".


        """
        impltype = impl.__class__
        return impl.adapt(impltype, **kw)

    @classmethod
    def adapt_emulated_to_native(cls, impl, **kw):
        """Given an impl, adapt this type's class to the impl assuming "native".

        The impl will be an :class:`.Emulated` class but not a
        :class:`.NativeForEmulated`.

        e.g.: postgresql.ENUM produces a type given an Enum instance.

        """
        return cls(**kw)


class TypeDecorator(ExternalType, SchemaEventTarget, TypeEngine):
    """Allows the creation of types which add additional functionality
    to an existing type.

    This method is preferred to direct subclassing of SQLAlchemy's
    built-in types as it ensures that all required functionality of
    the underlying type is kept in place.

    Typical usage::

      import sqlalchemy.types as types

      class MyType(types.TypeDecorator):
          '''Prefixes Unicode values with "PREFIX:" on the way in and
          strips it off on the way out.
          '''

          impl = types.Unicode

          cache_ok = True

          def process_bind_param(self, value, dialect):
              return "PREFIX:" + value

          def process_result_value(self, value, dialect):
              return value[7:]

          def copy(self, **kw):
              return MyType(self.impl.length)

    The class-level ``impl`` attribute is required, and can reference any
    :class:`.TypeEngine` class.  Alternatively, the :meth:`load_dialect_impl`
    method can be used to provide different type classes based on the dialect
    given; in this case, the ``impl`` variable can reference
    ``TypeEngine`` as a placeholder.

    The :attr:`.TypeDecorator.cache_ok` class-level flag indicates if this
    custom :class:`.TypeDecorator` is safe to be used as part of a cache key.
    This flag defaults to ``None`` which will initially generate a warning
    when the SQL compiler attempts to generate a cache key for a statement
    that uses this type.  If the :class:`.TypeDecorator` is not guaranteed
    to produce the same bind/result behavior and SQL generation
    every time, this flag should be set to ``False``; otherwise if the
    class produces the same behavior each time, it may be set to ``True``.
    See :attr:`.TypeDecorator.cache_ok` for further notes on how this works.

    Types that receive a Python type that isn't similar to the ultimate type
    used may want to define the :meth:`TypeDecorator.coerce_compared_value`
    method. This is used to give the expression system a hint when coercing
    Python objects into bind parameters within expressions. Consider this
    expression::

        mytable.c.somecol + datetime.date(2009, 5, 15)

    Above, if "somecol" is an ``Integer`` variant, it makes sense that
    we're doing date arithmetic, where above is usually interpreted
    by databases as adding a number of days to the given date.
    The expression system does the right thing by not attempting to
    coerce the "date()" value into an integer-oriented bind parameter.

    However, in the case of ``TypeDecorator``, we are usually changing an
    incoming Python type to something new - ``TypeDecorator`` by default will
    "coerce" the non-typed side to be the same type as itself. Such as below,
    we define an "epoch" type that stores a date value as an integer::

        class MyEpochType(types.TypeDecorator):
            impl = types.Integer

            epoch = datetime.date(1970, 1, 1)

            def process_bind_param(self, value, dialect):
                return (value - self.epoch).days

            def process_result_value(self, value, dialect):
                return self.epoch + timedelta(days=value)

    Our expression of ``somecol + date`` with the above type will coerce the
    "date" on the right side to also be treated as ``MyEpochType``.

    This behavior can be overridden via the
    :meth:`~TypeDecorator.coerce_compared_value` method, which returns a type
    that should be used for the value of the expression. Below we set it such
    that an integer value will be treated as an ``Integer``, and any other
    value is assumed to be a date and will be treated as a ``MyEpochType``::

        def coerce_compared_value(self, op, value):
            if isinstance(value, int):
                return Integer()
            else:
                return self

    .. warning::

       Note that the **behavior of coerce_compared_value is not inherited
       by default from that of the base type**.
       If the :class:`.TypeDecorator` is augmenting a
       type that requires special logic for certain types of operators,
       this method **must** be overridden.  A key example is when decorating
       the :class:`_postgresql.JSON` and :class:`_postgresql.JSONB` types;
       the default rules of :meth:`.TypeEngine.coerce_compared_value` should
       be used in order to deal with operators like index operations::

            class MyJsonType(TypeDecorator):
                impl = postgresql.JSON

                cache_ok = True

                def coerce_compared_value(self, op, value):
                    return self.impl.coerce_compared_value(op, value)

       Without the above step, index operations such as ``mycol['foo']``
       will cause the index value ``'foo'`` to be JSON encoded.

    """

    __visit_name__ = "type_decorator"

    _is_type_decorator = True

    def __init__(self, *args, **kwargs):
        """Construct a :class:`.TypeDecorator`.

        Arguments sent here are passed to the constructor
        of the class assigned to the ``impl`` class level attribute,
        assuming the ``impl`` is a callable, and the resulting
        object is assigned to the ``self.impl`` instance attribute
        (thus overriding the class attribute of the same name).

        If the class level ``impl`` is not a callable (the unusual case),
        it will be assigned to the same instance attribute 'as-is',
        ignoring those arguments passed to the constructor.

        Subclasses can override this to customize the generation
        of ``self.impl`` entirely.

        """

        if not hasattr(self.__class__, "impl"):
            raise AssertionError(
                "TypeDecorator implementations "
                "require a class-level variable "
                "'impl' which refers to the class of "
                "type being decorated"
            )
        self.impl = to_instance(self.__class__.impl, *args, **kwargs)

    coerce_to_is_types = (util.NoneType,)
    """Specify those Python types which should be coerced at the expression
    level to "IS <constant>" when compared using ``==`` (and same for
    ``IS NOT`` in conjunction with ``!=``).

    For most SQLAlchemy types, this includes ``NoneType``, as well as
    ``bool``.

    :class:`.TypeDecorator` modifies this list to only include ``NoneType``,
    as typedecorator implementations that deal with boolean types are common.

    Custom :class:`.TypeDecorator` classes can override this attribute to
    return an empty tuple, in which case no values will be coerced to
    constants.

    """

    class Comparator(TypeEngine.Comparator):
        """A :class:`.TypeEngine.Comparator` that is specific to
        :class:`.TypeDecorator`.

        User-defined :class:`.TypeDecorator` classes should not typically
        need to modify this.


        """

        __slots__ = ()

        def operate(self, op, *other, **kwargs):
            kwargs["_python_is_types"] = self.expr.type.coerce_to_is_types
            return super(TypeDecorator.Comparator, self).operate(
                op, *other, **kwargs
            )

        def reverse_operate(self, op, other, **kwargs):
            kwargs["_python_is_types"] = self.expr.type.coerce_to_is_types
            return super(TypeDecorator.Comparator, self).reverse_operate(
                op, other, **kwargs
            )

    @property
    def comparator_factory(self):
        if TypeDecorator.Comparator in self.impl.comparator_factory.__mro__:
            return self.impl.comparator_factory
        else:
            return type(
                "TDComparator",
                (TypeDecorator.Comparator, self.impl.comparator_factory),
                {},
            )

    def _gen_dialect_impl(self, dialect):
        """
        #todo
        """
        adapted = dialect.type_descriptor(self)
        if adapted is not self:
            return adapted

        # otherwise adapt the impl type, link
        # to a copy of this TypeDecorator and return
        # that.
        typedesc = self.load_dialect_impl(dialect).dialect_impl(dialect)
        tt = self.copy()
        if not isinstance(tt, self.__class__):
            raise AssertionError(
                "Type object %s does not properly "
                "implement the copy() method, it must "
                "return an object of type %s" % (self, self.__class__)
            )
        tt.impl = typedesc
        return tt

    @property
    def _type_affinity(self):
        """
        #todo
        """
        return self.impl._type_affinity

    def _set_parent(self, column, outer=False, **kw):
        """Support SchemaEventTarget"""

        super(TypeDecorator, self)._set_parent(column)

        if not outer and isinstance(self.impl, SchemaEventTarget):
            self.impl._set_parent(column, outer=False, **kw)

    def _set_parent_with_dispatch(self, parent):
        """Support SchemaEventTarget"""

        super(TypeDecorator, self)._set_parent_with_dispatch(
            parent, outer=True
        )

        if isinstance(self.impl, SchemaEventTarget):
            self.impl._set_parent_with_dispatch(parent)

    def type_engine(self, dialect):
        """Return a dialect-specific :class:`.TypeEngine` instance
        for this :class:`.TypeDecorator`.

        In most cases this returns a dialect-adapted form of
        the :class:`.TypeEngine` type represented by ``self.impl``.
        Makes usage of :meth:`dialect_impl`.
        Behavior can be customized here by overriding
        :meth:`load_dialect_impl`.

        """
        adapted = dialect.type_descriptor(self)
        if not isinstance(adapted, type(self)):
            return adapted
        else:
            return self.load_dialect_impl(dialect)

    def load_dialect_impl(self, dialect):
        """Return a :class:`.TypeEngine` object corresponding to a dialect.

        This is an end-user override hook that can be used to provide
        differing types depending on the given dialect.  It is used
        by the :class:`.TypeDecorator` implementation of :meth:`type_engine`
        to help determine what type should ultimately be returned
        for a given :class:`.TypeDecorator`.

        By default returns ``self.impl``.

        """
        return self.impl

    def _unwrapped_dialect_impl(self, dialect):
        """Return the 'unwrapped' dialect impl for this type.

        This is used by the :meth:`.DefaultDialect.set_input_sizes`
        method.

        """
        # some dialects have a lookup for a TypeDecorator subclass directly.
        # postgresql.INTERVAL being the main example
        typ = self.dialect_impl(dialect)

        # if we are still a type decorator, load the per-dialect switch
        # (such as what Variant uses), then get the dialect impl for that.
        if isinstance(typ, self.__class__):
            return typ.load_dialect_impl(dialect).dialect_impl(dialect)
        else:
            return typ

    def __getattr__(self, key):
        """Proxy all other undefined accessors to the underlying
        implementation."""
        return getattr(self.impl, key)

    def process_literal_param(self, value, dialect):
        """Receive a literal parameter value to be rendered inline within
        a statement.

        .. note::

            This method is called during the **SQL compilation** phase of a
            statement, when rendering a SQL string. Unlike other SQL
            compilation methods, it is passed a specific Python value to be
            rendered as a string. However it should not be confused with the
            :meth:`_types.TypeDecorator.process_bind_param` method, which is
            the more typical method that processes the actual value passed to a
            particular parameter at statement execution time.

        Custom subclasses of :class:`_types.TypeDecorator` should override
        this method to provide custom behaviors for incoming data values
        that are in the special case of being rendered as literals.

        The returned string will be rendered into the output string.

        """
        raise NotImplementedError()

    def process_bind_param(self, value, dialect):
        """Receive a bound parameter value to be converted.

        Custom subclasses of :class:`_types.TypeDecorator` should override
        this method to provide custom behaviors for incoming data values.
        This method is called at **statement execution time** and is passed
        the literal Python data value which is to be associated with a bound
        parameter in the statement.

        The operation could be anything desired to perform custom
        behavior, such as transforming or serializing data.
        This could also be used as a hook for validating logic.

        :param value: Data to operate upon, of any type expected by
         this method in the subclass.  Can be ``None``.
        :param dialect: the :class:`.Dialect` in use.

        .. seealso::

            :ref:`types_typedecorator`

            :meth:`_types.TypeDecorator.process_result_value`

        """

        raise NotImplementedError()

    def process_result_value(self, value, dialect):
        """Receive a result-row column value to be converted.

        Custom subclasses of :class:`_types.TypeDecorator` should override
        this method to provide custom behaviors for data values
        being received in result rows coming from the database.
        This method is called at **result fetching time** and is passed
        the literal Python data value that's extracted from a database result
        row.

        The operation could be anything desired to perform custom
        behavior, such as transforming or deserializing data.

        :param value: Data to operate upon, of any type expected by
         this method in the subclass.  Can be ``None``.
        :param dialect: the :class:`.Dialect` in use.

        .. seealso::

            :ref:`types_typedecorator`

            :meth:`_types.TypeDecorator.process_bind_param`


        """

        raise NotImplementedError()

    @util.memoized_property
    def _has_bind_processor(self):
        """memoized boolean, check if process_bind_param is implemented.

        Allows the base process_bind_param to raise
        NotImplementedError without needing to test an expensive
        exception throw.

        """

        return util.method_is_overridden(
            self, TypeDecorator.process_bind_param
        )

    @util.memoized_property
    def _has_literal_processor(self):
        """memoized boolean, check if process_literal_param is implemented."""

        return util.method_is_overridden(
            self, TypeDecorator.process_literal_param
        )

    def literal_processor(self, dialect):
        """Provide a literal processing function for the given
        :class:`.Dialect`.

        This is the method that fulfills the :class:`.TypeEngine`
        contract for literal value conversion which normally occurs via
        the :meth:`_types.TypeEngine.literal_processor` method.

        .. note::

            User-defined subclasses of :class:`_types.TypeDecorator` should
            **not** implement this method, and should instead implement
            :meth:`_types.TypeDecorator.process_literal_param` so that the
            "inner" processing provided by the implementing type is maintained.

        """
        if self._has_literal_processor:
            process_param = self.process_literal_param
        elif self._has_bind_processor:
            # the bind processor should normally be OK
            # for TypeDecorator since it isn't doing DB-level
            # handling, the handling here won't be different for bound vs.
            # literals.
            process_param = self.process_bind_param
        else:
            process_param = None

        if process_param:
            impl_processor = self.impl.literal_processor(dialect)
            if impl_processor:

                def process(value):
                    return impl_processor(process_param(value, dialect))

            else:

                def process(value):
                    return process_param(value, dialect)

            return process
        else:
            return self.impl.literal_processor(dialect)

    def bind_processor(self, dialect):
        """Provide a bound value processing function for the
        given :class:`.Dialect`.

        This is the method that fulfills the :class:`.TypeEngine`
        contract for bound value conversion which normally occurs via
        the :meth:`_types.TypeEngine.bind_processor` method.

        .. note::

            User-defined subclasses of :class:`_types.TypeDecorator` should
            **not** implement this method, and should instead implement
            :meth:`_types.TypeDecorator.process_bind_param` so that the "inner"
            processing provided by the implementing type is maintained.

        :param dialect: Dialect instance in use.

        """
        if self._has_bind_processor:
            process_param = self.process_bind_param
            impl_processor = self.impl.bind_processor(dialect)
            if impl_processor:

                def process(value):
                    return impl_processor(process_param(value, dialect))

            else:

                def process(value):
                    return process_param(value, dialect)

            return process
        else:
            return self.impl.bind_processor(dialect)

    @util.memoized_property
    def _has_result_processor(self):
        """memoized boolean, check if process_result_value is implemented.

        Allows the base process_result_value to raise
        NotImplementedError without needing to test an expensive
        exception throw.

        """

        return util.method_is_overridden(
            self, TypeDecorator.process_result_value
        )

    def result_processor(self, dialect, coltype):
        """Provide a result value processing function for the given
        :class:`.Dialect`.

        This is the method that fulfills the :class:`.TypeEngine`
        contract for bound value conversion which normally occurs via
        the :meth:`_types.TypeEngine.result_processor` method.

        .. note::

            User-defined subclasses of :class:`_types.TypeDecorator` should
            **not** implement this method, and should instead implement
            :meth:`_types.TypeDecorator.process_result_value` so that the
            "inner" processing provided by the implementing type is maintained.

        :param dialect: Dialect instance in use.
        :param coltype: A SQLAlchemy data type

        """
        if self._has_result_processor:
            process_value = self.process_result_value
            impl_processor = self.impl.result_processor(dialect, coltype)
            if impl_processor:

                def process(value):
                    return process_value(impl_processor(value), dialect)

            else:

                def process(value):
                    return process_value(value, dialect)

            return process
        else:
            return self.impl.result_processor(dialect, coltype)

    @util.memoized_property
    def _has_bind_expression(self):

        return (
            util.method_is_overridden(self, TypeDecorator.bind_expression)
            or self.impl._has_bind_expression
        )

    def bind_expression(self, bindparam):
        """Given a bind value (i.e. a :class:`.BindParameter` instance),
        return a SQL expression which will typically wrap the given parameter.

        .. note::

            This method is called during the **SQL compilation** phase of a
            statement, when rendering a SQL string. It is **not** necessarily
            called against specific values, and should not be confused with the
            :meth:`_types.TypeDecorator.process_bind_param` method, which is
            the more typical method that processes the actual value passed to a
            particular parameter at statement execution time.

        Subclasses of :class:`_types.TypeDecorator` can override this method
        to provide custom bind expression behavior for the type.  This
        implementation will **replace** that of the underlying implementation
        type.

        """
        return self.impl.bind_expression(bindparam)

    @util.memoized_property
    def _has_column_expression(self):
        """memoized boolean, check if column_expression is implemented.

        Allows the method to be skipped for the vast majority of expression
        types that don't use this feature.

        """

        return (
            util.method_is_overridden(self, TypeDecorator.column_expression)
            or self.impl._has_column_expression
        )

    def column_expression(self, column):
        """Given a SELECT column expression, return a wrapping SQL expression.

        .. note::

            This method is called during the **SQL compilation** phase of a
            statement, when rendering a SQL string. It is **not** called
            against specific values, and should not be confused with the
            :meth:`_types.TypeDecorator.process_result_value` method, which is
            the more typical method that processes the actual value returned
            in a result row subsequent to statement execution time.

        Subclasses of :class:`_types.TypeDecorator` can override this method
        to provide custom column expresion behavior for the type.  This
        implementation will **replace** that of the underlying implementation
        type.

        See the description of :meth:`_types.TypeEngine.column_expression`
        for a complete description of the method's use.

        """

        return self.impl.column_expression(column)

    def coerce_compared_value(self, op, value):
        """Suggest a type for a 'coerced' Python value in an expression.

        By default, returns self.   This method is called by
        the expression system when an object using this type is
        on the left or right side of an expression against a plain Python
        object which does not yet have a SQLAlchemy type assigned::

            expr = table.c.somecolumn + 35

        Where above, if ``somecolumn`` uses this type, this method will
        be called with the value ``operator.add``
        and ``35``.  The return value is whatever SQLAlchemy type should
        be used for ``35`` for this particular operation.

        """
        return self

    def copy(self, **kw):
        """Produce a copy of this :class:`.TypeDecorator` instance.

        This is a shallow copy and is provided to fulfill part of
        the :class:`.TypeEngine` contract.  It usually does not
        need to be overridden unless the user-defined :class:`.TypeDecorator`
        has local state that should be deep-copied.

        """

        instance = self.__class__.__new__(self.__class__)
        instance.__dict__.update(self.__dict__)
        return instance

    def get_dbapi_type(self, dbapi):
        """Return the DBAPI type object represented by this
        :class:`.TypeDecorator`.

        By default this calls upon :meth:`.TypeEngine.get_dbapi_type` of the
        underlying "impl".
        """
        return self.impl.get_dbapi_type(dbapi)

    def compare_values(self, x, y):
        """Given two values, compare them for equality.

        By default this calls upon :meth:`.TypeEngine.compare_values`
        of the underlying "impl", which in turn usually
        uses the Python equals operator ``==``.

        This function is used by the ORM to compare
        an original-loaded value with an intercepted
        "changed" value, to determine if a net change
        has occurred.

        """
        return self.impl.compare_values(x, y)

    @property
    def sort_key_function(self):
        return self.impl.sort_key_function

    def __repr__(self):
        return util.generic_repr(self, to_inspect=self.impl)


class Variant(TypeDecorator):
    """A wrapping type that selects among a variety of
    implementations based on dialect in use.

    The :class:`.Variant` type is typically constructed
    using the :meth:`.TypeEngine.with_variant` method.

    .. seealso:: :meth:`.TypeEngine.with_variant` for an example of use.

    """

    cache_ok = True

    def __init__(self, base, mapping):
        """Construct a new :class:`.Variant`.

        :param base: the base 'fallback' type
        :param mapping: dictionary of string dialect names to
          :class:`.TypeEngine` instances.

        """
        self.impl = base
        self.mapping = mapping

    @util.memoized_property
    def _static_cache_key(self):
        # TODO: needs tests in test/sql/test_compare.py
        return (self.__class__,) + (
            self.impl._static_cache_key,
            tuple(
                (key, self.mapping[key]._static_cache_key)
                for key in sorted(self.mapping)
            ),
        )

    def coerce_compared_value(self, operator, value):
        result = self.impl.coerce_compared_value(operator, value)
        if result is self.impl:
            return self
        else:
            return result

    def load_dialect_impl(self, dialect):
        if dialect.name in self.mapping:
            return self.mapping[dialect.name]
        else:
            return self.impl

    def _set_parent(self, column, outer=False, **kw):
        """Support SchemaEventTarget"""

        if isinstance(self.impl, SchemaEventTarget):
            self.impl._set_parent(column, **kw)
        for impl in self.mapping.values():
            if isinstance(impl, SchemaEventTarget):
                impl._set_parent(column, **kw)

    def _set_parent_with_dispatch(self, parent):
        """Support SchemaEventTarget"""

        if isinstance(self.impl, SchemaEventTarget):
            self.impl._set_parent_with_dispatch(parent)
        for impl in self.mapping.values():
            if isinstance(impl, SchemaEventTarget):
                impl._set_parent_with_dispatch(parent)

    def with_variant(self, type_, dialect_name):
        r"""Return a new :class:`.Variant` which adds the given
        type + dialect name to the mapping, in addition to the
        mapping present in this :class:`.Variant`.

        :param type\_: a :class:`.TypeEngine` that will be selected
         as a variant from the originating type, when a dialect
         of the given name is in use.
        :param dialect_name: base name of the dialect which uses
         this type. (i.e. ``'postgresql'``, ``'mysql'``, etc.)

        """

        if dialect_name in self.mapping:
            raise exc.ArgumentError(
                "Dialect '%s' is already present in "
                "the mapping for this Variant" % dialect_name
            )
        mapping = self.mapping.copy()
        mapping[dialect_name] = type_
        return Variant(self.impl, mapping)

    @property
    def comparator_factory(self):
        """express comparison behavior in terms of the base type"""
        return self.impl.comparator_factory


def _reconstitute_comparator(expression):
    return expression.comparator


def to_instance(typeobj, *arg, **kw):
    if typeobj is None:
        return NULLTYPE

    if callable(typeobj):
        return typeobj(*arg, **kw)
    else:
        return typeobj


def adapt_type(typeobj, colspecs):
    if isinstance(typeobj, type):
        typeobj = typeobj()
    for t in typeobj.__class__.__mro__[0:-1]:
        try:
            impltype = colspecs[t]
            break
        except KeyError:
            pass
    else:
        # couldn't adapt - so just return the type itself
        # (it may be a user-defined type)
        return typeobj
    # if we adapted the given generic type to a database-specific type,
    # but it turns out the originally given "generic" type
    # is actually a subclass of our resulting type, then we were already
    # given a more specific type than that required; so use that.
    if issubclass(typeobj.__class__, impltype):
        return typeobj
    return typeobj.adapt(impltype)
