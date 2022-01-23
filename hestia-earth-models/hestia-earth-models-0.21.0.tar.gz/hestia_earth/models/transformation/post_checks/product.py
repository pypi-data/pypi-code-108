from hestia_earth.schema import TermTermType
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logger
from hestia_earth.models.utils.constant import Units, convert_to_N
from hestia_earth.models.utils.input import get_total_nitrogen, get_total_value


EMISSIONS_VALUE = {
    Units.KG_N.value: lambda inputs, emissions: list_sum(
        get_total_nitrogen(inputs)
    ) - list_sum([convert_to_N(e) for e in emissions])
}


def _product_value(product: dict, inputs: list, emissions: list):
    units = product.get('term', {}).get('units')
    return EMISSIONS_VALUE[units](inputs, emissions) if units in EMISSIONS_VALUE else list_sum(get_total_value(inputs))


def _run_product(product: dict, inputs: list, emissions: list):
    inputs = [i for i in inputs if i.get('term', {}).get('@id') == product.get('term', {}).get('@id')]
    should_replace = len(product.get('value', [])) == 0
    return {
        **product,
        **({'value': [_product_value(product, inputs, emissions)]} if should_replace else {})
    }


def _run(transformation: dict):
    emissions = transformation.get('emissions', [])
    inputs = transformation.get('inputs', [])
    return [_run_product(p, inputs, emissions) for p in transformation.get('products', [])]


def _should_run(transformation: dict):
    term_id = transformation.get('term', {}).get('@id')
    should_run = transformation.get('term', {}).get('termType') == TermTermType.EXCRETAMANAGEMENT.value
    logger.info('model=transformation/post_checks, term=%s, should_run=%s', term_id, should_run)
    return should_run


def run(transformation: dict):
    products = _run(transformation) if _should_run(transformation) else []
    return {**transformation, **({'products': products} if len(products) > 0 else {})}
