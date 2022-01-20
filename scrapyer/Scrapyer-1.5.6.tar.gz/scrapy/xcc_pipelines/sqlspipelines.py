
import pymysql
from datetime import datetime
from pymysql.err import IntegrityError
import logging
from pymysql import cursors
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
import json

class SQLSPipeline:
    def __init__(self, host, database, user, password, port,database_map):
        self.db = pymysql.connect(host=host, user=user, password=password, charset='utf8', port=port)
        self.database_map = database_map
        self.cursor = self.db.cursor()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(host=crawler.settings.get('MYSQL_HOST'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
            database_map=crawler.settings.get('DATABASE_MAP_PARAMS'),
        )

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        if item.__class__.__name__ in self.database_map.keys():
            database = database_map[item.__class__.__name__]
            data = item
            data = dict(item)
            keys = ', '.join(data.keys())
            values = ', '.join(['% s'] * len(data))
            sql = 'insert into "% s"."% s" (% s) values (% s)' % (database,item.table, keys, values)
            try:
                self.db.ping(reconnect=True)
                self.cursor.execute(sql, tuple(data.values()))
                self.db.commit()
                logging.debug('Crawl done.' )
            except IntegrityError:
                self.db.rollback()
                logging.info('去重 Skip .') 
        return item