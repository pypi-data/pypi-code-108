import pymongo
from py3db.log.Log import Log


class MongoDb(object):
    def __init__(self, client="mongodb://localhost:27017/", db_name="test", collection=None):
        self.client = pymongo.MongoClient(client)
        self.db = self.client[db_name]
        self.log = Log("mongodb.log")
        if collection:
            self.collection = self.db[collection]

    def insert_one(self, data_dict):
        try:
            self.collection.insert_one(data_dict)
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def inserts(self, data_dict_list):
        if not self.collection:
            print("连接失败，无法插入")
            return
        self.collection.insert_many(data_dict_list)

    def find_one(self, search_dict):
        return self.collection.find_one(search_dict)

    def finds(self, search_dict):
        return self.collection.find(search_dict)

    def delete_one(self, delete_dict):
        try:
            self.collection.delete_one(delete_dict)
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def deletes(self, delete_dict):
        try:
            self.collection.delete_many(delete_dict)
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def update_one(self, filter_dict, update_dict):
        try:
            self.collection.update_one(filter_dict, {"$set": update_dict})
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def updates(self, filter_dict, update_dict):
        try:
            self.collection.update_many(filter_dict, {"$set": update_dict})
        except Exception as e:
            self.log.call_error()
            self.log.error(str(e))

    def __str__(self) -> str:
        return ("client:{0}\n"
                + "db:{1}\n"
                + "collection:{2}\n").format(
            self.client,
            self.db,
            self.collection
        )


if __name__ == "__main__":
    mongodb = MongoDb(collection="video")
    mongodb.insert_one({"name": "hello world"})
