from abc import ABC


class ditto_feature(ABC):
    def __init__(self, id, key, value):
        self.__id = id
        self.__key = key
        self.__value = value

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        self.__key = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def to_json(self):
        return {
            "properties": {
                self.__key: self.__value
            }
        }