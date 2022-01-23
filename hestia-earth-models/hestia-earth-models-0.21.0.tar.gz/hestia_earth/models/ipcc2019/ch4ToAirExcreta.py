from enum import Enum
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value, extract_grouped_data
from hestia_earth.utils.model import find_primary_product, filter_list_term_type
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugRequirements, debugMissingLookup, logger
from hestia_earth.models.utils.productivity import _get_productivity
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.input import total_excreta_vs
from . import MODEL

TERM_ID = 'ch4ToAirExcreta'
MONTH = 365.25/12


class DURAT(Enum):
    MONTH_1 = 'month_1'
    MONTH_3 = 'month_3'
    MONTH_4 = 'month_4'
    MONTH_6 = 'month_6'
    MONTH_12 = 'month_12'


# defaults to 12 months when no value per duration
DEFAULT_DURATION = DURAT.MONTH_12
DURAT_KEY = {
    DURAT.MONTH_1: lambda duration: duration <= 1 * MONTH,
    DURAT.MONTH_3: lambda duration: duration <= 3 * MONTH,
    DURAT.MONTH_4: lambda duration: duration <= 4 * MONTH,
    DURAT.MONTH_6: lambda duration: duration <= 6 * MONTH,
    DEFAULT_DURATION: lambda _duration: True
}


def _get_duration_key(duration: int):
    # returns the first matching duration up to the number of months
    return next((key for key in DURAT_KEY if duration and DURAT_KEY[key](duration)), DEFAULT_DURATION)


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(excretaKgVs: float, ch4_conv_factor: float, ch4_potential: float):
    value = excretaKgVs * ch4_potential * 0.67 * ch4_conv_factor / 100
    return [_emission(value)]


def _get_ch4_potential(country: dict, product: str, termType: str):
    # defaults to high productivity
    productivity_key = _get_productivity(country)
    lookup_name = f"region-{termType}-excretaManagement-ch4B0.csv"
    lookup = download_lookup(lookup_name)
    data_values = get_table_value(lookup, 'termid', country.get('@id'), column_name(product))
    debugMissingLookup(lookup_name, 'termid', country.get('@id'), product, data_values)
    return safe_parse_float(extract_grouped_data(data_values, productivity_key.value))


def _get_manure_managemet_conv_factor(term_id: str, ecoClimateZone: int, duration_key: DURAT_KEY):
    lookup_name = 'excretaManagement-ecoClimateZone-CH4conv.csv'
    lookup = download_lookup(lookup_name)
    data_values = get_table_value(lookup, 'termid', term_id, str(ecoClimateZone))
    debugMissingLookup(lookup_name, 'termid', term_id, ecoClimateZone, data_values)
    return safe_parse_float(
        extract_grouped_data(data_values, duration_key.value)
        or extract_grouped_data(data_values, DEFAULT_DURATION.value)
    ) if data_values else 0


def _get_ch4_conv_factor(cycle: dict):
    duration = cycle.get('cycleDuration')
    duration_key = _get_duration_key(duration)
    end_date = cycle.get('endDate')
    measurements = cycle.get('site', {}).get('measurements', [])
    ecoClimateZone = most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)
    practices = filter_list_term_type(cycle.get('practices', []), TermTermType.EXCRETAMANAGEMENT)
    practice_id = practices[0].get('term', {}).get('@id') if len(practices) > 0 else None

    debugRequirements(model=MODEL, term=TERM_ID,
                      duration_key=duration_key.value,
                      end_date=end_date,
                      ecoClimateZone=ecoClimateZone,
                      practice_id=practice_id)

    return _get_manure_managemet_conv_factor(practice_id, ecoClimateZone, duration_key) if practice_id else 0


def _should_run(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    product_id = primary_product.get('term', {}).get('@id')
    term_type = primary_product.get('term', {}).get('termType')

    excretaKgVs = total_excreta_vs(cycle.get('inputs', []))

    country = cycle.get('site', {}).get('country', {})
    ch4_potential = _get_ch4_potential(country, product_id, term_type) if product_id else None

    ch4_conv_factor = _get_ch4_conv_factor(cycle)

    debugRequirements(model=MODEL, term=TERM_ID,
                      excretaKgVs=excretaKgVs,
                      ch4_conv_factor=ch4_conv_factor,
                      ch4_potential=ch4_potential,
                      country=country.get('@id'),
                      primary_product=product_id,
                      term_type=term_type)

    should_run = all([excretaKgVs, ch4_conv_factor, ch4_potential])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, excretaKgVs, ch4_conv_factor, ch4_potential


def run(cycle: dict):
    should_run, excretaKgVs, ch4_conv_factor, ch4_potential = _should_run(cycle)
    return _run(excretaKgVs, ch4_conv_factor, ch4_potential) if should_run else []
