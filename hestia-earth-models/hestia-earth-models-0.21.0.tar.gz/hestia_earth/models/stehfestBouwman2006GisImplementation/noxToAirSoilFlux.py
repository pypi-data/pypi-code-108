from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import get_total_nitrogen
from hestia_earth.models.utils.product import residue_nitrogen
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'noxToAirSoilFlux'


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {})
    residue = residue_nitrogen(cycle.get('products', []))
    N_total = list_sum(get_total_nitrogen(cycle.get('inputs', [])) + [residue])

    debugRequirements(model=MODEL, term=TERM_ID,
                      country=country.get('@id'),
                      residue=residue,
                      N_total=N_total)

    should_run = all([valid_site_type(cycle), country, N_total > 0])
    return should_run, country, N_total, residue


def _get_value(country: dict, N_total: float):
    value = safe_parse_float(get_lookup_value(country, 'ef_nox'))
    logger.info('model=%s, term=%s, N_total=%s, value=%s', MODEL, TERM_ID, N_total, value)
    return value * N_total


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(country: dict, N_total: float):
    value = _get_value(country, N_total)
    return [_emission(value)]


def run(cycle: dict):
    should_run, country, N_total, *args = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(country, N_total) if should_run else []
