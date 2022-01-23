from hestia_earth.schema import PropertyStatsDefinition, TermTermType
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import non_empty_list, safe_parse_date

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils import _filter_list_term_unit
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.property import _new_property
from . import MODEL
from .utils import product_equivalent_value

TERM_ID = 'liveweightPerHead'


def _property(value: float, product_term_id: str):
    logger.info('model=%s, term=%s, product=%s, value=%s', MODEL, TERM_ID, product_term_id, value)
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    prop['statsDefinition'] = PropertyStatsDefinition.REGIONS.value
    return prop


def _run(products: list, year: int, country: str):
    def run_product(product: dict):
        value = product_equivalent_value(product, year, country)
        prop = _property(value, product.get('term', {}).get('@id')) if value else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else None

    return non_empty_list(map(run_product, products))


def _should_run(cycle: dict):
    products = filter_list_term_type(cycle.get('products', []), TermTermType.ANIMALPRODUCT)
    products = _filter_list_term_unit(products, Units.KG_LIVEWEIGHT)

    end_date = safe_parse_date(cycle.get('endDate'))
    year = end_date.year if end_date else None
    country = cycle.get('site', {}).get('country', {}).get('@id')

    debugRequirements(model=MODEL, term='animalProduct',
                      products=len(products),
                      year=year,
                      country=country)

    should_run = all([len(products) > 0, year, country])
    logger.info('model=%s, term=animalProduct, should_run=%s', MODEL, should_run)
    return should_run, products, year, country


def run(cycle: dict):
    should_run, products, year, country = _should_run(cycle)
    return _run(products, year, country) if should_run else []
