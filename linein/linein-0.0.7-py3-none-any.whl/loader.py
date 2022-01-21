__all__ = ['M2MFieldWithThrough', 'Loader', 'NullLoader']

import warnings
from .exceptions import *


def data_to_instance(serializer_class, data):
    serializer = serializer_class(data=data)
    if not serializer.is_valid():
        warnings.warn("Invalid data for {}: {}\nErrors: {}".format(serializer_class, data, serializer.errors),
                      InvalidSerializerData)
    else:
        return serializer.save()


class M2MFieldWithThrough:
    def __init__(self, name, serializer_class, host_id_key=None):
        self.name = name
        self.serializer_class = serializer_class
        self.host_id_key = host_id_key

    def load_list(self, data_list, host_id=None):
        for data in data_list:
            self.load(data, host_id=host_id)

    def load(self, data, host_id=None):
        if self.host_id_key and host_id is not None:
            data[self.host_id_key] = host_id
        data_to_instance(self.serializer_class, data)


class Loader:
    model = None
    serializer_class = None
    m2m_fields_with_through = None

    def __init__(self, source=None):
        self.source = source

    def load(self):
        if not self.source or not self.serializer_class:
            return

        for raw_data in self.source:
            data = self.parse(raw_data)
            self.load_entry(data)

    def load_entry(self, data):
        m2m_data = {}
        if self.m2m_fields_with_through:
            for field in self.m2m_fields_with_through:
                m2m_data[field.name] = data.pop(field.name, [])

        instance = data_to_instance(self.serializer_class, data)

        if self.m2m_fields_with_through:
            for field in self.m2m_fields_with_through:
                field.load_list(m2m_data[field.name], host_id=instance.pk)

        return instance

    def parse(self, raw_data):
        return raw_data


class NullLoader(Loader):
    def load(self):
        return