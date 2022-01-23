from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value, extract_grouped_data
from hestia_earth.utils.model import find_primary_product, filter_list_term_type, find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.input import get_feed
from hestia_earth.models.utils.emission import _new_emission
from . import MODEL

TERM_ID = 'ch4ToAirEntericFermentation'
LOOKUP_TABLE = 'liveAnimal-ipcc2019Tier2Ch4.csv'


def _emission(value: float, sd: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['sd'] = [sd]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(feed: float, enteric_factor: float, enteric_sd: float):
    value = feed * enteric_factor / 55.65
    return [_emission(value, enteric_sd)]


DE_NDF_MAPPING = {
    'high_DE_low_NDF': lambda DE, NDF: DE >= 70 and NDF < 35,
    'high_DE_high_NDF': lambda DE, NDF: DE >= 70 and NDF >= 35,
    'medium_DE_high_NDF': lambda DE, NDF: DE >= 63 and DE < 70 and NDF > 37,
    'low_DE_high_NDF': lambda DE, NDF: DE < 62 and NDF >= 38
}

DE_MAPPING = {
    'high_medium_DE': lambda DE, _: DE > 63,
    'medium_DE': lambda DE, _: DE > 62 and DE < 72,
    'low_DE': lambda DE, _: DE <= 62,
    'high_DE': lambda DE, _: DE >= 72,
    'high_DE_ionophore': lambda DE, ionophore: DE > 75 and ionophore
}


def _get_grouped_data_key(keys: list, DE: float, NDF: float, ionophore: bool):
    # test conditions one by one and return the key associated for the first one that passes
    return next(
        (key for key in keys if key in DE_NDF_MAPPING and DE_NDF_MAPPING[key](DE, NDF)),
        None
    ) or next(
        (key for key in keys if key in DE_MAPPING and DE_MAPPING[key](DE, ionophore)),
        None
    )


def _extract_groupped_data(value: str, DE: float, NDF: float, ionophore: bool):
    value_keys = [val.split(':')[0] for val in value.split(';')]
    value_key = _get_grouped_data_key(value_keys, DE, NDF, ionophore)
    return safe_parse_float(extract_grouped_data(value, value_key))


def _get_liveAnimal_lookup_value(lookup, term_id: str, lookup_col: str, DE: float, NDF: float, ionophore: bool):
    value = get_table_value(lookup, 'termid', term_id, column_name(lookup_col)) if term_id else None
    return value if value is None or ':' not in value else _extract_groupped_data(value, DE, NDF, ionophore)


def _get_crop_property_average(inputs: list, col_name: str):
    lookup = download_lookup('crop-property.csv', True)
    total_value = list_sum([list_sum(i.get('value', [])) for i in inputs])
    return (list_sum([
        safe_parse_float(
            extract_grouped_data(
                get_table_value(lookup, 'termid', i.get('term', {}).get('@id'), column_name(col_name)), 'Avg'
            )
        ) * list_sum(i.get('value', [])) for i in inputs
    ]) / total_value) if total_value > 0 else 0


def _get_DE_type(lookup, term_id: str):
    return get_table_value(lookup, 'termid', term_id, column_name('Digestibility'))


def _is_ionophore(cycle: dict, total_feed: float):
    inputs = cycle.get('inputs', [])
    has_input = find_term_match(inputs, 'ionophores', None) is not None
    maize_input = find_term_match(inputs, 'maizeSteamFlaked', {'value': 0})
    maize_feed = get_feed([maize_input])
    return has_input and maize_feed / total_feed >= 0.9


def _should_run(cycle: dict):
    primary_product = find_primary_product(cycle)
    term_id = primary_product.get('term', {}).get('@id') if primary_product else None

    lookup = download_lookup(LOOKUP_TABLE, True)
    DE_type = _get_DE_type(lookup, term_id) if term_id else None

    total_feed = get_feed(cycle.get('inputs', []))
    ionophore = _is_ionophore(cycle, total_feed) if total_feed > 0 else False

    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.CROP)
    # only keep inputs that have a positive value
    inputs = list(filter(lambda i: list_sum(i.get('value', [])) > 0, inputs))
    DE = _get_crop_property_average(inputs, DE_type) if DE_type and isinstance(DE_type, str) else 0
    NDF = _get_crop_property_average(inputs, 'ndfContent')

    enteric_factor = safe_parse_float(_get_liveAnimal_lookup_value(lookup, term_id, 'Ym', DE, NDF, ionophore)) / 100
    enteric_sd = safe_parse_float(_get_liveAnimal_lookup_value(lookup, term_id, 'SD', DE, NDF, ionophore))

    debugRequirements(model=MODEL, term=TERM_ID,
                      digestibility=DE,
                      ndf=NDF,
                      ionophore=ionophore,
                      total_feed=total_feed,
                      enteric_factor=enteric_factor)

    should_run = all([total_feed != 0, enteric_factor != 0])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, total_feed, enteric_factor, enteric_sd


def run(cycle: dict):
    should_run, feed, enteric_factor, enteric_sd = _should_run(cycle)
    return _run(feed, enteric_factor, enteric_sd) if should_run else []
