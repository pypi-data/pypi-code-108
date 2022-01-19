# sql/visitors.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""Visitor/traversal interface and library functions.

SQLAlchemy schema and expression constructs rely on a Python-centric
version of the classic "visitor" pattern as the primary way in which
they apply functionality.  The most common use of this pattern
is statement compilation, where individual expression classes match
up to rendering methods that produce a string result.   Beyond this,
the visitor system is also used to inspect expressions for various
information and patterns, as well as for the purposes of applying
transformations to expressions.

Examples of how the visit system is used can be seen in the source code
of for example the ``sqlalchemy.sql.util`` and the ``sqlalchemy.sql.compiler``
modules.  Some background on clause adaption is also at
https://techspot.zzzeek.org/2008/01/23/expression-transformations/ .

"""

from collections import deque
import itertools
import operator

from .. import exc
from .. import util
from ..util import langhelpers
from ..util import symbol

__all__ = [
    "iterate",
    "traverse_using",
    "traverse",
    "cloned_traverse",
    "replacement_traverse",
    "Traversible",
    "TraversibleType",
    "ExternalTraversal",
    "InternalTraversal",
]


def _generate_compiler_dispatch(cls):
    """Generate a _compiler_dispatch() external traversal on classes with a
    __visit_name__ attribute.

    """
    visit_name = cls.__visit_name__

    if "_compiler_dispatch" in cls.__dict__:
        # class has a fixed _compiler_dispatch() method.
        # copy it to "original" so that we can get it back if
        # sqlalchemy.ext.compiles overrides it.
        cls._original_compiler_dispatch = cls._compiler_dispatch
        return

    if not isinstance(visit_name, util.compat.string_types):
        raise exc.InvalidRequestError(
            "__visit_name__ on class %s must be a string at the class level"
            % cls.__name__
        )

    name = "visit_%s" % visit_name
    getter = operator.attrgetter(name)

    def _compiler_dispatch(self, visitor, **kw):
        """Look for an attribute named "visit_<visit_name>" on the
        visitor, and call it with the same kw params.

        """
        try:
            meth = getter(visitor)
        except AttributeError as err:
            return visitor.visit_unsupported_compilation(self, err, **kw)

        else:
            return meth(self, **kw)

    cls._compiler_dispatch = (
        cls._original_compiler_dispatch
    ) = _compiler_dispatch


class TraversibleType(type):
    """Metaclass which assigns dispatch attributes to various kinds of
    "visitable" classes.

    Attributes include:

    * The ``_compiler_dispatch`` method, corresponding to ``__visit_name__``.
      This is called "external traversal" because the caller of each visit()
      method is responsible for sub-traversing the inner elements of each
      object. This is appropriate for string compilers and other traversals
      that need to call upon the inner elements in a specific pattern.

    * internal traversal collections ``_children_traversal``,
      ``_cache_key_traversal``, ``_copy_internals_traversal``, generated from
      an optional ``_traverse_internals`` collection of symbols which comes
      from the :class:`.InternalTraversal` list of symbols.  This is called
      "internal traversal" MARKMARK

    """

    def __init__(cls, clsname, bases, clsdict):
        if clsname != "Traversible":
            if "__visit_name__" in clsdict:
                _generate_compiler_dispatch(cls)

        super(TraversibleType, cls).__init__(clsname, bases, clsdict)


class Traversible(util.with_metaclass(TraversibleType)):
    """Base class for visitable objects, applies the
    :class:`.visitors.TraversibleType` metaclass.

    """

    def __class_getitem__(cls, key):
        # allow generic classes in py3.9+
        return cls

    @util.preload_module("sqlalchemy.sql.traversals")
    def get_children(self, omit_attrs=(), **kw):
        r"""Return immediate child :class:`.visitors.Traversible`
        elements of this :class:`.visitors.Traversible`.

        This is used for visit traversal.

        \**kw may contain flags that change the collection that is
        returned, for example to return a subset of items in order to
        cut down on larger traversals, or to return child items from a
        different context (such as schema-level collections instead of
        clause-level).

        """

        traversals = util.preloaded.sql_traversals

        try:
            traverse_internals = self._traverse_internals
        except AttributeError:
            # user-defined classes may not have a _traverse_internals
            return []

        dispatch = traversals._get_children.run_generated_dispatch
        return itertools.chain.from_iterable(
            meth(obj, **kw)
            for attrname, obj, meth in dispatch(
                self, traverse_internals, "_generated_get_children_traversal"
            )
            if attrname not in omit_attrs and obj is not None
        )


class _InternalTraversalType(type):
    def __init__(cls, clsname, bases, clsdict):
        if cls.__name__ in ("InternalTraversal", "ExtendedInternalTraversal"):
            lookup = {}
            for key, sym in clsdict.items():
                if key.startswith("dp_"):
                    visit_key = key.replace("dp_", "visit_")
                    sym_name = sym.name
                    assert sym_name not in lookup, sym_name
                    lookup[sym] = lookup[sym_name] = visit_key
            if hasattr(cls, "_dispatch_lookup"):
                lookup.update(cls._dispatch_lookup)
            cls._dispatch_lookup = lookup

        super(_InternalTraversalType, cls).__init__(clsname, bases, clsdict)


def _generate_dispatcher(visitor, internal_dispatch, method_name):
    names = []
    for attrname, visit_sym in internal_dispatch:
        meth = visitor.dispatch(visit_sym)
        if meth:
            visit_name = ExtendedInternalTraversal._dispatch_lookup[visit_sym]
            names.append((attrname, visit_name))

    code = (
        ("    return [\n")
        + (
            ", \n".join(
                "        (%r, self.%s, visitor.%s)"
                % (attrname, attrname, visit_name)
                for attrname, visit_name in names
            )
        )
        + ("\n    ]\n")
    )
    meth_text = ("def %s(self, visitor):\n" % method_name) + code + "\n"
    # print(meth_text)
    return langhelpers._exec_code_in_env(meth_text, {}, method_name)


class InternalTraversal(util.with_metaclass(_InternalTraversalType, object)):
    r"""Defines visitor symbols used for internal traversal.

    The :class:`.InternalTraversal` class is used in two ways.  One is that
    it can serve as the superclass for an object that implements the
    various visit methods of the class.   The other is that the symbols
    themselves of :class:`.InternalTraversal` are used within
    the ``_traverse_internals`` collection.   Such as, the :class:`.Case`
    object defines ``_traverse_internals`` as ::

        _traverse_internals = [
            ("value", InternalTraversal.dp_clauseelement),
            ("whens", InternalTraversal.dp_clauseelement_tuples),
            ("else_", InternalTraversal.dp_clauseelement),
        ]

    Above, the :class:`.Case` class indicates its internal state as the
    attributes named ``value``, ``whens``, and ``else_``.    They each
    link to an :class:`.InternalTraversal` method which indicates the type
    of datastructure referred towards.

    Using the ``_traverse_internals`` structure, objects of type
    :class:`.InternalTraversible` will have the following methods automatically
    implemented:

    * :meth:`.Traversible.get_children`

    * :meth:`.Traversible._copy_internals`

    * :meth:`.Traversible._gen_cache_key`

    Subclasses can also implement these methods directly, particularly for the
    :meth:`.Traversible._copy_internals` method, when special steps
    are needed.

    .. versionadded:: 1.4

    """

    def dispatch(self, visit_symbol):
        """Given a method from :class:`.InternalTraversal`, return the
        corresponding method on a subclass.

        """
        name = self._dispatch_lookup[visit_symbol]
        return getattr(self, name, None)

    def run_generated_dispatch(
        self, target, internal_dispatch, generate_dispatcher_name
    ):
        try:
            dispatcher = target.__class__.__dict__[generate_dispatcher_name]
        except KeyError:
            # most of the dispatchers are generated up front
            # in sqlalchemy/sql/__init__.py ->
            # traversals.py-> _preconfigure_traversals().
            # this block will generate any remaining dispatchers.
            dispatcher = self.generate_dispatch(
                target.__class__, internal_dispatch, generate_dispatcher_name
            )
        return dispatcher(target, self)

    def generate_dispatch(
        self, target_cls, internal_dispatch, generate_dispatcher_name
    ):
        dispatcher = _generate_dispatcher(
            self, internal_dispatch, generate_dispatcher_name
        )
        # assert isinstance(target_cls, type)
        setattr(target_cls, generate_dispatcher_name, dispatcher)
        return dispatcher

    dp_has_cache_key = symbol("HC")
    """Visit a :class:`.HasCacheKey` object."""

    dp_has_cache_key_list = symbol("HL")
    """Visit a list of :class:`.HasCacheKey` objects."""

    dp_clauseelement = symbol("CE")
    """Visit a :class:`_expression.ClauseElement` object."""

    dp_fromclause_canonical_column_collection = symbol("FC")
    """Visit a :class:`_expression.FromClause` object in the context of the
    ``columns`` attribute.

    The column collection is "canonical", meaning it is the originally
    defined location of the :class:`.ColumnClause` objects.   Right now
    this means that the object being visited is a
    :class:`_expression.TableClause`
    or :class:`_schema.Table` object only.

    """

    dp_clauseelement_tuples = symbol("CTS")
    """Visit a list of tuples which contain :class:`_expression.ClauseElement`
    objects.

    """

    dp_clauseelement_list = symbol("CL")
    """Visit a list of :class:`_expression.ClauseElement` objects.

    """

    dp_clauseelement_tuple = symbol("CT")
    """Visit a tuple of :class:`_expression.ClauseElement` objects.

    """

    dp_executable_options = symbol("EO")

    dp_with_context_options = symbol("WC")

    dp_fromclause_ordered_set = symbol("CO")
    """Visit an ordered set of :class:`_expression.FromClause` objects. """

    dp_string = symbol("S")
    """Visit a plain string value.

    Examples include table and column names, bound parameter keys, special
    keywords such as "UNION", "UNION ALL".

    The string value is considered to be significant for cache key
    generation.

    """

    dp_string_list = symbol("SL")
    """Visit a list of strings."""

    dp_anon_name = symbol("AN")
    """Visit a potentially "anonymized" string value.

    The string value is considered to be significant for cache key
    generation.

    """

    dp_boolean = symbol("B")
    """Visit a boolean value.

    The boolean value is considered to be significant for cache key
    generation.

    """

    dp_operator = symbol("O")
    """Visit an operator.

    The operator is a function from the :mod:`sqlalchemy.sql.operators`
    module.

    The operator value is considered to be significant for cache key
    generation.

    """

    dp_type = symbol("T")
    """Visit a :class:`.TypeEngine` object

    The type object is considered to be significant for cache key
    generation.

    """

    dp_plain_dict = symbol("PD")
    """Visit a dictionary with string keys.

    The keys of the dictionary should be strings, the values should
    be immutable and hashable.   The dictionary is considered to be
    significant for cache key generation.

    """

    dp_dialect_options = symbol("DO")
    """Visit a dialect options structure."""

    dp_string_clauseelement_dict = symbol("CD")
    """Visit a dictionary of string keys to :class:`_expression.ClauseElement`
    objects.

    """

    dp_string_multi_dict = symbol("MD")
    """Visit a dictionary of string keys to values which may either be
    plain immutable/hashable or :class:`.HasCacheKey` objects.

    """

    dp_annotations_key = symbol("AK")
    """Visit the _annotations_cache_key element.

    This is a dictionary of additional information about a ClauseElement
    that modifies its role.  It should be included when comparing or caching
    objects, however generating this key is relatively expensive.   Visitors
    should check the "_annotations" dict for non-None first before creating
    this key.

    """

    dp_plain_obj = symbol("PO")
    """Visit a plain python object.

    The value should be immutable and hashable, such as an integer.
    The value is considered to be significant for cache key generation.

    """

    dp_named_ddl_element = symbol("DD")
    """Visit a simple named DDL element.

    The current object used by this method is the :class:`.Sequence`.

    The object is only considered to be important for cache key generation
    as far as its name, but not any other aspects of it.

    """

    dp_prefix_sequence = symbol("PS")
    """Visit the sequence represented by :class:`_expression.HasPrefixes`
    or :class:`_expression.HasSuffixes`.

    """

    dp_table_hint_list = symbol("TH")
    """Visit the ``_hints`` collection of a :class:`_expression.Select`
    object.

    """

    dp_setup_join_tuple = symbol("SJ")

    dp_memoized_select_entities = symbol("ME")

    dp_statement_hint_list = symbol("SH")
    """Visit the ``_statement_hints`` collection of a
    :class:`_expression.Select`
    object.

    """

    dp_unknown_structure = symbol("UK")
    """Visit an unknown structure.

    """

    dp_dml_ordered_values = symbol("DML_OV")
    """Visit the values() ordered tuple list of an
    :class:`_expression.Update` object."""

    dp_dml_values = symbol("DML_V")
    """Visit the values() dictionary of a :class:`.ValuesBase`
    (e.g. Insert or Update) object.

    """

    dp_dml_multi_values = symbol("DML_MV")
    """Visit the values() multi-valued list of dictionaries of an
    :class:`_expression.Insert` object.

    """

    dp_propagate_attrs = symbol("PA")
    """Visit the propagate attrs dict.  This hardcodes to the particular
    elements we care about right now."""


class ExtendedInternalTraversal(InternalTraversal):
    """Defines additional symbols that are useful in caching applications.

    Traversals for :class:`_expression.ClauseElement` objects only need to use
    those symbols present in :class:`.InternalTraversal`.  However, for
    additional caching use cases within the ORM, symbols dealing with the
    :class:`.HasCacheKey` class are added here.

    """

    dp_ignore = symbol("IG")
    """Specify an object that should be ignored entirely.

    This currently applies function call argument caching where some
    arguments should not be considered to be part of a cache key.

    """

    dp_inspectable = symbol("IS")
    """Visit an inspectable object where the return value is a
    :class:`.HasCacheKey` object."""

    dp_multi = symbol("M")
    """Visit an object that may be a :class:`.HasCacheKey` or may be a
    plain hashable object."""

    dp_multi_list = symbol("MT")
    """Visit a tuple containing elements that may be :class:`.HasCacheKey` or
    may be a plain hashable object."""

    dp_has_cache_key_tuples = symbol("HT")
    """Visit a list of tuples which contain :class:`.HasCacheKey`
    objects.

    """

    dp_inspectable_list = symbol("IL")
    """Visit a list of inspectable objects which upon inspection are
    HasCacheKey objects."""


class ExternalTraversal(object):
    """Base class for visitor objects which can traverse externally using
    the :func:`.visitors.traverse` function.

    Direct usage of the :func:`.visitors.traverse` function is usually
    preferred.

    """

    __traverse_options__ = {}

    def traverse_single(self, obj, **kw):
        for v in self.visitor_iterator:
            meth = getattr(v, "visit_%s" % obj.__visit_name__, None)
            if meth:
                return meth(obj, **kw)

    def iterate(self, obj):
        """Traverse the given expression structure, returning an iterator
        of all elements.

        """
        return iterate(obj, self.__traverse_options__)

    def traverse(self, obj):
        """Traverse and visit the given expression structure."""

        return traverse(obj, self.__traverse_options__, self._visitor_dict)

    @util.memoized_property
    def _visitor_dict(self):
        visitors = {}

        for name in dir(self):
            if name.startswith("visit_"):
                visitors[name[6:]] = getattr(self, name)
        return visitors

    @property
    def visitor_iterator(self):
        """Iterate through this visitor and each 'chained' visitor."""

        v = self
        while v:
            yield v
            v = getattr(v, "_next", None)

    def chain(self, visitor):
        """'Chain' an additional ClauseVisitor onto this ClauseVisitor.

        The chained visitor will receive all visit events after this one.

        """
        tail = list(self.visitor_iterator)[-1]
        tail._next = visitor
        return self


class CloningExternalTraversal(ExternalTraversal):
    """Base class for visitor objects which can traverse using
    the :func:`.visitors.cloned_traverse` function.

    Direct usage of the :func:`.visitors.cloned_traverse` function is usually
    preferred.


    """

    def copy_and_process(self, list_):
        """Apply cloned traversal to the given list of elements, and return
        the new list.

        """
        return [self.traverse(x) for x in list_]

    def traverse(self, obj):
        """Traverse and visit the given expression structure."""

        return cloned_traverse(
            obj, self.__traverse_options__, self._visitor_dict
        )


class ReplacingExternalTraversal(CloningExternalTraversal):
    """Base class for visitor objects which can traverse using
    the :func:`.visitors.replacement_traverse` function.

    Direct usage of the :func:`.visitors.replacement_traverse` function is
    usually preferred.

    """

    def replace(self, elem):
        """Receive pre-copied elements during a cloning traversal.

        If the method returns a new element, the element is used
        instead of creating a simple copy of the element.  Traversal
        will halt on the newly returned element if it is re-encountered.
        """
        return None

    def traverse(self, obj):
        """Traverse and visit the given expression structure."""

        def replace(elem):
            for v in self.visitor_iterator:
                e = v.replace(elem)
                if e is not None:
                    return e

        return replacement_traverse(obj, self.__traverse_options__, replace)


# backwards compatibility
Visitable = Traversible
VisitableType = TraversibleType
ClauseVisitor = ExternalTraversal
CloningVisitor = CloningExternalTraversal
ReplacingCloningVisitor = ReplacingExternalTraversal


def iterate(obj, opts=util.immutabledict()):
    r"""Traverse the given expression structure, returning an iterator.

    Traversal is configured to be breadth-first.

    The central API feature used by the :func:`.visitors.iterate`
    function is the
    :meth:`_expression.ClauseElement.get_children` method of
    :class:`_expression.ClauseElement` objects.  This method should return all
    the :class:`_expression.ClauseElement` objects which are associated with a
    particular :class:`_expression.ClauseElement` object. For example, a
    :class:`.Case` structure will refer to a series of
    :class:`_expression.ColumnElement` objects within its "whens" and "else\_"
    member variables.

    :param obj: :class:`_expression.ClauseElement` structure to be traversed

    :param opts: dictionary of iteration options.   This dictionary is usually
     empty in modern usage.

    """
    yield obj
    children = obj.get_children(**opts)

    if not children:
        return

    stack = deque([children])
    while stack:
        t_iterator = stack.popleft()
        for t in t_iterator:
            yield t
            stack.append(t.get_children(**opts))


def traverse_using(iterator, obj, visitors):
    """Visit the given expression structure using the given iterator of
    objects.

    :func:`.visitors.traverse_using` is usually called internally as the result
    of the :func:`.visitors.traverse` function.

    :param iterator: an iterable or sequence which will yield
     :class:`_expression.ClauseElement`
     structures; the iterator is assumed to be the
     product of the :func:`.visitors.iterate` function.

    :param obj: the :class:`_expression.ClauseElement`
     that was used as the target of the
     :func:`.iterate` function.

    :param visitors: dictionary of visit functions.  See :func:`.traverse`
     for details on this dictionary.

    .. seealso::

        :func:`.traverse`


    """
    for target in iterator:
        meth = visitors.get(target.__visit_name__, None)
        if meth:
            meth(target)
    return obj


def traverse(obj, opts, visitors):
    """Traverse and visit the given expression structure using the default
    iterator.

     e.g.::

        from sqlalchemy.sql import visitors

        stmt = select(some_table).where(some_table.c.foo == 'bar')

        def visit_bindparam(bind_param):
            print("found bound value: %s" % bind_param.value)

        visitors.traverse(stmt, {}, {"bindparam": visit_bindparam})

    The iteration of objects uses the :func:`.visitors.iterate` function,
    which does a breadth-first traversal using a stack.

    :param obj: :class:`_expression.ClauseElement` structure to be traversed

    :param opts: dictionary of iteration options.   This dictionary is usually
     empty in modern usage.

    :param visitors: dictionary of visit functions.   The dictionary should
     have strings as keys, each of which would correspond to the
     ``__visit_name__`` of a particular kind of SQL expression object, and
     callable functions  as values, each of which represents a visitor function
     for that kind of object.

    """
    return traverse_using(iterate(obj, opts), obj, visitors)


def cloned_traverse(obj, opts, visitors):
    """Clone the given expression structure, allowing modifications by
    visitors.

    Traversal usage is the same as that of :func:`.visitors.traverse`.
    The visitor functions present in the ``visitors`` dictionary may also
    modify the internals of the given structure as the traversal proceeds.

    The central API feature used by the :func:`.visitors.cloned_traverse`
    and :func:`.visitors.replacement_traverse` functions, in addition to the
    :meth:`_expression.ClauseElement.get_children`
    function that is used to achieve
    the iteration, is the :meth:`_expression.ClauseElement._copy_internals`
    method.
    For a :class:`_expression.ClauseElement`
    structure to support cloning and replacement
    traversals correctly, it needs to be able to pass a cloning function into
    its internal members in order to make copies of them.

    .. seealso::

        :func:`.visitors.traverse`

        :func:`.visitors.replacement_traverse`

    """

    cloned = {}
    stop_on = set(opts.get("stop_on", []))

    def deferred_copy_internals(obj):
        return cloned_traverse(obj, opts, visitors)

    def clone(elem, **kw):
        if elem in stop_on:
            return elem
        else:
            if id(elem) not in cloned:

                if "replace" in kw:
                    newelem = kw["replace"](elem)
                    if newelem is not None:
                        cloned[id(elem)] = newelem
                        return newelem

                cloned[id(elem)] = newelem = elem._clone(clone=clone, **kw)
                newelem._copy_internals(clone=clone, **kw)
                meth = visitors.get(newelem.__visit_name__, None)
                if meth:
                    meth(newelem)
            return cloned[id(elem)]

    if obj is not None:
        obj = clone(
            obj, deferred_copy_internals=deferred_copy_internals, **opts
        )
    clone = None  # remove gc cycles
    return obj


def replacement_traverse(obj, opts, replace):
    """Clone the given expression structure, allowing element
    replacement by a given replacement function.

    This function is very similar to the :func:`.visitors.cloned_traverse`
    function, except instead of being passed a dictionary of visitors, all
    elements are unconditionally passed into the given replace function.
    The replace function then has the option to return an entirely new object
    which will replace the one given.  If it returns ``None``, then the object
    is kept in place.

    The difference in usage between :func:`.visitors.cloned_traverse` and
    :func:`.visitors.replacement_traverse` is that in the former case, an
    already-cloned object is passed to the visitor function, and the visitor
    function can then manipulate the internal state of the object.
    In the case of the latter, the visitor function should only return an
    entirely different object, or do nothing.

    The use case for :func:`.visitors.replacement_traverse` is that of
    replacing a FROM clause inside of a SQL structure with a different one,
    as is a common use case within the ORM.

    """

    cloned = {}
    stop_on = {id(x) for x in opts.get("stop_on", [])}

    def deferred_copy_internals(obj):
        return replacement_traverse(obj, opts, replace)

    def clone(elem, **kw):
        if (
            id(elem) in stop_on
            or "no_replacement_traverse" in elem._annotations
        ):
            return elem
        else:
            newelem = replace(elem)
            if newelem is not None:
                stop_on.add(id(newelem))
                return newelem
            else:
                # base "already seen" on id(), not hash, so that we don't
                # replace an Annotated element with its non-annotated one, and
                # vice versa
                id_elem = id(elem)
                if id_elem not in cloned:
                    if "replace" in kw:
                        newelem = kw["replace"](elem)
                        if newelem is not None:
                            cloned[id_elem] = newelem
                            return newelem

                    cloned[id_elem] = newelem = elem._clone(**kw)
                    newelem._copy_internals(clone=clone, **kw)
                return cloned[id_elem]

    if obj is not None:
        obj = clone(
            obj, deferred_copy_internals=deferred_copy_internals, **opts
        )
    clone = None  # remove gc cycles
    return obj
