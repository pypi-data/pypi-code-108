from hestia_earth.schema import SiteSiteType
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import logger
from . import MODEL

MODEL_KEY = 'other'


def run(cycle: dict):
    site_type = cycle.get('site', {}).get('siteType')
    input = find_term_match(cycle.get('inputs', []), 'seed', None)
    is_complete = all([site_type == SiteSiteType.CROPLAND.value, input])
    logger.info('model=%s, key=%s, is_complete=%s', MODEL, MODEL_KEY, is_complete)
    return is_complete
