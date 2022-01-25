from db_hj3415 import mongo, sqlite, setting

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.WARNING)

# 한개의 스파이더에서 연속 3일분량의 데이터가 전달된다.


class MongoPipeline:
    # 몽고 데이터 베이스에 저장하는 파이프라인
    def __init__(self):
        self.db_setting = setting.load()
        logger.info(f"mongodb addr : {self.db_setting.mongo_addr}")

    def process_item(self, item, spider):
        """
        아이템 구조
            title = scrapy.Field()
            date = scrapy.Field()
            value = scrapy.Field()
        """
        if self.db_setting.active_mongo:
            print(f"\tIn the {self.__class__.__name__}...date : {item['date']} / title : {item['title']} / value : {item['value']}")
            mongo.MI(index=item['title']).save(mi_dict={"date": item['date'], "value": item['value']})
            return item
        else:
            print(f"\tIn the {self.__class__.__name__}...skipping save to db ", flush=True)
            return item


mi_db = sqlite.MI()


class SqlitePipeline:
    # Sqlite3 데이터 베이스에 저장하는 파이프라인
    def __init__(self):
        self.db_setting = setting.load()
        logger.info(f"sqlite3db addr : {self.db_setting.sqlite3_path}")

    def process_item(self, item, spider):
        if self.db_setting.active_sqlite3:
            print(f"\tIn the {self.__class__.__name__}...date : {item['date']} / title : {item['title']} / value : {item['value']}")
            mi_db.save(mi_dict={"date": item['date'], "value": item['value']}, index=item['title'])
            return item
        else:
            print(f"\tIn the SqlitePipeline...skipping save to db ", flush=True)
            return item
