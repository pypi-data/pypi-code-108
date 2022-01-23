from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.input import get_organic_fertilizer_N_total
from hestia_earth.models.utils.crop import get_N2ON_fertilizer_coeff_from_primary_product
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'n2OToAirOrganicFertilizerDirect'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, N_total: float):
    coefficient = get_N2ON_fertilizer_coeff_from_primary_product(cycle)
    value = N_total * coefficient * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    N_total = get_organic_fertilizer_N_total(cycle)

    debugRequirements(model=MODEL, term=TERM_ID,
                      N_total=N_total)

    should_run = valid_site_type(cycle, True) and (
        all([N_total]) or _is_term_type_complete(cycle, {'termType': 'fertilizer'})
    )
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, N_total


def run(cycle: dict):
    should_run, N_total = _should_run(cycle)
    return _run(cycle, N_total) if should_run else []
