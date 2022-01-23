from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.product import residue_nitrogen
from .no3ToGroundwaterSoilFlux import _should_run, _get_value
from . import MODEL

TERM_ID = 'no3ToGroundwaterCropResidueDecomposition'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, content_list_of_items: list):
    no3ToGroundwaterSoilFlux = _get_value(content_list_of_items)
    residue = residue_nitrogen(cycle.get('products', []))
    logger.debug('model=%s, term=%s, residue=%s', MODEL, TERM_ID, residue)
    return [_emission(residue * no3ToGroundwaterSoilFlux)]


def run(cycle: dict):
    should_run, content_list_of_items = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(cycle, content_list_of_items) if should_run else []
