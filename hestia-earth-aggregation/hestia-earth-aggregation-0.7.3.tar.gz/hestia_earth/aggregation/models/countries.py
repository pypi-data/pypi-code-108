from functools import reduce
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data_closest_date
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float, flatten

from hestia_earth.aggregation.log import debugWeights
from hestia_earth.aggregation.utils import _end_date_year, _min, _max, _sd
from hestia_earth.aggregation.utils.term import _blank_node_completeness, _format_organic, _format_irrigated


def _organic_weight(country_id: str, year: int):
    lookup = download_lookup('region-standardsLabels-isOrganic.csv', True)
    data = get_table_value(lookup, 'termid', country_id, 'organic')
    # default to 0 => assume nothing organic
    value = safe_parse_float(extract_grouped_data_closest_date(data, year), 0)
    return value / 100


def _irrigated_weight(country_id: str, year: int):
    lookup = download_lookup('region-irrigated.csv', True)
    irrigated_data = get_table_value(lookup, 'termid', country_id, column_name('irrigatedValue'))
    # default to 0 => assume nothing irrigated
    irrigated = safe_parse_float(extract_grouped_data_closest_date(irrigated_data, year), 0)
    area_data = get_table_value(lookup, 'termid', country_id, column_name('totalCroplandArea'))
    # default to 1 => assume whole area
    area = safe_parse_float(extract_grouped_data_closest_date(area_data, year), 1)
    return irrigated / area


def _add_weights(country_id: str, year: int):
    def apply(prev: dict, node: dict):
        organic_weight = _organic_weight(country_id, year)
        irrigated_weight = _irrigated_weight(country_id, year)
        weight = (
            organic_weight if node.get('organic', False) else 1-organic_weight
        ) * (
            irrigated_weight if node.get('irrigated', False) else 1-irrigated_weight
        )
        return {**prev, node.get('id'): {'weight': weight, 'dataCompleteness': node.get('dataCompleteness', {})}}
    return apply


def _weighted_value(weights: dict):
    def apply(node: dict):
        value = node.get('value')
        weight = weights.get(node.get('id'), {}).get('weight')
        return None if (value is None or weight is None) else (list_sum(value, value), weight)
    return apply


def _missing_weights(nodes: list):
    completeness_key = _blank_node_completeness(nodes[0])
    keys = ['-'.join([
        _format_organic(node.get('organic')), _format_irrigated(node.get('irrigated'))
    ]) for node in nodes]

    def apply(item: tuple):
        key, weight = item
        is_complete = weight.get('dataCompleteness', {}).get(completeness_key, False)
        is_missing = all([k not in key for k in keys])
        return (0, weight.get('weight')) if is_complete and is_missing else None
    return apply


def _aggregate_weighted(term: dict, nodes: list, weights: dict):
    # account for complete missing values
    missing_weights = non_empty_list(map(_missing_weights(nodes), weights.items()))

    values = non_empty_list(map(_weighted_value(weights), nodes)) + missing_weights

    total_weight = sum(weight for _v, weight in values)
    weighted_value = [value * weight for value, weight in values]
    value = sum(weighted_value) / (total_weight if total_weight != 0 else 1)
    observations = len(nodes) + len(missing_weights)
    return {
        'node': nodes[0],
        'term': term,
        'value': value if len(values) > 0 else None,
        'max': _max(weighted_value),
        'min': _min(weighted_value),
        'sd': _sd(weighted_value),
        'observations': observations
    }


def _aggregate_nodes(aggregate_key: str, weights: dict):
    def aggregate(data: dict):
        def aggregate(term_id: str):
            blank_nodes = data.get(aggregate_key).get(term_id)
            term = blank_nodes[0].get('term')
            return _aggregate_weighted(term, blank_nodes, weights)

        aggregates = flatten(map(aggregate, data.get(aggregate_key, {}).keys()))
        return (aggregates, data) if len(aggregates) > 0 else ([], {})

    def aggregate_multiple(data: dict):
        return reduce(
            lambda prev, curr: {**prev, curr: _aggregate_nodes(curr, weights)(data)}, aggregate_key, {}
        )

    return aggregate if isinstance(aggregate_key, str) else aggregate_multiple


def aggregate(aggregate_key: str, groups: dict) -> list:
    nodes = next((data.get('nodes') for data in groups.values() if len(data.get('nodes', [])) > 0), [])
    first_node = nodes[0]
    country_id = first_node.get('country').get('@id')
    year = _end_date_year(first_node)
    weights = reduce(_add_weights(country_id, year), nodes, {})
    debugWeights(weights)
    return non_empty_list(map(_aggregate_nodes(aggregate_key, weights), groups.values()))
