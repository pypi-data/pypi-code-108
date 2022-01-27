from .column import Column
from .filter import Filter
from .dataframe import DataFrame
from pymongo import MongoClient


def from_mongo(host, database, collection,
               columns=None,
               filter={},
               array_expand=True):


    if columns is None:
        _client = MongoClient(host)
        _db = _client.get_database(database)
        _coll = _db.get_collection(collection)

        # compute the colums of the data
        _columns = list(_coll.aggregate([
            {"$project": {
                "data": {"$objectToArray": "$$ROOT"}
            }},
            {"$project": {"data": "$data.k"}},
            {"$unwind": "$data"},
            {"$group": {
                "_id": None,
                "keys": {"$addToSet": "$data"}
            }}
        ]))[0]["keys"]

        _columns = [c for c in _columns if c != "_id"]
    else:
        _columns = columns

    mf = DataFrame(host, database, collection, _columns,
                   filter=filter,
                   array_expand=array_expand)

    mf._filter = Filter(mf, filter)
    return mf


__all__ = ["Column", "Filter", "DataFrame", "from_mongo"]
