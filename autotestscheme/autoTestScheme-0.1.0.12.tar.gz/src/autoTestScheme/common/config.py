# -*- coding: utf-8 -*-
#!/usr/bin/env python
__owner__ = "熊润"
__created_date__ = "2019/9/23"

from xml.dom import minidom

from . import logger

"""

Usage:
    配置读取

"""

import json
import os
import traceback


class Json(object):
    
    def __init__(self, path):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        if not os.path.exists(path):
            with open(path, 'w+')as f:f.write('{}')
        config_str = ''
        self._path = path
        try:
            with open(self._path, encoding='utf8') as f:
                config_str = f.read()
            self.json_str = json.loads(config_str)
        except Exception:
            logger.error('error json format,path:{0},error:{1}'.format(self._path, traceback.format_exc()))
            self.json_str = {}

    def get_json(self):
        '''
            获取json字符串
        '''
        config_content = None
        try:
            config_content = json.dumps(self.json_str, sort_keys=True, ensure_ascii=False,
										indent=4, separators=(',', ':'))
        except Exception:
            print(self.json_str)
            print(traceback.format_exc())
        return config_content
    
    def get_count(self):
        '''
            获取json的键值对的个数
        '''
        return len(self.get_keys())

    def get_items(self):
        '''
            获取json的键值对的个数
        '''
        return self.json_str.items()

    def get_key(self, key):
        '''
            获取key对应的value值
        '''
        return self.json_str[key]

    get = get_key

    def put_key(self, key, value):
        '''
            修改key
        '''
        self.json_str[key] = value
        self.save()

    put = put_key

    def remove_key(self, key):
        if key in list(self.json_str.keys()):
            del self.json_str[key]
            self.save()

    def save(self):
        '''
            保存修改至文件内获取
        '''
        with open(self._path, 'w+') as f:
            f.write(self.get_json())

    def get_keys(self):
        '''
            获取key列表
        '''
        return list(self.json_str.keys())

    def get_values(self):
        '''
            获取value列表
        '''
        return list(self.json_str.values())

    def get_object(self):
        return self.json_str

    def set_object(self, json_str):
        self.json_str = json_str
        self.save()


class AllureXml(object):

    def __init__(self):
        self.dom = minidom.getDOMImplementation().createDocument(None, 'environment', None)
        self.root = self.dom.documentElement

    def append_child(self, environment):
        for value in environment:
            tmp_element = self.dom.createElement('parameter')
            tmp_element1 = self.dom.createElement('key')
            tmp_element1.appendChild(self.dom.createTextNode(value[0]))
            tmp_element2 = self.dom.createElement('value')
            tmp_element2.appendChild(self.dom.createTextNode(str(value[1])))
            tmp_element.appendChild(tmp_element1)
            tmp_element.appendChild(tmp_element2)
            self.root.appendChild(tmp_element)

    def save_path(self, save_path):
        # 保存文件
        with open(save_path, 'w+', encoding='utf-8') as f:
            self.dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')
