from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.cycle import valid_site_type
from .utils import get_liquid_slurry_sludge_P_total
from . import MODEL

TERM_ID = 'pToDrainageWaterSoilFlux'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, drainageClass: list):
    P_total, _ = get_liquid_slurry_sludge_P_total(cycle)
    value = 0.07 * (1 + P_total * 0.2/80) * (6 if drainageClass > 3 else 0)
    return [_emission(value)]


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    drainageClass = most_relevant_measurement_value(measurements, 'drainageClass', end_date)

    debugRequirements(model=MODEL, term=TERM_ID,
                      drainageClass=drainageClass)

    should_run = all([valid_site_type(cycle, True), drainageClass])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, drainageClass


def run(cycle: dict):
    should_run, drainageClass = _should_run(cycle)
    return _run(cycle, drainageClass) if should_run else []
