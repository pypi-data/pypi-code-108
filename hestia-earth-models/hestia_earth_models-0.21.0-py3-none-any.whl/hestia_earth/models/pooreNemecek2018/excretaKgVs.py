from hestia_earth.schema import ProductStatsDefinition, SiteSiteType
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.constant import Units
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.input import get_feed_carbon
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.term import get_excreta_terms
from . import MODEL
from .excretaKgN import _get_excreta_n_term

Conv_AQ_CLW_CO2CR = 1
Conv_AQ_CLW_CExcr = 0.5
Conv_AQ_OC_OCSed_Marine = 0.55
Conv_AQ_OC_OCSed_Fresh = 0.35


def _product(value: float, excreta: str):
    logger.info('model=%s, term=%s, value=%s', MODEL, excreta, value)
    product = _new_product(excreta, MODEL)
    product['value'] = [value]
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _run(mass_balance_items: list, inputs_c: float, term_id: str, alternate_items: list):
    carbonContent, tsy, slaughterAge, aqocsed, npp = mass_balance_items
    excretaKgN, vsc = alternate_items
    value = max(
        inputs_c + (npp * slaughterAge) / (tsy * 1000) - carbonContent - carbonContent * Conv_AQ_CLW_CO2CR,
        carbonContent * Conv_AQ_CLW_CExcr
    ) * aqocsed if all(mass_balance_items) else excretaKgN * vsc / 100
    return [_product(value, term_id)]


def _get_carbonContent(cycle: dict):
    primary_prod = find_primary_product(cycle) or {}
    return safe_parse_float(get_lookup_value(primary_prod.get('term', {}), 'carbonContent')) / 100


def _get_excreta_vs_term(product: dict): return get_lookup_value(product.get('term', {}), 'excretaVs')


def _no_excreta_term(products: list):
    term_ids = get_excreta_terms(Units.KG_VS)
    return all([not find_term_match(products, term) for term in term_ids])


def _get_conv_aq_ocsed(siteType: str):
    return Conv_AQ_OC_OCSed_Marine if siteType == SiteSiteType.SEA_OR_OCEAN.value else Conv_AQ_OC_OCSed_Fresh


def _should_run(cycle: dict):
    primary_prod = find_primary_product(cycle) or {}

    dc = cycle.get('dataCompleteness', {})
    is_complete = dc.get('animalFeed', False) and dc.get('products', False)
    carbonContent = _get_carbonContent(cycle)

    products = cycle.get('products', [])
    no_excreta = _no_excreta_term(products)

    inputs = cycle.get('inputs', [])
    inputs_c = get_feed_carbon(inputs)

    practices = cycle.get('practices', [])
    tsy = list_sum(find_term_match(practices, 'yieldOfPrimaryAquacultureProductLiveweightPerM2').get('value', []))
    slaughterAge = list_sum(find_term_match(practices, 'slaughterAge').get('value', []))

    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    aqocsed = _get_conv_aq_ocsed(site.get('siteType', {}))
    measurements = site.get('measurements', [])
    npp = most_relevant_measurement_value(measurements, 'netPrimaryProduction', end_date, 0)

    excreta_vs = _get_excreta_vs_term(primary_prod)

    # we can still run the model with excreta in "kg N" units
    excreta = _get_excreta_n_term(primary_prod)
    excreta_product = find_term_match(products, excreta)
    excretaKgN = list_sum(excreta_product.get('value', [0]))
    vsc = get_node_property(excreta_product, 'volatileSolidsContent').get('value', 0)

    debugRequirements(model=MODEL, term=excreta_vs,
                      is_complete=is_complete,
                      aqocsed=aqocsed,
                      inputs_c=inputs_c,
                      carbonContent=carbonContent,
                      yield_of_target_species=tsy,
                      slaughterAge=slaughterAge,
                      netPrimaryProduction=npp,
                      no_excreta=no_excreta,
                      excretaKgN=excretaKgN,
                      volatileSolidsContent=vsc)

    mass_balance_items = [carbonContent, tsy, slaughterAge, aqocsed, npp]
    alternate_items = [excretaKgN, vsc]

    should_run = excreta_vs is not None and no_excreta and (
        (is_complete and all(mass_balance_items)) or
        all(alternate_items)
    )

    logger.info('model=%s, term=%s, should_run=%s', MODEL, excreta_vs, should_run)
    return should_run, mass_balance_items, inputs_c, excreta_vs, alternate_items


def run(cycle: dict):
    should_run, mass_balance_items, inputs_c, excreta_vs, alternate_items = _should_run(cycle)
    return _run(mass_balance_items, inputs_c, excreta_vs, alternate_items) if should_run else []
