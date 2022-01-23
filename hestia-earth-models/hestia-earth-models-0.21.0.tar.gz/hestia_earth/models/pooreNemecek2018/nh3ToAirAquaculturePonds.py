from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.site import FRESH_WATER_TYPES
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import total_excreta_tan
from hestia_earth.models.utils.practice import is_model_enabled
from hestia_earth.models.utils.aquacultureManagement import valid_site_type
from . import MODEL

TERM_ID = 'nh3ToAirAquaculturePonds'
EF_Aqua = {'TAN_NH3N': 0.3, 'MAX_NH3N': 0.00005}


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(excr_tan: float, yield_of_target_species: float, has_slow_flowing: bool):
    tan_value = excr_tan * EF_Aqua['TAN_NH3N']
    average_nh3n_per_m2_per_day = EF_Aqua['MAX_NH3N'] * 365 / yield_of_target_species if yield_of_target_species else 0
    value = min([tan_value, average_nh3n_per_m2_per_day]) if has_slow_flowing else tan_value
    value = value * get_atomic_conversion(Units.KG_NH3, Units.TO_N)
    return [_emission(value)]


def _should_run(cycle: dict):
    practices = cycle.get('practices', [])
    first_practice = practices[0] if len(practices) > 0 else None
    model_enabled = is_model_enabled(MODEL, TERM_ID, first_practice)
    excr_tan = total_excreta_tan(cycle.get('inputs', []))
    yield_of_target_species = list_sum(
        find_term_match(practices, 'yieldOfPrimaryAquacultureProductLiveweightPerM2').get('value', []))

    measurements = cycle.get('site', {}).get('measurements', [])
    is_freshwater = cycle.get('site', {}).get('siteType') in FRESH_WATER_TYPES
    has_slow_flowing = is_freshwater and find_term_match(measurements, 'slowFlowingWater', None) is not None

    set_to_zero = not valid_site_type(cycle)  # if site is not water, set value to 0

    debugRequirements(model=MODEL, term=TERM_ID,
                      model_enabled=model_enabled,
                      excr_tan=excr_tan,
                      yield_of_target_species=yield_of_target_species,
                      has_slow_flowing=has_slow_flowing,
                      is_freshwater=is_freshwater,
                      set_to_zero=set_to_zero)

    should_run = (
        model_enabled and excr_tan > 0 and (not has_slow_flowing or yield_of_target_species > 0)
    ) or set_to_zero
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, excr_tan, yield_of_target_species, has_slow_flowing, set_to_zero


def run(cycle: dict):
    should_run, excr_tan, yield_of_target_species, has_slow_flowing, set_to_zero = _should_run(cycle)
    return [_emission(0)] if set_to_zero else \
        _run(excr_tan, yield_of_target_species, has_slow_flowing) if should_run else []
