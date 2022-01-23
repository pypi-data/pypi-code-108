from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.cycle import get_excreta_N_total, get_max_rooting_depth, valid_site_type
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import get_total_nitrogen
from hestia_earth.models.utils.product import residue_nitrogen
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.term import get_rice_paddy_terms
from . import MODEL

TERM_ID = 'no3ToGroundwaterSoilFlux'


def _low_leaching_conditions(rooting_depth: float, clay: float, _s, rainfall: float, *args):
    return rooting_depth > 1.3 or clay > 50 or rainfall < 500


def _high_leaching_conditions(rooting_depth: float, _c, sand: float, rainfall: float, *args):
    return rooting_depth < 0.5 or sand > 85 or rainfall > 1300


def _flooded_rice_leaching_conditions(_rd, _c, _s, _r, product: dict):
    return product and product.get('term', {}).get('@id') in get_rice_paddy_terms()


def _other_leaching_conditions(*args):
    return True


NO3_LEACHING_FACTORS = {
    0.035: _flooded_rice_leaching_conditions,
    0.067: _low_leaching_conditions,
    0.23: _high_leaching_conditions,
    0.12: _other_leaching_conditions
}


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    clay = most_relevant_measurement_value(measurements, 'clayContent', end_date)
    sand = most_relevant_measurement_value(measurements, 'sandContent', end_date)
    rainfall = most_relevant_measurement_value(
        measurements, 'rainfallAnnual', end_date) or most_relevant_measurement_value(
        measurements, 'rainfallLongTermAnnualMean', end_date)
    rooting_depth = get_max_rooting_depth(cycle)
    primary_product = find_primary_product(cycle) or {}

    debugRequirements(model=MODEL, term=TERM_ID,
                      clayContent=clay,
                      sandContent=sand,
                      rainfall=rainfall,
                      rooting_depth=rooting_depth,
                      primary_product=primary_product.get('term', {}).get('@id'))

    should_run = all([valid_site_type(cycle), clay, sand, rainfall, rooting_depth])
    return should_run, [rooting_depth, clay, sand, rainfall, primary_product]


def get_leaching_factor(content_list_of_items: list):
    rooting_depth, clay, sand, rainfall, product = content_list_of_items
    # test conditions one by one and return the value associated for the first one that passes
    return next(
        (key for key, value in NO3_LEACHING_FACTORS.items() if value(rooting_depth, clay, sand, rainfall, product)),
        0.12  # default value for "Other"
    )


def _get_value(content_list_of_items: list):
    value = get_leaching_factor(content_list_of_items)
    logger.debug('model=%s, term=%s, leaching_factor=%s', MODEL, TERM_ID, value)
    return value * get_atomic_conversion(Units.KG_NO3, Units.TO_N)


def _run(cycle: dict, content_list_of_items: list):
    value = _get_value(content_list_of_items)
    residue = residue_nitrogen(cycle.get('products', []))
    # sums up all nitrogen content from all other "no3ToGroundwater" emissions
    N_total = list_sum(
        get_total_nitrogen(cycle.get('inputs', [])) + [get_excreta_N_total(cycle)] + [residue])
    return [_emission(value * N_total)]


def run(cycle: dict):
    should_run, content_list_of_items = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(cycle, content_list_of_items) if should_run else []
