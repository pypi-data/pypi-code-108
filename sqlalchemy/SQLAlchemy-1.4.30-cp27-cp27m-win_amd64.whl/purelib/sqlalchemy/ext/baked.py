# sqlalchemy/ext/baked.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
"""Baked query extension.

Provides a creational pattern for the :class:`.query.Query` object which
allows the fully constructed object, Core select statement, and string
compiled result to be fully cached.


"""

import logging

from .. import exc as sa_exc
from .. import util
from ..orm import exc as orm_exc
from ..orm import strategy_options
from ..orm.query import Query
from ..orm.session import Session
from ..sql import func
from ..sql import literal_column
from ..sql import util as sql_util
from ..util import collections_abc


log = logging.getLogger(__name__)


class Bakery(object):
    """Callable which returns a :class:`.BakedQuery`.

    This object is returned by the class method
    :meth:`.BakedQuery.bakery`.  It exists as an object
    so that the "cache" can be easily inspected.

    .. versionadded:: 1.2


    """

    __slots__ = "cls", "cache"

    def __init__(self, cls_, cache):
        self.cls = cls_
        self.cache = cache

    def __call__(self, initial_fn, *args):
        return self.cls(self.cache, initial_fn, args)


class BakedQuery(object):
    """A builder object for :class:`.query.Query` objects."""

    __slots__ = "steps", "_bakery", "_cache_key", "_spoiled"

    def __init__(self, bakery, initial_fn, args=()):
        self._cache_key = ()
        self._update_cache_key(initial_fn, args)
        self.steps = [initial_fn]
        self._spoiled = False
        self._bakery = bakery

    @classmethod
    def bakery(cls, size=200, _size_alert=None):
        """Construct a new bakery.

        :return: an instance of :class:`.Bakery`

        """

        return Bakery(cls, util.LRUCache(size, size_alert=_size_alert))

    def _clone(self):
        b1 = BakedQuery.__new__(BakedQuery)
        b1._cache_key = self._cache_key
        b1.steps = list(self.steps)
        b1._bakery = self._bakery
        b1._spoiled = self._spoiled
        return b1

    def _update_cache_key(self, fn, args=()):
        self._cache_key += (fn.__code__,) + args

    def __iadd__(self, other):
        if isinstance(other, tuple):
            self.add_criteria(*other)
        else:
            self.add_criteria(other)
        return self

    def __add__(self, other):
        if isinstance(other, tuple):
            return self.with_criteria(*other)
        else:
            return self.with_criteria(other)

    def add_criteria(self, fn, *args):
        """Add a criteria function to this :class:`.BakedQuery`.

        This is equivalent to using the ``+=`` operator to
        modify a :class:`.BakedQuery` in-place.

        """
        self._update_cache_key(fn, args)
        self.steps.append(fn)
        return self

    def with_criteria(self, fn, *args):
        """Add a criteria function to a :class:`.BakedQuery` cloned from this
        one.

        This is equivalent to using the ``+`` operator to
        produce a new :class:`.BakedQuery` with modifications.

        """
        return self._clone().add_criteria(fn, *args)

    def for_session(self, session):
        """Return a :class:`_baked.Result` object for this
        :class:`.BakedQuery`.

        This is equivalent to calling the :class:`.BakedQuery` as a
        Python callable, e.g. ``result = my_baked_query(session)``.

        """
        return Result(self, session)

    def __call__(self, session):
        return self.for_session(session)

    def spoil(self, full=False):
        """Cancel any query caching that will occur on this BakedQuery object.

        The BakedQuery can continue to be used normally, however additional
        creational functions will not be cached; they will be called
        on every invocation.

        This is to support the case where a particular step in constructing
        a baked query disqualifies the query from being cacheable, such
        as a variant that relies upon some uncacheable value.

        :param full: if False, only functions added to this
         :class:`.BakedQuery` object subsequent to the spoil step will be
         non-cached; the state of the :class:`.BakedQuery` up until
         this point will be pulled from the cache.   If True, then the
         entire :class:`_query.Query` object is built from scratch each
         time, with all creational functions being called on each
         invocation.

        """
        if not full and not self._spoiled:
            _spoil_point = self._clone()
            _spoil_point._cache_key += ("_query_only",)
            self.steps = [_spoil_point._retrieve_baked_query]
        self._spoiled = True
        return self

    def _effective_key(self, session):
        """Return the key that actually goes into the cache dictionary for
        this :class:`.BakedQuery`, taking into account the given
        :class:`.Session`.

        This basically means we also will include the session's query_class,
        as the actual :class:`_query.Query` object is part of what's cached
        and needs to match the type of :class:`_query.Query` that a later
        session will want to use.

        """
        return self._cache_key + (session._query_cls,)

    def _with_lazyload_options(self, options, effective_path, cache_path=None):
        """Cloning version of _add_lazyload_options."""
        q = self._clone()
        q._add_lazyload_options(options, effective_path, cache_path=cache_path)
        return q

    def _add_lazyload_options(self, options, effective_path, cache_path=None):
        """Used by per-state lazy loaders to add options to the
        "lazy load" query from a parent query.

        Creates a cache key based on given load path and query options;
        if a repeatable cache key cannot be generated, the query is
        "spoiled" so that it won't use caching.

        """

        key = ()

        if not cache_path:
            cache_path = effective_path

        for opt in options:
            if opt._is_legacy_option or opt._is_compile_state:
                ck = opt._generate_cache_key()
                if ck is None:
                    self.spoil(full=True)
                else:
                    assert not ck[1], (
                        "loader options with variable bound parameters "
                        "not supported with baked queries.  Please "
                        "use new-style select() statements for cached "
                        "ORM queries."
                    )
                    key += ck[0]

        self.add_criteria(
            lambda q: q._with_current_path(effective_path).options(*options),
            cache_path.path,
            key,
        )

    def _retrieve_baked_query(self, session):
        query = self._bakery.get(self._effective_key(session), None)
        if query is None:
            query = self._as_query(session)
            self._bakery[self._effective_key(session)] = query.with_session(
                None
            )
        return query.with_session(session)

    def _bake(self, session):
        query = self._as_query(session)
        query.session = None

        # in 1.4, this is where before_compile() event is
        # invoked
        statement = query._statement_20()

        # if the query is not safe to cache, we still do everything as though
        # we did cache it, since the receiver of _bake() assumes subqueryload
        # context was set up, etc.
        #
        # note also we want to cache the statement itself because this
        # allows the statement itself to hold onto its cache key that is
        # used by the Connection, which in itself is more expensive to
        # generate than what BakedQuery was able to provide in 1.3 and prior

        if statement._compile_options._bake_ok:
            self._bakery[self._effective_key(session)] = (
                query,
                statement,
            )

        return query, statement

    def to_query(self, query_or_session):
        """Return the :class:`_query.Query` object for use as a subquery.

        This method should be used within the lambda callable being used
        to generate a step of an enclosing :class:`.BakedQuery`.   The
        parameter should normally be the :class:`_query.Query` object that
        is passed to the lambda::

            sub_bq = self.bakery(lambda s: s.query(User.name))
            sub_bq += lambda q: q.filter(
                User.id == Address.user_id).correlate(Address)

            main_bq = self.bakery(lambda s: s.query(Address))
            main_bq += lambda q: q.filter(
                sub_bq.to_query(q).exists())

        In the case where the subquery is used in the first callable against
        a :class:`.Session`, the :class:`.Session` is also accepted::

            sub_bq = self.bakery(lambda s: s.query(User.name))
            sub_bq += lambda q: q.filter(
                User.id == Address.user_id).correlate(Address)

            main_bq = self.bakery(
                lambda s: s.query(
                Address.id, sub_bq.to_query(q).scalar_subquery())
            )

        :param query_or_session: a :class:`_query.Query` object or a class
         :class:`.Session` object, that is assumed to be within the context
         of an enclosing :class:`.BakedQuery` callable.


         .. versionadded:: 1.3


        """

        if isinstance(query_or_session, Session):
            session = query_or_session
        elif isinstance(query_or_session, Query):
            session = query_or_session.session
            if session is None:
                raise sa_exc.ArgumentError(
                    "Given Query needs to be associated with a Session"
                )
        else:
            raise TypeError(
                "Query or Session object expected, got %r."
                % type(query_or_session)
            )
        return self._as_query(session)

    def _as_query(self, session):
        query = self.steps[0](session)

        for step in self.steps[1:]:
            query = step(query)

        return query


class Result(object):
    """Invokes a :class:`.BakedQuery` against a :class:`.Session`.

    The :class:`_baked.Result` object is where the actual :class:`.query.Query`
    object gets created, or retrieved from the cache,
    against a target :class:`.Session`, and is then invoked for results.

    """

    __slots__ = "bq", "session", "_params", "_post_criteria"

    def __init__(self, bq, session):
        self.bq = bq
        self.session = session
        self._params = {}
        self._post_criteria = []

    def params(self, *args, **kw):
        """Specify parameters to be replaced into the string SQL statement."""

        if len(args) == 1:
            kw.update(args[0])
        elif len(args) > 0:
            raise sa_exc.ArgumentError(
                "params() takes zero or one positional argument, "
                "which is a dictionary."
            )
        self._params.update(kw)
        return self

    def _using_post_criteria(self, fns):
        if fns:
            self._post_criteria.extend(fns)
        return self

    def with_post_criteria(self, fn):
        """Add a criteria function that will be applied post-cache.

        This adds a function that will be run against the
        :class:`_query.Query` object after it is retrieved from the
        cache.    This currently includes **only** the
        :meth:`_query.Query.params` and :meth:`_query.Query.execution_options`
        methods.

        .. warning::  :meth:`_baked.Result.with_post_criteria`
           functions are applied
           to the :class:`_query.Query`
           object **after** the query's SQL statement
           object has been retrieved from the cache.   Only
           :meth:`_query.Query.params` and
           :meth:`_query.Query.execution_options`
           methods should be used.


        .. versionadded:: 1.2


        """
        return self._using_post_criteria([fn])

    def _as_query(self):
        q = self.bq._as_query(self.session).params(self._params)
        for fn in self._post_criteria:
            q = fn(q)
        return q

    def __str__(self):
        return str(self._as_query())

    def __iter__(self):
        return self._iter().__iter__()

    def _iter(self):
        bq = self.bq

        if not self.session.enable_baked_queries or bq._spoiled:
            return self._as_query()._iter()

        query, statement = bq._bakery.get(
            bq._effective_key(self.session), (None, None)
        )
        if query is None:
            query, statement = bq._bake(self.session)

        if self._params:
            q = query.params(self._params)
        else:
            q = query
        for fn in self._post_criteria:
            q = fn(q)

        params = q._params
        execution_options = dict(q._execution_options)
        execution_options.update(
            {
                "_sa_orm_load_options": q.load_options,
                "compiled_cache": bq._bakery,
            }
        )

        result = self.session.execute(
            statement, params, execution_options=execution_options
        )
        if result._attributes.get("is_single_entity", False):
            result = result.scalars()

        if result._attributes.get("filtered", False):
            result = result.unique()

        return result

    def count(self):
        """return the 'count'.

        Equivalent to :meth:`_query.Query.count`.

        Note this uses a subquery to ensure an accurate count regardless
        of the structure of the original statement.

        .. versionadded:: 1.1.6

        """

        col = func.count(literal_column("*"))
        bq = self.bq.with_criteria(lambda q: q._from_self(col))
        return bq.for_session(self.session).params(self._params).scalar()

    def scalar(self):
        """Return the first element of the first result or None
        if no rows present.  If multiple rows are returned,
        raises MultipleResultsFound.

        Equivalent to :meth:`_query.Query.scalar`.

        .. versionadded:: 1.1.6

        """
        try:
            ret = self.one()
            if not isinstance(ret, collections_abc.Sequence):
                return ret
            return ret[0]
        except orm_exc.NoResultFound:
            return None

    def first(self):
        """Return the first row.

        Equivalent to :meth:`_query.Query.first`.

        """

        bq = self.bq.with_criteria(lambda q: q.slice(0, 1))
        return (
            bq.for_session(self.session)
            .params(self._params)
            ._using_post_criteria(self._post_criteria)
            ._iter()
            .first()
        )

    def one(self):
        """Return exactly one result or raise an exception.

        Equivalent to :meth:`_query.Query.one`.

        """
        return self._iter().one()

    def one_or_none(self):
        """Return one or zero results, or raise an exception for multiple
        rows.

        Equivalent to :meth:`_query.Query.one_or_none`.

        .. versionadded:: 1.0.9

        """
        return self._iter().one_or_none()

    def all(self):
        """Return all rows.

        Equivalent to :meth:`_query.Query.all`.

        """
        return self._iter().all()

    def get(self, ident):
        """Retrieve an object based on identity.

        Equivalent to :meth:`_query.Query.get`.

        """

        query = self.bq.steps[0](self.session)
        return query._get_impl(ident, self._load_on_pk_identity)

    def _load_on_pk_identity(self, session, query, primary_key_identity, **kw):
        """Load the given primary key identity from the database."""

        mapper = query._raw_columns[0]._annotations["parententity"]

        _get_clause, _get_params = mapper._get_clause

        def setup(query):
            _lcl_get_clause = _get_clause
            q = query._clone()
            q._get_condition()
            q._order_by = None

            # None present in ident - turn those comparisons
            # into "IS NULL"
            if None in primary_key_identity:
                nones = set(
                    [
                        _get_params[col].key
                        for col, value in zip(
                            mapper.primary_key, primary_key_identity
                        )
                        if value is None
                    ]
                )
                _lcl_get_clause = sql_util.adapt_criterion_to_null(
                    _lcl_get_clause, nones
                )

            # TODO: can mapper._get_clause be pre-adapted?
            q._where_criteria = (
                sql_util._deep_annotate(_lcl_get_clause, {"_orm_adapt": True}),
            )

            for fn in self._post_criteria:
                q = fn(q)
            return q

        # cache the query against a key that includes
        # which positions in the primary key are NULL
        # (remember, we can map to an OUTER JOIN)
        bq = self.bq

        # add the clause we got from mapper._get_clause to the cache
        # key so that if a race causes multiple calls to _get_clause,
        # we've cached on ours
        bq = bq._clone()
        bq._cache_key += (_get_clause,)

        bq = bq.with_criteria(
            setup, tuple(elem is None for elem in primary_key_identity)
        )

        params = dict(
            [
                (_get_params[primary_key].key, id_val)
                for id_val, primary_key in zip(
                    primary_key_identity, mapper.primary_key
                )
            ]
        )

        result = list(bq.for_session(self.session).params(**params))
        l = len(result)
        if l > 1:
            raise orm_exc.MultipleResultsFound()
        elif l:
            return result[0]
        else:
            return None


@util.deprecated(
    "1.2", "Baked lazy loading is now the default implementation."
)
def bake_lazy_loaders():
    """Enable the use of baked queries for all lazyloaders systemwide.

    The "baked" implementation of lazy loading is now the sole implementation
    for the base lazy loader; this method has no effect except for a warning.

    """
    pass


@util.deprecated(
    "1.2", "Baked lazy loading is now the default implementation."
)
def unbake_lazy_loaders():
    """Disable the use of baked queries for all lazyloaders systemwide.

    This method now raises NotImplementedError() as the "baked" implementation
    is the only lazy load implementation.  The
    :paramref:`_orm.relationship.bake_queries` flag may be used to disable
    the caching of queries on a per-relationship basis.

    """
    raise NotImplementedError(
        "Baked lazy loading is now the default implementation"
    )


@strategy_options.loader_option()
def baked_lazyload(loadopt, attr):
    """Indicate that the given attribute should be loaded using "lazy"
    loading with a "baked" query used in the load.

    """
    return loadopt.set_relationship_strategy(attr, {"lazy": "baked_select"})


@baked_lazyload._add_unbound_fn
@util.deprecated(
    "1.2",
    "Baked lazy loading is now the default "
    "implementation for lazy loading.",
)
def baked_lazyload(*keys):
    return strategy_options._UnboundLoad._from_keys(
        strategy_options._UnboundLoad.baked_lazyload, keys, False, {}
    )


@baked_lazyload._add_unbound_all_fn
@util.deprecated(
    "1.2",
    "Baked lazy loading is now the default "
    "implementation for lazy loading.",
)
def baked_lazyload_all(*keys):
    return strategy_options._UnboundLoad._from_keys(
        strategy_options._UnboundLoad.baked_lazyload, keys, True, {}
    )


baked_lazyload = baked_lazyload._unbound_fn
baked_lazyload_all = baked_lazyload_all._unbound_all_fn

bakery = BakedQuery.bakery
