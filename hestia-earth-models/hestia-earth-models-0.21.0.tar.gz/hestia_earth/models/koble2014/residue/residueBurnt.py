from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugRequirements, debugMissingLookup
from hestia_earth.models.utils.term import get_lookup_value
from .. import MODEL

TERM_ID = 'residueBurnt'


def _get_default_percent(term: dict, country_id: str):
    crop_grouping = get_lookup_value(term, 'cropGroupingResidue')
    lookup = download_lookup('region-crop-cropGroupingResidue-burnt.csv')
    percent = safe_parse_float(
        get_table_value(lookup, 'termid', country_id, column_name(crop_grouping)), None
    ) if crop_grouping else None
    debugMissingLookup('region-crop-cropGroupingResidue-burnt.csv', 'termid', country_id, crop_grouping, percent)
    comb_factor = safe_parse_float(get_lookup_value(term, 'combustion_factor_crop_residue'))
    debugRequirements(model=MODEL, term=TERM_ID,
                      crop_grouping=crop_grouping,
                      country_id=country_id,
                      percent=percent,
                      comb_factor=comb_factor)
    return percent if comb_factor is None or percent is None else percent * comb_factor


def run(cycle: dict, primary_product: dict):
    term = primary_product.get('term', {})
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    value = _get_default_percent(term, country_id)
    return None if value is None else value * 100
