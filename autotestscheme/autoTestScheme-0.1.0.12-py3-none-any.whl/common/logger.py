import gevent.monkey
gevent.monkey.patch_all()
from . import common
from .._version import __version__
from loguru import logger


debug = logger.debug
info = logger.info
error = logger.error
warning = logger.warning
exception = logger.exception


logger.info("autoScheme Version:{}".format(__version__))


