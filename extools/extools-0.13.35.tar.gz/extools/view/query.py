"""extools.view.query - Query Sets for Extender
"""
from accpac import *
from extools.view import exview
from extools.view.exsql import exsql, columns_for_table
from extools.view.errors import ExViewError
from extools.message import logger_for_module

from contextlib import contextmanager

class ExQueryResult(object):
    """A single result entry for an ExQuery.

    :param rotoid: rotoid of the view the query is for.
    :type rotoid: str
    :param keys: key fields for index 0 of rotoid.
    :type keys: arg
    :param field: field values for the result entry.
    :type field: dict
    """

    def __init__(self, query, rotoid, *keys, **fields):
        self.log = logger_for_module("extools")
        self._rotoid = rotoid
        self._fields = fields
        self._keys = keys
        self.query = query

    def refresh(self):
        """Refresh the object through the view.

        :returns: None
        :raises: ExViewError
        """
        with self._view() as v:
            self._fields = v.to_dict()

    def update(self, **kvs):
        """Update the result with new values.

        :param kvs: key=value pairs.
        :returns: None
        :raises: ExViewError
        """
        with self._view() as v:
            v.update(**kvs)
            self._fields = v.to_dict()

    def delete(self):
        """Delete a result.

        :param kvs: key=value pairs.
        :returns: None
        :raises: ExViewError
        """
        with self._view() as v:
            v.delete()
            self.query.invalidate()

    @contextmanager
    def _view(self):
        seek_to = {f: self._fields[f] for f in self._keys}
        with exview(self._rotoid, seek_to=seek_to, compose=True) as exv:
            yield exv

    def __getattr__(self, attr):
        if attr.upper() in self._fields:
            return self._fields[attr.upper()]
        raise AttributeError()

    def __hash__(self):
        k = [self._fields[a] for a in self._keys]
        return hash(tuple(k))

    def __str__(self):
        return repr(self._fields)

    def __repr__(self):
        return "ExQueryResult('{}', '{}', {}, {})".format(
            self.query, self._rotoid, self._keys, self._fields)


class ExQueryIterator:
    """A general purpose, linear, iterator for ExQuery results.

    :param exquery: the query to iterate over.
    :type exquery: ExQuery
    """

    def __init__(self, exquery):
        self._exquery = exquery
        self._index = 0

    def __next__(self):
        self._exquery._execute()
        if self._index < len(self._exquery._results):
            self._index += 1
            return self._exquery._results[self._index - 1]
        raise StopIteration

class ExQuery:
    """A dynamic query builder with lazy execution.

    :param rotoid: view rotoid to query from
    :type rotoid: str
    :param terms: query terms (WHERE FIELD = VALUE)
    :type terms: params (CUSTOMER='1200', SHIPTO='WAREHS')
    """

    index = 20


    def __init__(self, rotoid, _offset=0, _limit=0,
                 _order_by="", _ascending=False, _parent_keys={},
                 **terms):
        self.log = logger_for_module('extools', box=None)
        self.rotoid = rotoid
        self.terms = terms
        self._results = []
        self._executed = False
        self._index = self.index
        self.index += 1 % 99
        self._offset = _offset
        self._limit = _limit
        self._order_by = _order_by
        self._ascending = _ascending
        self._parent_keys = _parent_keys
        for term, value in _parent_keys.items():
            if term not in terms:
                self.terms[term] = value
        self.log.debug("new exquery({} [{}], {})".format(
                rotoid, self._index, terms))

    @classmethod
    def from_results(cls, rotoid, results, **terms):
        """Create an ExQuery instance from an existing results set"""
        query = self._chained_self()
        query._results = results
        query._executed = True
        return query

    def _chained_self(self):
        """Returns a new instance of self, used for chaining."""
        return ExQuery(self.rotoid, _limit=self._limit, _offset=self._offset,
                   _order_by=self._order_by, _ascending=self._ascending,
                   **self.terms)

    def where(self, **terms):
        """Select records with fields matching terms.

        :param terms: query terms (WHERE FIELD = VALUE)
        :type terms: params (CUSTOMER='1200', SHIPTO='WAREHS')
        :returns: new ExQuery instance with new terms.
        :rtype: ExQuery
        """
        for term, value in terms.items():
            self.terms[term] = value
        return self._chained_self()

    def order_by(self, column, ascending=False):
        """Order the result set by a specific column.

        :param column: column to order query results by.
        :type column: str
        :param ascending: order by ascending values
        :type ascending: bool
        :returns: new ExQuery instance with new ordering.
        :rtype: ExQuery
        """
        self._order_by = column
        self._ascending = ascending
        return self._chained_self()

    def limit(self, limit):
        """Limit the number of results returned.

        :param limit: limit number of results.
        :type limit: str
        :returns: new ExQuery instance with new limit.
        :rtype: ExQuery
        """
        self._limit = limit
        return self._chained_self()

    def offset(self, offset):
        """Begin at an offset.

        :param offset: offset to start results from
        :type offset: int
        :returns: new ExQuery instance with new offset.
        :rtype: ExQuery
        """
        self._offset = offset
        return self._chained_self()

    def _build_query(self):
        criteria = []
        table = ""
        self.log.debug("building sql query")
        # Open a view instance to get at the metadata.
        with exview(self.rotoid, index=-1) as exv:
            for term, value in self.terms.items():
                # only quote character and bytes.
                self.log.debug('adding term {} = {}'.format(term, value))
                _type = exv._get_field_type(term)
                self.log.debug("field {} type {}".format(term, _type))
                if _type in [FT_CHAR, FT_BYTE]:
                    criteria.append("{} = '{}'".format(term, value))
                else:
                    criteria.append("{} = {}".format(term, value))
            table = exv.table or exv.table_name(self.rotoid)
        # build it
        query = "SELECT"

        if self._limit and not self._offset:
            query += " TOP ({})".format(self._limit)
        query += " * FROM {} WHERE {}".format(
                table, " AND ".join(criteria))
        if self._order_by:
            _dir = "ASC" if self._ascending else "DESC"
            query += " ORDER BY {} {}".format(self._order_by, _dir)
        if self._offset:
            query += " OFFSET {} ROWS".format(self._offset)
            if self._limit:
                query += " FETCH NEXT {} ROWS ONLY".format(self._limit)

        self.log.debug("query: {}".format(query))
        return query

    def _execute(self):
        # There are basically two cases:
        # - terms match a key: use view
        # - terms match no key: use exsql
        if self._executed:
            return
        queried = False
        self.log.debug("executing {}".format(str(self)))
        self._results.clear()
        with exview(self.rotoid) as exv:
            # If there is an index for this field type, use it.
            # If this is a unique
            index = exv._get_index_for_fields(self.terms.keys())
            self.log.debug("found index for terms {}: {}".format(
                    self.terms.keys(), index))
            if index is not None:
                original_order = exv._order
                temp = []
                try:
                    exv.order(index)
                    exv.recordClear()
                    for (key, value) in self.terms.items():
                        exv.put(key, value)
                    while exv.fetch():
                        temp.append(ExQueryResult(
                            self, self.rotoid,
                            *exv.indexes[0], **exv.to_dict()))
                    if self._offset:
                        if self._offset > len(temp):
                            temp = []
                        else:
                            temp = temp[self._offset:]
                    if self._limit:
                        temp = temp[:self._limit]
                    if self._order_by:
                        temp = sorted(
                                temp,
                                key=lambda e: getattr(
                                        e, self._order_by.lower()),
                                reverse=self._ascending)
                    self._results = temp
                    queried = True
                except ExViewError as e:
                    self.log.error("failed to populate through view: {}".format(e))
                finally:
                    exv.order(original_order)

        if not queried:
            with exsql() as exs:
                cols = columns_for_table(exs.table_name(self.rotoid))
                exs.query(self._build_query())
                while exs.fetch():
                    result = {col: exs.get(col) for col in cols}
                    self._results.append(ExQueryResult(
                            self, self.rotoid, *exv.indexes[0], **result))
        self._executed = True

    def _invalidate(self):
        self._executed = False

    def refresh(self):
        """Refresh the result, re-execute the query."""
        self._invalidate()
        self._execute()

    def __repr__(self):
        repr = ("ExQuery({}, _offset={}, _limit={}, _order_by={},"
                "        _ascending={}, _parent_keys={}, **{}").format(
                    self.rotoid, self._offset, self._limit, self._order_by,
                    self._ascending, self._parent_keys, self.terms)
        return repr

    def __str__(self):
        return repr(self)

    def __len__(self):
        self._execute()
        return len(self._results)

    def __iter__(self):
        self._execute()
        return ExQueryIterator(self)

    def __or__(self, other):
        if other.rotoid != self.rotoid:
            raise TypeError("ExQueries being combined must be for the same view.")
        terms = {}
        for term, value in self.terms.items():
            terms[term] = value
        for term, value in other.terms.items():
            terms[term] = value

        self._execute()
        other._execute()
        _results = list(set(self._results) | set(other._results))

        if _results and not self._order_by:
            sort_key = _results[0]._keys[0]
        else:
            sort_key = self._order_by
        _results = sorted(
                    _results,
                    key=lambda e: getattr(e, sort_key),
                    reverse=self._ascending)

        return self.from_results(self.rotoid, _results, **terms)

    def __and__(self, other):
        if other.rotoid != self.rotoid:
            raise TypeError("ExQueries being combined must be for the same view.")
        self._execute()
        other._execute()
        _results = list(set(self._results) & set(other._results))
        if _results and not self._order_by:
            sort_key = _results[0]._keys[0]
        else:
            sort_key = self._order_by
        _results = sorted(
                    _results,
                    key=lambda e: getattr(e, sort_key),
                    reverse=self._ascending)
        return self.from_results(self.rotoid, _results, **self.terms)

    def __sub__(self, other):
        if other.rotoid != self.rotoid:
            raise TypeError("ExQueries being combined must be for the same view.")
        self._execute()
        other._execute()
        _results = list(set(self._results) - set(other._results))
        if _results and not self._order_by:
            sort_key = _results[0]._keys[0]
        else:
            sort_key = self._order_by
        _results = sorted(
                    _results,
                    key=lambda e: getattr(e, sort_key),
                    reverse=self._ascending)
        return self.from_results(self.rotoid, _results, **self.terms)
