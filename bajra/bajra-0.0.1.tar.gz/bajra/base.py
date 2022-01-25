class ExecuteResult:
    def __init__(self, lastrowid=None, rowcount=None, rownumber=None):
        self.lastrowid = lastrowid
        self.rowcount = rowcount
        self.rownumber = rownumber

    def __repr__(self):
        return '<ExecuteResult lastrowid={} rowcount={} rownumber={}'.format(
            self.lastrowid, self.rowcount, self.rownumber
        )


class Row:
    def __init__(self, **kwargs):
        self._data = kwargs

    def __getattr__(self, item):
        return self._data[item]

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        for key, value in self._data.items():
            yield (key, value)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def __repr__(self):
        val = ' '.join('{}={}'.format(k, v) for k, v in self.items())
        return '<Row {}>'.format(val)


class RowResult:
    def __init__(self, data, row_class=Row):
        self._data = data
        self._row_class = row_class

    def _to_row(self, data):
        return self._row_class(**data)

    def __getitem__(self, idx):
        return self._to_row(self._data[idx])

    def __iter__(self):
        for datum in self._data:
            yield self._to_row(datum)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return '<RowResult items={}>'.format(len(self))


class Query:
    def __init__(self):
        self._parts = []
        self._dict_params = {}
        self._list_params = []

    def _fusion(self, sql):
        self._parts.append(sql.as_sql())
        self._append_params(sql.get_params())

    def _append_params(self, params):
        if isinstance(params, dict):
            self._dict_params.update(params)

        elif isinstance(params, (list, tuple, set)):
            self._list_params.extend(params)

    def append(self, sql, params=None, **kwargs):
        if params is None:
            params = kwargs

        if isinstance(sql, Query):
            self._fusion(sql)
            self._append_params(params)
            return self

        self._parts.append(sql)
        self._append_params(params)
        return self

    def as_sql(self):
        return '\n'.join(self._parts)

    def get_params(self):
        if self._dict_params:
            return self._dict_params

        elif self._list_params:
            return self._list_params

        return None

    def __repr__(self):
        return self.as_sql()
