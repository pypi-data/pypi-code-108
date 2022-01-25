import bson
import pymongo

TEST_DB_PREFIX = "__test__"


class TestDb(object):
    # This isn't a test suite
    __test__ = False

    def __init__(self):
        connection = pymongo.MongoClient("mongodb://localhost:27017")
        database_name = TEST_DB_PREFIX + str(bson.ObjectId())
        self.db = connection[database_name]

    def __getattr__(self, attr):
        return getattr(self.db, attr)

    def __getitem__(self, item):
        return self.db[item]

    def clear_db(self):
        for collection_name in self.db.list_collection_names():
            if not collection_name.startswith("system."):
                self.db.drop_collection(collection_name)
