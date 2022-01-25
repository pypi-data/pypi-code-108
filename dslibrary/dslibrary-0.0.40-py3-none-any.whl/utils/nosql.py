"""
Connections to NoSQL databases.
"""
import typing
from dslibrary.engine_intf import NoSqlDatabase, NoSQLReadOnly


def connect_to_nosql(uri: str, library: str=None, for_write: bool=False, **kwargs) -> NoSqlDatabase:
    """
    Connect to a NoSQL database based on a URI.
    """
    protocol = uri.split("://")[0]
    if protocol == "monogodb":
        try:
            import pymongo
        except ImportError:
            raise ImportWarning(f"pymongo library not available, can't open database: {uri}")
        db = pymongo.MongoClient(uri, **kwargs)
        intf = MongoDBAdapter(db)
    else:
        raise ValueError(f"protocol not supported: {protocol}")
    if not for_write:
        intf = NoSQLReadOnly(intf)
    return intf


class MongoDBAdapter(NoSqlDatabase):
    """
    Extremely simple interface to pymongo.
    """
    def __init__(self, db):
        self.db = db

    def query(self, collection: str, query: dict=None, limit: int=None, **kwargs) -> typing.Iterable[dict]:
        return self.db[collection].query(query, limit=limit, **kwargs)

    def insert(self, collection: str, doc: dict, **kwargs):
        resp = self.db[collection].insert_one(doc, **kwargs)
        return str(resp.inserted_id)

    def update(self, collection: str, filter: dict, changes: dict, upsert: bool=False, **kwargs):
        return self.db[collection].update_many(filter, update=changes, upsert=upsert, **kwargs).matched_count

    def delete(self, collection: str, filter: dict, **kwargs):
        return self.db[collection].delete_many(filter, **kwargs).modified_count
