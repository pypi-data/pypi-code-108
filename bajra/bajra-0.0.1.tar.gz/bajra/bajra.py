from functools import wraps

from .base import Row, RowResult, Query, ExecuteResult


class Transaction:
    def __init__(self, bajra, rollback_on_exc=True, callback_exc=None):
        self._cater = bajra
        self._rollback_on_exc = rollback_on_exc
        self._callback_exc = callback_exc

    def __enter__(self):
        self._cater.begin()
        return self._cater

    def __exit__(self, exc_type, exc_value, traceback):
        returned_value = True

        if exc_type is not None and self._rollback_on_exc:
            self._cater.rollback()
            returned_value = False

        if exc_type is not None and callable(self._callback_exc):
            self._callback_exc(self._cater, exc_type, exc_value, traceback)
            returned_value = True

        self._cater.commit()
        return returned_value

    def __call__(self, fnx):
        @wraps(fnx)
        def _inner(*args, **kwargs):
            with self:
                fnx(*args, **kwargs)

        return _inner


class Bajra:
    def __init__(self, engine, autocommit=True):
        self._engine = engine
        self._autocommit = autocommit
        self._in_transaction = False

    def _commit(self):
        if self._autocommit and not self._in_transaction:
            self.commit()

    def _get_sql(self, query):
        if isinstance(query, Query):
            return query.as_sql()

        return query

    def _get_params(self, query, params):
        if not isinstance(query, Query):
            return params

        query_params = query.get_params()
        if not query_params:
            return params

        if not params:
            return query_params

        if type(query_params) != type(params):
            raise Exception("Diferent parameters format!")

        if isinstance(query_params, dict):
            query_params.update(params)
            return query_params

        query_params.extend(params)
        return query_params

    def query(self, query=None, params=None, **kwargs):
        q = Query()
        if params is None:
            params = kwargs

        if query is not None:
            q.append(query, params=params)

        return q

    def execute(self, query, params=None, **kwargs):
        if params is None:
            params = kwargs

        sql = self._get_sql(query)
        _params = self._get_params(query, params)
        data = self._engine.execute(sql, _params)
        self._commit()
        return ExecuteResult(**data)

    def fetchone(self, query, params=None, **kwargs):
        if params is None:
            params = kwargs

        sql = self._get_sql(query)
        _params = self._get_params(query, params)
        data = self._engine.fetchone(sql, _params)
        self._commit()
        if data is None:
            return None

        return Row(**data)

    def fetchall(self, query, params=None, **kwargs):
        if params is None:
            params = kwargs

        sql = self._get_sql(query)
        _params = self._get_params(query, params)
        data = self._engine.fetchall(sql, _params)
        self._commit()
        if data is None:
            return None

        return RowResult(data, row_class=Row)

    def reset(self):
        self._engine.reset()

    def commit(self):
        self._engine.commit()
        self._in_transaction = False

    def begin(self):
        self._engine.begin()
        self._in_transaction = True

    def rollback(self):
        if self._in_transaction:
            self._engine.rollback()
            self._in_transaction = False

    def transaction(self, rollback_on_exc=True, callback_exc=None):
        return Transaction(
            self, rollback_on_exc=rollback_on_exc, callback_exc=callback_exc
        )

    def mogrify(self, query, params=None, fnx=None):
        sql = self._get_sql(query)
        _params = self._get_params(query, params)
        data = self._engine.mogrify(sql, _params)
        if fnx is None:
            return data

        fnx(data)