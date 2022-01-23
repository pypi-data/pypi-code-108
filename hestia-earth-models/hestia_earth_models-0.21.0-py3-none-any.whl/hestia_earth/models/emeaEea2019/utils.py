from hestia_earth.utils.tools import list_sum

from hestia_earth.models.utils.term import get_liquid_fuel_terms
from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete


def _get_input_values(cycle: dict, term_ids: list, prefix: str):
    ids = list(filter(lambda i: prefix in i.lower(), term_ids))
    values = [list_sum(i.get('value', [])) for i in cycle.get('inputs', [])
              if i.get('term', {}).get('@id') in ids and len(i.get('value', [])) > 0]
    return [0] if len(values) == 0 and _is_term_type_complete(cycle, {'termType': 'electricityFuel'}) else values


def _get_fuel_values(cycle: dict):
    liquid_fuels = get_liquid_fuel_terms()
    diesel_values = _get_input_values(cycle, liquid_fuels, 'diesel')
    gasoline_values = _get_input_values(cycle, liquid_fuels, 'gasoline')
    return diesel_values, gasoline_values
