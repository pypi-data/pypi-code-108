# -*- coding: utf-8 -*-
'''
PicItem 
'''

import scrapy

#图排测试
class PicItem(scrapy.Item):
    # define the fields for your item here like:
    table = 'pic' # 测试库bd-crawler 正式库bd-spider
    def __init__(self, *args, **kwargs):
        table_params = {'table':kwargs.get('table',self.table)} if not kwargs.get('table_add','') \
            else {'table':kwargs.get('table',self.table)+kwargs.get('table_add','')}
        self.__dict__.update(table_params) 
        self._values = {}
        if args or kwargs and 'table' not in kwargs and 'table_add' not in kwargs:  # avoid creating dict for most common case
            for k, v in dict(*args, **kwargs).items():
                self[k] = v
    raw_img_url = scrapy.Field()
    img_url = scrapy.Field()
    title = scrapy.Field()
