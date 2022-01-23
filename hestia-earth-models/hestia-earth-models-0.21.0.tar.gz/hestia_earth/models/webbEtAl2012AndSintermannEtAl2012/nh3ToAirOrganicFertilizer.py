from enum import Enum
from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import match_lookup_value
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete
from hestia_earth.models.utils.cycle import valid_site_type
from hestia_earth.models.utils.property import _get_nitrogen_tan_content
from . import MODEL

TERM_ID = 'nh3ToAirOrganicFertilizer'
CLASS_LOOKUP_COLUMN = 'OrganicFertilizerClassification'


class Classification(Enum):
    LIQUID_SLURRY_SEWAGESLUDGE = 'Liquid, Slurry, Sewage Sludge'
    SOLID = 'Solid'
    COMPOST = 'Compost'
    GREEN_MANURE = 'Green Manure'


NH3_TAN_FACTOR = {
    Classification.LIQUID_SLURRY_SEWAGESLUDGE: 0.307877242878561,
    Classification.SOLID: 0.685083144186046,
    Classification.COMPOST: 0.710000000000000,
    Classification.GREEN_MANURE: 0
}


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _grouped_value(group: dict):
    classification = group.get('classification')
    return list_sum(group.get('values')) * NH3_TAN_FACTOR[classification]


def _run(organic_fertilizer_values: list):
    value = sum(list(map(_grouped_value, organic_fertilizer_values)))
    return [_emission(value)]


def _get_N_grouped_values(cycle: dict, classification: Classification):
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.ORGANICFERTILIZER)
    values = [
        list_sum(get_total_value([i])) * _get_nitrogen_tan_content(i) / 100 for i in inputs
        if match_lookup_value(i, col_name=CLASS_LOOKUP_COLUMN, col_value=classification.value)
    ]
    values = [0] if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'fertilizer'}) else values
    return {'classification': classification, 'values': values}


def _grouped_values_log(group: dict):
    return ';'.join([group.get('classification').value, str(list_sum(group.get('values')))])


def _should_run(cycle: dict):
    lqd_slurry_sluge_values = _get_N_grouped_values(cycle, Classification.LIQUID_SLURRY_SEWAGESLUDGE)
    solid_values = _get_N_grouped_values(cycle, Classification.SOLID)
    compost_values = _get_N_grouped_values(cycle, Classification.COMPOST)
    green_manure_values = _get_N_grouped_values(cycle, Classification.GREEN_MANURE)
    organic_fertilizer_values = [lqd_slurry_sluge_values, solid_values, compost_values, green_manure_values]

    debugRequirements(model=MODEL, term=TERM_ID,
                      lqd_slurry_sluge_values=_grouped_values_log(lqd_slurry_sluge_values),
                      solid_values=_grouped_values_log(solid_values),
                      compost_values=_grouped_values_log(compost_values),
                      green_manure_values=_grouped_values_log(green_manure_values))

    should_run = valid_site_type(cycle) and all([len(v.get('values')) > 0 for v in organic_fertilizer_values])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)

    return should_run, organic_fertilizer_values


def run(cycle: dict):
    should_run, organic_fertilizer_values = _should_run(cycle)
    return _run(organic_fertilizer_values) if should_run else []
