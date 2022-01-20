"""
date:2021/10/26
auth:t.y.jie
"""
import json
import pymongo
from pymongo import MongoClient,ReadPreference
class mongodbPipeline(object):
    def __init__(self,MONGO_HOST,MONGO_PORT,MONGO_PSW,MONGO_USER,MONGO_DB):
        # 链接数据库
        # self.client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        # # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(MINGO_USER, MONGO_PSW)
        # MONGO_PORT = None
        if MONGO_PORT:
            # 兼容之前的settings配置
            mongo_url = 'mongodb://{0}:{1}@{2}:{3}/?authSource={4}&authMechanism=SCRAM-SHA-1'.format(MONGO_USER, MONGO_PSW,
                                                                                                     MONGO_HOST,MONGO_PORT, MONGO_DB)
            self.client = MongoClient(mongo_url)
            self.db = self.client[MONGO_DB]  # 获得数据库的句柄
        else:
            mongo_url = 'mongodb://{0}:{1}@{2}/?authSource={3}&replicaSet=rs01'.format(MONGO_USER, MONGO_PSW,
                                                                                                     MONGO_HOST,
                                                                                                     MONGO_DB)
            self.client = MongoClient(mongo_url)
            # 读写分离
            self.db = self.client.get_database(MONGO_DB, read_preference=ReadPreference.SECONDARY_PREFERRED)
        print("mongo_url:",mongo_url)
        # print('mongo_url',mongo_url)
        self.client = MongoClient(mongo_url)

        # self.coll = self.db[MONGO_COLL]  # 获得collection的句柄`

    @classmethod
    def from_crawler(cls, crawler):
        return cls(MONGO_HOST=crawler.settings.get('MONGO_HOST'),
                   MONGO_PORT=crawler.settings.get('MONGO_PORT'),
                   MONGO_PSW=crawler.settings.get('MONGO_PSW'),
                   MONGO_USER=crawler.settings.get('MONGO_USER'),
                   MONGO_DB=crawler.settings.get('MONGO_DB'),
                   # MONGO_COLL=crawler.settings.get('MONGO_COLL'),
                   )

    def process_item(self, item, spider):
        postItem = dict(item)
        if postItem.get("brand_id", None):  # brand_id :: int
            postItem["brand_id"] = int(postItem["brand_id"])
        if postItem.get("level", None):  # level :: int
            postItem["level"] = int(postItem["level"])
        if postItem.get("list_json", None):  # list_json :: json
            if isinstance(postItem["list_json"], dict):
                postItem["list_json"] = json.dumps(dict(postItem["list_json"]))
        if postItem.get("min_work_tp",None):  # min_work_tp :: int
            postItem["min_work_tp"] = int(postItem["min_work_tp"])
        if postItem.get("max_work_tp",None):  # max_work_tp :: int
            postItem["max_work_tp"] = int(postItem["max_work_tp"])
        if postItem.get("moq", None):  # moq :: int
            postItem["moq"] = int(postItem["moq"].replace(",",''))
        if postItem.get("mpq", None):  # mpq :: int
            postItem["mpq"] = int(postItem["mpq"].replace(",",''))
        if postItem.get("rough_weight", None):  # rough_weight :: float #注意单位是g
            postItem["rough_weight"] = int(postItem["rough_weight"])
        if postItem.get("title", None):  # title :: 去两端空格
            postItem["title"] = postItem["title"].strip()
        if postItem.get("sources",None):  # sources :: 去两端空格
            postItem["sources"] = postItem["sources"].strip()
        if postItem.get("brand_name", None):  # brand_name :: 去两端空格
            postItem["brand_name"] = postItem["brand_name"].strip()
        if postItem.get("category_id", None):  # category_id :: 去两端空格
            postItem["category_id"] = postItem["category_id"].strip()
        if postItem.get("category_name", None):  # category_name :: 去两端空格
            postItem["category_name"] = postItem["category_name"].strip()
        if postItem.get("brand_id", None):  # brand_id :: int
            postItem["brand_id"] = int(postItem["brand_id"])
        if postItem.get("level", None):  # level :: int
            postItem["level"] = int(postItem["level"])
        if postItem.get("list_json", None):  # list_json :: json
            if isinstance(postItem["list_json"], dict):
                postItem["list_json"] = json.dumps(dict(postItem["list_json"]))
        if postItem.get("min_work_tp",None):  # min_work_tp :: int
            postItem["min_work_tp"] = int(postItem["min_work_tp"])
        if postItem.get("max_work_tp",None):  # max_work_tp :: int
            postItem["max_work_tp"] = int(postItem["max_work_tp"])
        if postItem.get("moq", None):  # moq :: int
            postItem["moq"] = int(postItem["moq"])
        if postItem.get("mpq", None):  # mpq :: int
            postItem["mpq"] = int(postItem["mpq"])
        if postItem.get("rough_weight", None):  # rough_weight :: float #注意:单位g
            postItem["rough_weight"] = float(postItem["rough_weight"])
        try:
             # 把item转化成字典形式
            coll = self.db[item.table]
            coll.insert(postItem)  # 向数据库插入一条记录
        except pymongo.errors.DuplicateKeyError:
            print("去重了...",postItem)
        return item

    def close_spider(self):
        self.client.close()
