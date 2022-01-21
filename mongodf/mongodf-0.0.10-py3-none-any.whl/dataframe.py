from .filter import Filter
from .column import Column
from .exception import MongoDfException
import pandas as _pd
import numpy as _np
from itertools import cycle, islice



class DataFrame():

    def __init__(self, _mongo, _database, _collection, _columns,
                 list_columns=[], filter=None, array_expand=True):
        self._mongo = _mongo
        self._database = _database
        self._collection = _collection
        self.columns = _columns
        self._filter = filter
        self._array_expand = array_expand
        if isinstance(list_columns, list):
            self.list_columns = set(list_columns)
        elif isinstance(list_columns, set):
            self.list_columns = list_columns
        else:
            self.list_columns = set([])

    def __getitem__(self, key):
        if isinstance(key, Filter):
            return DataFrame(
                self._mongo,
                self._database,
                self._collection,
                self.columns,
                filter=key.__and__(self._filter),
                array_expand=self._array_expand,
                list_columns=self.list_columns
            )

        if isinstance(key, list):
            if not all([k in self.columns for k in key]):
                raise MongoDfException("Not all columns available")

            return DataFrame(
                self._mongo,
                self._database,
                self._collection,
                key,
                filter=self._filter,
                array_expand=self._array_expand,
                list_columns=self.list_columns
            )

        if key in self.columns:
            return Column(self, key)
        else:
            raise MongoDfException(f"column {key} not found!")

    def __getattr__(self, key):
        if key in self.columns:
            return Column(self, key)
        else:
            raise MongoDfException(f"column {key} not found!")

    def compute(self, **kwargs):
        colfilter = {"_id": 0}
        colfilter.update(
            {c: 1 for c in list(set([*self.columns, *self._filter.config.keys()]))})

        query_data = self._collection.find(
            self._filter.config,
            colfilter
        )

        if self._array_expand:

            def create_df(d):
                try:
                    return _pd.DataFrame(d)
                except:
                    return _pd.DataFrame(d, index=[0])

            res_df = _pd.concat([
                create_df(d) for d in query_data
            ])

            if len(self._filter.config) != 0:
                res_df = res_df[self._filter.func(res_df)]


            res_df = res_df[ [c for c in self.columns if c in res_df.columns]]

            for c in [cc for cc in self.columns if cc not in res_df.columns]:
                res_df[c] = _np.nan

            return res_df

        return _pd.DataFrame(list(query_data))

    def example(self, n=20):

        def get_sampledata(name):
            data = list(self._collection.find(
                {name: {"$exists": True}}, {name: 1, "_id": 0})[:n])
            data = [d[name] for d in data]

            if len(data) < n:
                data = list(islice(cycle(data), n))

            return data

        res = {
            c: get_sampledata(c) for c in self.columns
        }
        out = _pd.DataFrame(res)
        if self._array_expand:
            for c in out.columns:
                if any([isinstance(d, list) for d in out[c].values]):
                    self.list_columns.add(c)
                    out[c] = out[c].map(
                        lambda x: x[0] if isinstance(x, list) else x)

        return out

    @property
    def dtypes(self):
        sample_df = self.example(20)
        return sample_df.dtypes
