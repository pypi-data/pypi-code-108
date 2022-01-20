
import pymysql
from datetime import datetime
from pymysql.err import IntegrityError
import logging
from pymysql import cursors
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
import json

class MySQLPipeline:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spide):
        self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        data = dict(item)
        if data.get("title", None):  # brand_id :: 出去型号两边空格
            data["title"] = data["title"].strip()
        if data.get("sources", None):  # sources :: 出去sources两边空格
            data["sources"] = data["sources"].strip()
        if data.get("brand_name", None):  # brand_name :: 出去品牌两边空格
            data["brand_name"] = data["brand_name"].strip()
        if data.get("category_id", None):  # category_id :: 出去category_id两边空格
            data["category_id"] = data["category_id"].strip()
        if data.get("list_json", None):  # list_json :: 出去category_id两边空格
            if isinstance(data["list_json"],dict):
                data["list_json"] =json.dumps(data["list_json"])
        keys = ', '.join(data.keys())
        values = ', '.join(['% s'] * len(data))
        sql = 'insert into % s (% s) values (% s)' % (item.table, keys, values)
        try:
            self.db.ping(reconnect=True)
            self.cursor.execute(sql, tuple(data.values()))
            self.db.commit()
            logging.debug('Crawl done.' )
        except IntegrityError:
            self.db.rollback()
            logging.info('去重 Skip .') 
        return item