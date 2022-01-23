from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.lookup import download_lookup, extract_grouped_data, get_table_value, column_name
from hestia_earth.utils.tools import list_sum, safe_parse_float

from ..log import debugMissingLookup
from .property import get_node_property
from .term import get_lookup_value

FAO_LOOKUP_COLUMN = 'cropGroupingFAO'
FAOSTAT_AREA_LOOKUP_COLUMN = 'cropGroupingFaostatArea'
FAOSTAT_PRODUCTION_LOOKUP_COLUMN = 'cropGroupingFaostatProduction'


def get_crop_lookup_value(term_id: str, column: str):
    return get_lookup_value({'@id': term_id, 'termType': TermTermType.CROP.value}, column)


def get_crop_grouping_fao(term: dict): return get_lookup_value(term, FAO_LOOKUP_COLUMN)


def get_crop_grouping_faostat_area(term: dict): return get_lookup_value(term, FAOSTAT_AREA_LOOKUP_COLUMN)


def get_crop_grouping_faostat_production(term: dict): return get_lookup_value(term, FAOSTAT_PRODUCTION_LOOKUP_COLUMN)


def get_N2ON_fertilizer_coeff_from_primary_product(cycle: dict):
    product = find_primary_product(cycle)
    term_id = product.get('term', {}).get('@id') if product else None
    percent = get_crop_lookup_value(term_id, 'N2ON_FERT') if term_id else None
    return safe_parse_float(percent, 0.01)


def _crop_property(term: dict, prop_name: str):
    # as the lookup table might not exist, we are making sure we return `0` in thise case
    try:
        lookup = download_lookup('crop-property.csv')
        term_id = term.get('@id')
        value = extract_grouped_data(get_table_value(lookup, 'termid', term_id, column_name(prop_name)), 'Avg')
        debugMissingLookup('crop-property.csv', 'termid', term_id, prop_name, value)
        return safe_parse_float(value)
    except Exception:
        return 0


def get_crop_property_value_converted(node: dict, prop_name: str):
    prop = get_node_property(node, prop_name)
    prop_value = prop.get('value', 0) if prop else _crop_property(node.get('term', {}), prop_name)
    return list_sum(node.get('value', [])) * prop_value
