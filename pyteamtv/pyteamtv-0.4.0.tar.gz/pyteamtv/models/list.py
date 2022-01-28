from typing import TypeVar, Type, Generic, Optional, Callable

from pyteamtv.infra.requester import Requester

T = TypeVar('T')


class List(Generic[T]):
    def __init__(self,
                 content_class: Type[T],
                 requester: Requester,
                 method: str,
                 url: str,
                 item_filter: Optional[Callable[[T], bool]] = None):
        self.requester = requester
        self.content_class = content_class
        self.url = url

        data = requester.request(method, url)
        items = [content_class(
            requester,
            item
        ) for item in data]
        if item_filter:
            self._items = [
                item for item in items if item_filter(item)
            ]
        else:
            self._items = items

    def __getitem__(self, index) -> T:
        assert isinstance(index, (int, slice))
        return self._items[index]

    def __iter__(self):
        for item in self._items:
            yield item

    # TODO: not used yet, might be usefull
    # when /api/sportingEvent/<uuid>/videos endpoint exists
    # def create(self, body) -> T:
    #     data = self.requester.request('POST', self.url, body)
    #     item = self.content_class(
    #         self.requester,
    #         data
    #     )
    #     self._items.append(item)
    #     return item



