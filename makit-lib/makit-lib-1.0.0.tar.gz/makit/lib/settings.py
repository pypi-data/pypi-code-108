#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：kevinleong1011@hotmail.com
@desc: 
"""
from typing import List

import yaml
from ._json import Json


class Settings(Json):
    """
    设置，可继承
    """

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.parents: List[Settings] = []

    def get(self, path=None, default=None, raise_error=False):
        v = super().get(path, default, raise_error)
        if v is None:
            for parent in self.parents:
                v = parent.get(path, default, raise_error)
                if v is not None:
                    return v
        else:
            return v

    def load_module(self, setting_module):
        for name in dir(setting_module):
            if name.startswith('_'):
                continue
            v = getattr(setting_module, name)
            self[name] = v
        return self

    def read_yaml(self, yaml_cfg):
        data = yaml.load(open(yaml_cfg, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
        self.update(**data)
        return self

    def inherit(self, *settings):
        for item in settings:
            if item in self.parents:
                continue
            self.parents.append(item)
        return self


def configure(**settings):
    """
    初始化设置
    :param settings:
    :return:
    """
    return Settings(**settings)


def inherit(*settings, **kwargs):
    """
    从已有设置继承并设置
    :param settings:
    :return:
    """
    setting = Settings(**kwargs)
    setting.inherit(*settings)
    return setting


def load_module(setting_module):
    return Settings().load_module(setting_module)
