from .filter import Filter
import numpy as _np
import pandas as _pd
import datetime
from pymongo import MongoClient


class Column():
    def __init__(self, dataframe, name):
        self._mf = dataframe
        self._name = name

    def _query_value(self, qt, value):

        if isinstance(value, _np.datetime64):
            value = _pd.Timestamp(value).to_pydatetime()

        if self._mf._array_expand and self._name in self._mf.list_columns:
            return {"$elemMatch": {qt: value}}
        return {qt: value}

    def isin(self, array):
        return Filter(self._mf, {self._name: self._query_value("$in", array)}, lambda x: x[self._name].isin(array))

    def __eq__(self, value):
        return Filter(self._mf, {self._name: self._query_value("$eq", value)}, lambda x: x[self._name] == value)

    def __ne__(self, value):
        return Filter(self._mf, {self._name: self._query_value("$ne", value)}, lambda x: x[self._name] != value)

    def __ge__(self, value):
        return Filter(self._mf, {self._name: self._query_value("$gte", value)}, lambda x: x[self._name] >= value)

    def __gt__(self, value):
        return Filter(self._mf, {self._name: self._query_value("$gt", value)}, lambda x: x[self._name] > value)

    def __lt__(self, value):
        return Filter(self._mf, {self._name: self._query_value("$lt", value)}, lambda x: x[self._name] < value)

    def __le__(self, value):
        return Filter(self._mf, {self._name: self._query_value("$lte", value)}, lambda x: x[self._name] <= value)

    def unique(self):

        with MongoClient(self._mf._host) as client:
            db = client.get_database(self._mf._database)
            coll = db.get_collection(self._mf._collection)
            return _np.array(
                coll.distinct(
                    self._name,
                    self._mf._filter.config
                )
            )

    def agg(self, types):
        if isinstance(types, str):
            types = [types]

        pmap = {
            "mean": "$avg",
            "median": "$avg",
            "min": "$min",
            "max": "$max",
        }

        with MongoClient(self._mf._host) as client:
            db = client.get_database(self._mf._database)
            coll = db.get_collection(self._mf._collection)


            res = coll.aggregate([
                {"$match": self._mf._filter.config},
                {"$group": {
                    "_id": None,
                    **{t: {pmap[t]: f"${self._name}"} for t in types}
                }}
            ])

            res = list(res)[0]

        if res["median"] is None and "min" in res and res["min"] is not None:
            res["median"] = res["min"]
        if res["median"] is None and "max" in res and res["max"] is not None:
            res["median"] = res["max"]

        def flatten(t, el):
            if isinstance(el, list):
                a = _np.array(el)
                a = a[_pd.notnull(a)]
                return getattr(_np, t)(a)
            return el

        res = {k: flatten(k, v) for k, v in res.items() if k != "_id"}

        return _pd.Series(res, name=self._name)
