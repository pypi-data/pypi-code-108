from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugRequirements, debugMissingLookup
from hestia_earth.models.utils.term import get_lookup_value
from .. import MODEL

TERM_ID = 'residueRemoved'


def _get_default_percent(term: dict, country_id: str):
    crop_grouping = get_lookup_value(term, 'cropGroupingResidue')
    percent = get_table_value(
        download_lookup('region-crop-cropGroupingResidue-removed.csv'), 'termid', country_id, column_name(crop_grouping)
    ) if crop_grouping else None
    debugMissingLookup('region-crop-cropGroupingResidue-removed.csv', 'termid', country_id, crop_grouping, percent)
    debugRequirements(model=MODEL, term=TERM_ID,
                      crop_grouping=crop_grouping,
                      country_id=country_id,
                      percent=percent)
    return safe_parse_float(percent, None)


def run(cycle: dict, primary_product: dict):
    term = primary_product.get('term', {})
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    value = _get_default_percent(term, country_id)
    return None if value is None else value * 100
