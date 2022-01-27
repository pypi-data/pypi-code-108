# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import os
from typing import Text

import toml
from melon import ROOT_DIR, CONFIG_PATH


def __load():
    _content = toml.load(CONFIG_PATH)
    active_profile = _content.get('melon', {}).get('profiles', {}).get('active', '')
    if not active_profile:
        return _content

    active_profile_path = os.path.join(ROOT_DIR, f'melon-{active_profile}.toml')
    profile_content = toml.load(active_profile_path)

    __append(_content, profile_content)
    return _content


def __append(base_content, append_content):
    for k, v in append_content.items():
        if type(v) != dict or k not in base_content.keys():
            base_content[k] = v
            continue
        # 递归追加
        __append(base_content[k], v)


config = __load()


def get_config(keys_str: Text, default=None):
    target = config
    keys = keys_str.split('.')
    for key in keys:
        if not key:
            continue
        target = target.get(key, default)
    return target
