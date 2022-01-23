from functools import reduce
from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data_closest_date
from hestia_earth.utils.tools import list_sum, non_empty_list, safe_parse_float, flatten

from hestia_earth.aggregation.log import debugWeights
from hestia_earth.aggregation.utils import _min, _max, _sd
from hestia_earth.aggregation.utils.term import DEFAULT_COUNTRY_ID, _blank_node_completeness, _format_country_name

LOOKUP_GROUPING = {
    TermTermType.CROP.value: download_lookup(f"{TermTermType.CROP.value}.csv", True),
    TermTermType.ANIMALPRODUCT.value: download_lookup(f"{TermTermType.ANIMALPRODUCT.value}.csv", True)
}
LOOKUP_GROUPING_COLUMN = {
    TermTermType.CROP.value: 'cropGroupingFaostatProduction',
    TermTermType.ANIMALPRODUCT.value: 'animalProductGroupingFAO'
}


def _lookup(product: dict):
    term_type = product.get('termType')
    try:
        lookup = LOOKUP_GROUPING[term_type]
        grouping_column = LOOKUP_GROUPING_COLUMN[term_type]
        grouping = get_table_value(lookup, 'termid', product.get('@id'), column_name(grouping_column))
        return download_lookup(f"region-{term_type}-{grouping_column}-productionQuantity.csv", True), grouping
    except Exception:
        return None, None


def _get_weight(lookup, lookup_column: str, country_id: str, year: int):
    country_value = get_table_value(lookup, 'termid', country_id, column_name(lookup_column))
    country_value = extract_grouped_data_closest_date(country_value, year)
    world_value = get_table_value(lookup, 'termid', DEFAULT_COUNTRY_ID, column_name(lookup_column))
    world_value = extract_grouped_data_closest_date(world_value, year)
    return safe_parse_float(country_value, 1) / safe_parse_float(world_value, 1)


def _add_weights(product: dict):
    lookup, lookup_column = _lookup(product)

    def apply(prev: dict, node: dict):
        id = node.get('@id', node.get('id'))
        country_id = node.get('country').get('@id')
        weight = _get_weight(lookup, lookup_column, country_id, node.get('year')) if lookup is not None else 1
        return {**prev, id: {'weight': weight, 'dataCompleteness': node.get('dataCompleteness', {})}}
    return apply


def _weighted_value(weights: dict):
    def apply(node: dict):
        value = node.get('value')
        country = node.get('country').get('name')
        weight = weights.get(node.get('@id', node.get('id')), {}).get('weight')
        return None if (value is None or weight is None) else (list_sum(value, value), weight, country)
    return apply


def _missing_weights(nodes: list):
    completeness_key = _blank_node_completeness(nodes[0])
    keys = [_format_country_name(node.get('country').get('name')) for node in nodes]

    def apply(item: tuple):
        key, weight = item
        is_complete = weight.get('dataCompleteness', {}).get(completeness_key, False)
        is_missing = all([k not in key for k in keys])
        return (0, weight.get('weight'), key.split('-')[1]) if is_complete and is_missing else None
    return apply


def _aggregate_weighted(term: dict, nodes: list, weights: dict):
    first_node = nodes[0]

    # account for complete missing values
    missing_weights = non_empty_list(map(_missing_weights(nodes), weights.items()))

    values = non_empty_list(map(_weighted_value(weights), nodes)) + missing_weights

    total_weight = sum(weight for _v, weight, _k in values)
    weighted_value = [value * weight for value, weight, _k in values]
    value = sum(weighted_value) / (total_weight if total_weight != 0 else 1)
    observations = len(nodes) + len(missing_weights)
    return {
        'node': first_node,
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
    product = next((data.get('product') for data in groups.values() if data.get('product') is not None), {})
    weights = reduce(_add_weights(product), nodes, {})
    debugWeights(weights)
    return non_empty_list(map(_aggregate_nodes(aggregate_key, weights), groups.values()))
