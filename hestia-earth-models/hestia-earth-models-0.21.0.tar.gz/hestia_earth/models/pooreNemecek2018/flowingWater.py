from hestia_earth.schema import MeasurementStatsDefinition, SiteSiteType

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.site import WATER_TYPES
from . import MODEL

TERM_ID = 'slowFlowingWater,fastFlowingWater'
SITE_TYPE_TO_TERM_ID = {
    SiteSiteType.RIVER_OR_STREAM.value: 'fastFlowingWater'
}


def measurement(term_id: str):
    logger.info('model=%s, term=%s', MODEL, TERM_ID)
    measurement = _new_measurement(term_id, MODEL)
    measurement['statsDefinition'] = MeasurementStatsDefinition.MODELLED.value
    return measurement


def _run(site: dict):
    site_type = site.get('siteType')
    term_id = SITE_TYPE_TO_TERM_ID.get(site_type, 'slowFlowingWater')
    return measurement(term_id)


def _should_run(site: dict):
    site_type = site.get('siteType')

    debugRequirements(model=MODEL, term=TERM_ID,
                      site_type=site_type)

    should_run = site_type in WATER_TYPES
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else None
