# -*- coding: future_fstrings -*-
import six
from abc import ABCMeta, abstractmethod


@six.add_metaclass(ABCMeta)
class Provider(object):

    def __init__(self, *args, **kwargs):
        self.setup(*args, **kwargs)

    def get_storage(self, storage_type, *args, **kwargs):
        storage_type_map = {
            "keyvalue": self.get_kvstorage
        }

        if storage_type in storage_type_map:
            instance = storage_type_map[storage_type](*args, **kwargs)
            return instance
        else:
            raise Exception("%s storage_type not found" % storage_type)

    def get_config(self, config_type, *args, **kwargs):
        config_map = {
            "config": self.generate_config
        }

        if config_type in config_map:
            instance = config_map[config_type](*args, **kwargs)
            return instance
        else:
            raise Exception("%s Config Type not found" % config_type)

    @abstractmethod
    def get_kvstorage(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def generate_config(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def setup(self, *args, **kwargs):
        raise NotImplementedError()
