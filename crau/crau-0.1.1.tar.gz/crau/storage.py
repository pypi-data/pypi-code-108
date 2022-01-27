from logging import getLogger
from pathlib import Path

from scrapy.utils.project import data_path
from warcio.warcwriter import WARCWriter

from .utils import write_warc_request_response

logger = getLogger(__file__)


class WARCCacheStorage:
    def __init__(self, settings):
        self.cache_dir = data_path(settings["HTTPCACHE_DIR"], create_dir=True)
        self.use_gzip = settings.getbool("HTTPCACHE_GZIP")
        self.expirations_secs = settings.getint("HTTPCACHE_EXPIRATION_SECS")
        self.filename = Path(cache_dir) / (
            spider.name + ".warc" + (".gz" if use_gzip else "")
        )
        # TODO: check other HTTPCACHE settings

    def open_spider(self, spider):
        self._fobj = open(self.filename, mode="wb")
        self._writer = WARCWriter(self._fobj, gzip=use_gzip)
        logger.debug(
            f"Using WARC cache storage in {self.filename}", extra={"spider": spider}
        )

    def close_spider(self, spider):
        self._writer.close()

    def retrieve_response(self, spider, request):
        # TODO: implement
        return None

    def store_response(self, spider, request, response):
        write_warc_request_response(self._writer, response)
