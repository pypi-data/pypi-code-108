from hestia_earth.utils.tools import non_empty_list

from hestia_earth.aggregation.utils import _group_by_product
from hestia_earth.aggregation.models.terms import aggregate as aggregate_by_term
from hestia_earth.aggregation.models.countries import aggregate as aggregate_by_country
from hestia_earth.aggregation.models.world import aggregate as aggregate_world
from .utils import (
    AGGREGATION_KEYS,
    _format_for_grouping, _format_terms_results, _format_country_results, _format_world_results,
    _update_impact_assessment
)


def aggregate_country(country: dict, product: dict, impacts: list, source: dict, start_year: int, end_year: int):
    # step 1: aggregate all impacts indexed on the platform
    impacts = _format_for_grouping(impacts)
    impacts = _group_by_product(product, impacts, AGGREGATION_KEYS, True)
    aggregates = aggregate_by_term(AGGREGATION_KEYS, impacts)
    impacts = non_empty_list(map(_format_terms_results, aggregates))
    impacts = list(map(_update_impact_assessment(country, start_year, end_year, source), impacts))
    if len(impacts) == 0:
        return []

    # step 2: use aggregated impacts to calculate country-level impacts
    aggregates = aggregate_by_country(AGGREGATION_KEYS, _group_by_product(product, impacts, AGGREGATION_KEYS, False))
    weight_impacts = non_empty_list(map(_format_country_results, aggregates))
    weight_impacts = list(map(_update_impact_assessment(country, start_year, end_year, source, False), weight_impacts))

    return impacts + weight_impacts


def aggregate_global(country: dict, product: dict, impacts: list, source: dict, start_year: int, end_year: int):
    impacts = _group_by_product(product, impacts, AGGREGATION_KEYS, False)
    aggregates = aggregate_world(AGGREGATION_KEYS, impacts)
    impacts = non_empty_list(map(_format_world_results, aggregates))
    impacts = list(map(_update_impact_assessment(country, start_year, end_year, source, False), impacts))
    return impacts
