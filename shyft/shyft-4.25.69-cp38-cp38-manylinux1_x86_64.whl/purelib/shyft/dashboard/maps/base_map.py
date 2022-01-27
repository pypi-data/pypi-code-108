import urllib
import abc
from typing import Any
from bokeh.models import BBoxTileSource


class BaseMap:

    @property
    @abc.abstractmethod
    def tiles(self) -> Any:
        pass


class BBoxTileBaseMap(BaseMap):
    def __init__(self, *, service: str, arguments: dict) -> None:
        super().__init__()
        self.service = service
        self.arguments = arguments

    @property
    def incomplete_url(self) -> str:
        return self.service + urllib.parse.urlencode(self.arguments)

    @property
    def url(self) -> str:
        return self.incomplete_url + '&bbox={XMIN},{YMIN},{XMAX},{YMAX}'

    @property
    def tiles(self) -> BBoxTileSource:
        return BBoxTileSource(url=self.url, snap_to_zoom=True)
