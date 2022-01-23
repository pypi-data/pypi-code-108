from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import list_sum
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.utils.crop import get_crop_property_value_converted

TERM_ID = 'feedConversionRatioNitrogen'


def run(cycle: dict):
    inputs = filter_list_term_type(cycle.get('inputs', []), TermTermType.CROP)
    return list_sum([get_crop_property_value_converted(input, 'crudeProteinContent') / 625 for input in inputs])
