from sidemash_sdk.Pagination import Pagination
from typing import Dict
from typing import List
from typing import TypeVar
import json

T = TypeVar('T')


class RestCollection:
    def __init__(self, url: str, pagination: Pagination, items: List[T]):
        self._type = "RestCollection" 
        self.url = url
        self.pagination = pagination
        self.items = items

    @staticmethod
    def _type(): 
        return "RestCollection"

    @staticmethod
    def from_json(js: str, item_converter):
        value = json.loads(js)
        items = list(map(lambda item: item_converter(item), value['items']))
        return RestCollection.from_dict({
            'url': value['url'],
            'pagination': value['pagination'],
            'items': items,
        })

    def __to_remote_dict(self):
        tuples = [
            ('url', self.url),
            ('pagination', self.pagination.__to_remote_dict()),
            ('items', list(map(lambda el: el.__to_remote_dict(), self.items)))
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('url', self.url),
            ('pagination', self.pagination.to_dict()),
            ('items', list(map(lambda el: el.to_dict(), self.items)))
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return RestCollection(d["url"],
                              Pagination.__from_remote_dict(d["pagination"]),
                              list(map(lambda el: el.__from_remote_dict(el), d["items"])))

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return RestCollection(d["url"],
                              Pagination.from_dict(d["pagination"]),
                              list(map(lambda el: el.from_dict(el), d["items"])))

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("RestCollection(url=" + self.url + 
                               ", pagination=" + repr(self.pagination) + 
                               ", items=" + repr(self.items) + ")")