from statistics import stdev
from functools import reduce
from hestia_earth.utils.tools import safe_parse_date

from ..version import VERSION
from .term import _group_by_term_id, _group_completeness, _is_complete

MIN_NB_OBSERVATIONS = 20


def _save_json(data: dict, filename: str):
    import os
    should_run = os.getenv('DEBUG', 'false') == 'true'
    if not should_run:
        return
    import json
    dir = os.getenv('TMP_DIR', '/tmp')
    with open(f"{dir}/{filename}.jsonld", 'w') as f:
        return json.dump(data, f, indent=2)


def _aggregated_node(node: dict):
    return {**node, 'aggregated': True, 'aggregatedVersion': VERSION}


def _aggregated_version(node: dict, *keys):
    node['aggregated'] = node.get('aggregated', [])
    node['aggregatedVersion'] = node.get('aggregatedVersion', [])
    all_keys = ['value'] if len(keys) == 0 else keys
    for key in all_keys:
        if node.get(key) is None:
            continue
        if key in node['aggregated']:
            node.get('aggregatedVersion')[node['aggregated'].index(key)] = VERSION
        else:
            node['aggregated'].append(key)
            node['aggregatedVersion'].append(VERSION)
    return node


def _min(values): return min(values) if len(values) >= MIN_NB_OBSERVATIONS else None


def _max(values): return max(values) if len(values) >= MIN_NB_OBSERVATIONS else None


def _sd(values): return stdev(values) if len(values) >= 2 else None


def sum_values(values: list):
    """
    Sum up the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return sum(filtered_values) if len(filtered_values) > 0 else None


def _set_dict_single(data: dict, key: str, value, strict=False):
    if value is not None and (not strict or value != 0):
        data[key] = value
    return data


def _set_dict_array(data: dict, key: str, value, strict=False):
    if value is not None and (not strict or value != 0):
        data[key] = [value]
    return data


def _end_date_year(node: dict):
    date = safe_parse_date(node.get('endDate'))
    return date.year if date else None


def _same_product(product: dict): return lambda node: node.get('product', {}).get('@id') == product.get('@id')


def _group_by_product(product: dict, nodes: list, props: list, include_matrix=True) -> dict:
    def group_by(group: dict, node: dict):
        node_id = node.get('@id', node.get('id'))
        end_date = _end_date_year(node)
        organic = node.get('organic', False)
        irrigated = node.get('irrigated', False)
        key = '-'.join([str(organic), str(irrigated)]) if include_matrix else ''
        data = {
            'organic': organic,
            'irrigated': irrigated,
            'country': node.get('country'),
            'year': end_date
        }
        if key not in group:
            group[key] = {
                'product': product,
                'nodes': [],
                'sites': [],
                'dataCompleteness': {},
                **data,
                **reduce(lambda prev, curr: {**prev, curr: {}}, props, {})
            }
        group[key]['nodes'].append({**node, **data})
        group[key]['sites'].append(node.get('site'))

        def group_by_prop(prop: str):
            # save ref to organic/irrigated for later grouping
            values = list(map(
                lambda v: {
                    **v,
                    **data,
                    'id': node_id,
                    'dataCompleteness': _is_complete(node, product, v)
                }, node.get(prop, [])))
            return reduce(_group_by_term_id, values, group[key][prop])

        group[key] = reduce(lambda prev, curr: {**prev, curr: group_by_prop(curr)}, props, group[key])
        group[key]['dataCompleteness'] = _group_completeness(group[key]['dataCompleteness'], node)
        return group

    return reduce(group_by, list(filter(_same_product(product), nodes)), {})
