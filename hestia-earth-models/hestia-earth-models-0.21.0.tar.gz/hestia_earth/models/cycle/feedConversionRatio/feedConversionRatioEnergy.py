from hestia_earth.models.utils.input import get_feed

from hestia_earth.models.log import logger
from . import MODEL

TERM_ID = 'feedConversionRatioEnergy'


def run(cycle: dict):
    feed = get_feed(cycle.get('inputs', []))
    logger.debug('model=%s, term=%s, feed=%s', MODEL, TERM_ID, feed)
    return feed
