from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.utils.dataCompleteness import _is_term_type_complete


def _get_aboveGroundCropResidueBurnt_value(cycle: dict):
    value = find_term_match(cycle.get('products', []), 'aboveGroundCropResidueBurnt', {}).get('value', [])
    data_complete = _is_term_type_complete(cycle, {'termType': TermTermType.CROPRESIDUE.value})
    return [0] if len(value) == 0 and data_complete else value
