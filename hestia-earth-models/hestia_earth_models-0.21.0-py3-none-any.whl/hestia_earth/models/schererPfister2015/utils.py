from hestia_earth.models.utils.term import get_tillage_terms
from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import list_sum, safe_parse_float
from hestia_earth.utils.model import filter_list_term_type, find_primary_product

from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.input import match_lookup_value, get_total_phosphate

SLOPE_RANGE = [
    [0.0, 0.03, 1.2],
    [0.03, 0.08, 1.0],
    [0.08, 0.12, 1.2],
    [0.12, 0.16, 1.4],
    [0.16, 0.20, 1.6],
    [0.20, 0.24, 1.8],
    [0.24, 0.28, 2.0],
    [0.28, 0.32, 2.2]
]


def get_liquid_slurry_sludge_P_total(cycle: dict):
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.ORGANICFERTILIZER)
    lookup_name = 'OrganicFertilizerClassification'
    lss_P_total = list_sum(get_total_phosphate([
        i for i in inputs if match_lookup_value(i, col_name=lookup_name, col_value='Liquid, Slurry, Sewage Sludge')
    ]))
    not_lss_P_total = list_sum(get_total_phosphate([
        i for i in inputs if not match_lookup_value(i, col_name=lookup_name, col_value='Liquid, Slurry, Sewage Sludge')
    ]))
    return lss_P_total, not_lss_P_total


def _get_tillage(cycle: dict):
    tillage_ids = get_tillage_terms()
    practices = cycle.get('practices', [])
    return next(filter(lambda i: i.get('term', {}).get('@id') in tillage_ids, practices), {}).get('term')


def get_pcorr(slope: float):
    return next((element[2] for element in SLOPE_RANGE if slope >= element[0] and slope < element[1]), None)


def _get_C2_factor(term: dict):
    return safe_parse_float(get_lookup_value(term, 'C2_FACTORS'), None)


def get_practice_factor(site: dict):
    return safe_parse_float(get_lookup_value(site.get('country', {}), 'Practice_Factor'), None)


def get_p_ef_c1(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    return safe_parse_float(get_lookup_value(primary_product.get('term', {}), 'P_EF_C1'), None)


def get_ef_p_c2(cycle: dict):
    tillage = _get_tillage(cycle)
    country = cycle.get('site', {}).get('country', {})
    # TODO: handle pasture
    return safe_parse_float(get_lookup_value(country, 'EF_P_C2'), None) if tillage is None else _get_C2_factor(tillage)


def get_water(cycle: dict, precipitation: float):
    inputs = cycle.get('inputs', [])
    filter_irrigation = filter_list_term_type(inputs, TermTermType.WATER)
    irrigation = list_sum(get_total_value(filter_irrigation))
    return list_sum([irrigation/10, precipitation or 0])


def calculate_R(heavy_winter_precipitation: float, water: float):
    winter_precipitation = 1 if heavy_winter_precipitation > 0 else 0.1
    water_coeff = (587.8 - 1.219 * water) + (0.004105 * water ** 2) if water > 850 else (0.0483 * water ** 1.61)
    return water_coeff * winter_precipitation


def calculate_A(
    R: float,
    practice_factor: float,
    erodibility: float,
    slope_length: float,
    pcorr: float,
    p_ef_c1: float,
    ef_p_c2: float
):
    return R * practice_factor * erodibility * slope_length * pcorr * p_ef_c1 * ef_p_c2
