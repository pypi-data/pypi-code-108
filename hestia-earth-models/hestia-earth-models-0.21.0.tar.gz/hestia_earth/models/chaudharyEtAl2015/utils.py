from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugRequirements, debugMissingLookup
from hestia_earth.models.utils.impact_assessment import get_site, get_region_id
from hestia_earth.models.utils.crop import get_crop_grouping_fao
from . import MODEL


def get_region_factor(impact_assessment: dict, factor: str):
    product = impact_assessment.get('product')
    region_id = get_region_id(impact_assessment)
    ecoregion = get_site(impact_assessment).get('ecoregion')
    lookup_name = 'ecoregion-factors' if ecoregion else 'region-ecoregion-factors' if region_id else None
    col = 'ecoregion' if ecoregion else 'termid' if region_id else None
    try:
        grouping = get_crop_grouping_fao(product)
        column = column_name(f"{grouping}_TAXA_AGGREGATED_Median_{factor}")
        debugRequirements(model=MODEL, factor=factor,
                          product=product.get('@id'),
                          crop_grouping=grouping,
                          lookup=lookup_name,
                          column=column,
                          value=ecoregion or region_id)
        value = get_table_value(download_lookup(f"{lookup_name}.csv"), col, ecoregion or region_id, column)
        debugMissingLookup(f"{lookup_name}.csv", col, ecoregion or region_id, column, value)
        return safe_parse_float(value) if grouping and lookup_name else 0
    except Exception:
        return 0
