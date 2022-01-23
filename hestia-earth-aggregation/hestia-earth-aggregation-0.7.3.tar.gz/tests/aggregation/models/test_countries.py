from unittest.mock import patch
import json

from tests.utils import PRODUCT, SOURCE, fixtures_path, start_year, end_year, fake_download, fake_aggregated_version
from hestia_earth.aggregation.utils import _group_by_product
from hestia_earth.aggregation.models.countries import aggregate

class_path = 'hestia_earth.aggregation.models.countries'


@patch('hestia_earth.aggregation.cycle.emission._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.input._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.practice.download_hestia', side_effect=fake_download)
@patch('hestia_earth.aggregation.cycle.product._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.utils._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.cycle.utils._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.measurement._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.site._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.site._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.utils.queries.download_hestia', side_effect=fake_download)
def test_aggregate_cycle(*args):
    from hestia_earth.aggregation.cycle.utils import (
        AGGREGATION_KEYS, _format_for_grouping, _update_cycle, _format_country_results
    )

    with open(f"{fixtures_path}/cycle/terms/aggregated.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    with open(f"{fixtures_path}/cycle/countries/aggregated.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    cycles = _format_for_grouping(cycles)
    results = aggregate(AGGREGATION_KEYS, _group_by_product(PRODUCT, cycles, AGGREGATION_KEYS, False))
    results = list(map(_format_country_results, results))
    results = list(map(_update_cycle(None, start_year, end_year, SOURCE, False), results))
    assert results == expected


@patch('hestia_earth.aggregation.impact_assessment.indicator._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.impact_assessment.utils._aggregated_version', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.impact_assessment.utils._aggregated_node', side_effect=fake_aggregated_version)
@patch('hestia_earth.aggregation.impact_assessment.utils.node_exists', return_value=True)
@patch('hestia_earth.aggregation.utils.queries.download_hestia', side_effect=fake_download)
def test_aggregate_impact(*args):
    from hestia_earth.aggregation.impact_assessment.utils import (
        AGGREGATION_KEYS, _format_for_grouping, _update_impact_assessment, _format_country_results
    )

    with open(f"{fixtures_path}/impact-assessment/terms/aggregated.jsonld", encoding='utf-8') as f:
        impacts = json.load(f)
    with open(f"{fixtures_path}/impact-assessment/countries/aggregated.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    impacts = _format_for_grouping(impacts)
    results = aggregate(AGGREGATION_KEYS, _group_by_product(PRODUCT, impacts, AGGREGATION_KEYS, False))
    results = list(map(_format_country_results, results))
    results = list(map(_update_impact_assessment(None, start_year, end_year, SOURCE, False), results))
    assert results == expected
