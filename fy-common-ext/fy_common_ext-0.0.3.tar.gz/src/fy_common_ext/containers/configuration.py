#! /usr/bin/python
# -*- coding: utf-8 -*-

import json


__all__ = [
    'Configuration',
]


class Configuration:
    # TODO

    def __init__(self):
        pass

    @classmethod
    def from_dict(cls, data: dict):
        # TODO
        pass

    @classmethod
    def from_json(cls, file_obj):
        if not hasattr(file_obj, 'read'):
            with open(file_obj, 'r', encoding='utf-8') as f:
                return cls.from_dict(json.load(f))
        return cls.from_dict(json.load(file_obj))
