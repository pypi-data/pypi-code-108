import requests
import json
import math
from concurrent.futures import ThreadPoolExecutor
from hestia_earth.schema import SCHEMA_VERSION, CycleFunctionalUnit, NodeType, TermTermType, PRODUCT_TERM
from hestia_earth.utils.api import download_hestia, find_node
from hestia_earth.utils.tools import non_empty_list
from hestia_earth.utils.request import api_url

from hestia_earth.aggregation.log import logger
from hestia_earth.aggregation.utils import _save_json
from .term import DEFAULT_COUNTRY_NAME, _should_aggregate

SEARCH_LIMIT = 10000
# exclude ecoinvent data
EXCLUDE_BIBLIOS = [
    'The ecoinvent database version 3 (part I): overview and methodology'
]
MATCH_AGGREGATED_QUERY = {'match': {'aggregated': 'true'}}
MATCH_SCHEMA_VERSION = {'regexp': {'schemaVersion': f"[{SCHEMA_VERSION.split('.')[0]}][.].*"}}


def _date_range_query(start: int, end: int):
    return {'range': {'endDate': {'gte': str(start), 'lte': str(end)}}} if start and end else None


SOURCE_FIELD_BY_TYPE = {
    NodeType.CYCLE.value: 'defaultSource',
    NodeType.SITE.value: 'defaultSource'
}


def _product_query(node_type: str, product_name: str):
    return {
        NodeType.CYCLE.value: {
            'nested': {
                'path': 'products',
                'query': {'match': {'products.term.name.keyword': product_name}}
            }
        },
        NodeType.IMPACTASSESSMENT.value: {'match': {'product.name.keyword': product_name}}
    }.get(node_type)


def _functionalUnit_query(node_type: str):
    return {
        NodeType.CYCLE.value: {
            # note: we currently ignore relative unit as we would need to convert values to aggregate
            'match': {'functionalUnit.keyword': CycleFunctionalUnit.RELATIVE.value}
        }
    }.get(node_type)


def _source_query(node_type: str, title: str):
    source_field = SOURCE_FIELD_BY_TYPE.get(node_type, 'source')
    return {'match': {f"{source_field}.bibliography.title.keyword": title}}


def _node_type_query(node_type: str, product_name: str = None):
    return {
        'bool': {
            'must': non_empty_list([
                {'match': {'@type': node_type}},
                _product_query(node_type, product_name) if product_name else None,
                MATCH_SCHEMA_VERSION
            ]),
            'must_not': list(map(lambda title: _source_query(node_type, title), EXCLUDE_BIBLIOS)) + [
                _functionalUnit_query(node_type),
                MATCH_AGGREGATED_QUERY
            ]
        }
    }


COUNTRY_FIELD_BY_TYPE = {
    NodeType.CYCLE.value: 'site.country'
}


def _country_query(node_type: str, country_name: str):
    country_field = COUNTRY_FIELD_BY_TYPE.get(node_type, 'country')
    return {'match': {f"{country_field}.name.keyword": country_name}}


def _run_query(data: dict):
    headers = {'Content-Type': 'application/json'}
    params = json.dumps(data)
    return requests.post(f'{api_url()}/search', params, headers=headers).json().get('results', [])


def _query_all_nodes(node_type: str, product_name: str, start_year: int, end_year: int, country_name: str):
    query = _node_type_query(node_type, product_name)
    date_range = _date_range_query(start_year, end_year)
    query['bool']['must'].extend([date_range] if date_range else [])
    if country_name != DEFAULT_COUNTRY_NAME:
        query['bool']['must'].append(_country_query(node_type, country_name))

    return _run_query({
        'query': query,
        'limit': SEARCH_LIMIT,
        'fields': ['@id', '@type']
    })


def _download_node(data_state=''):
    def download(n):
        try:
            node = download_hestia(n.get('@id'), n.get('@type'), data_state=data_state)
            return node if node.get('@type') else None
        except Exception:
            logger.debug('skip non-%s %s: %s', data_state, n.get('@type'), n.get('@id'))
            return None
    return download


def _download_nodes(nodes: list, data_state=''):
    total = len(nodes)
    with ThreadPoolExecutor() as executor:
        nodes = non_empty_list(executor.map(_download_node(data_state), nodes))
    logger.debug('downloaded %s nodes / %s total nodes', str(len(nodes)), str(total))
    return nodes


def _country_nodes(node_type: str, product_name: str, start_year: int, end_year: int, country_name: str):
    # TODO: paginate search and improve performance
    nodes = _query_all_nodes(node_type, product_name, start_year, end_year, country_name)
    return _download_nodes(nodes, data_state='recalculated')


def _global_nodes(node_type: str, product_name: str, start_year: int, end_year: int):
    nodes = _run_query({
        'query': {
            'bool': {
                'must': non_empty_list([
                    {'match': {'@type': node_type}},
                    _product_query(node_type, product_name),
                    MATCH_AGGREGATED_QUERY,
                    MATCH_SCHEMA_VERSION,
                    _date_range_query(start_year, end_year)
                ]),
                'must_not': [
                    _country_query(node_type, DEFAULT_COUNTRY_NAME),
                    # do not include lower levels of country breakdown
                    {'match': {'name': 'Conventional'}},
                    {'match': {'name': 'Irrigated'}},
                    {'match': {'name': 'Organic'}}
                ]
            }
        },
        'limit': SEARCH_LIMIT,
        'fields': ['@id', '@type']
    })
    return _download_nodes(nodes)


def find_nodes(node_type: str, product_name: str, start_year: int, end_year: int, country_name: str):
    nodes = _country_nodes(
        node_type, product_name, start_year, end_year, country_name
    ) if country_name != DEFAULT_COUNTRY_NAME else _global_nodes(
        node_type, product_name, start_year, end_year
    )
    _save_json({'nodes': nodes}, '-'.join([
        str(v) for v in ['nodes', node_type, product_name, country_name, start_year, end_year] if v
    ]))
    return nodes


def _earliest_date(node_type: str, product_name: str, country_name: str):
    query = _node_type_query(node_type, product_name)
    if country_name and country_name != DEFAULT_COUNTRY_NAME:
        query['bool']['must'].append(_country_query(node_type, country_name))
    params = {
        'query': query,
        'limit': 1,
        'fields': ['endDate'],
        'sort': [{'endDate.keyword': 'asc'}]
    }
    results = _run_query(params)
    return results[0].get('endDate') if len(results) > 0 else None


def _latest_date(node_type: str, product_name: str, country_name: str):
    query = _node_type_query(node_type, product_name)
    if country_name and country_name != DEFAULT_COUNTRY_NAME:
        query['bool']['must'].append(_country_query(node_type, country_name))
    params = {
        'query': query,
        'limit': 1,
        'fields': ['endDate'],
        'sort': [{'endDate.keyword': 'desc'}]
    }
    results = _run_query(params)
    return results[0].get('endDate') if len(results) > 0 else None


def get_countries():
    """
    Get the list of countries (GADM level 0 regions).

    Returns
    -------
    list
        The list of countries as `dict`.
    """
    return find_node(NodeType.TERM, {'termType': TermTermType.REGION.value, 'gadmLevel': 0}, limit=1000)


def get_products():
    """
    Get the list of terms that can be used to aggregate.

    Returns
    -------
    list
        The list of terms as `dict`.
    """
    query = {
        'bool': {
            'must': [{'match': {'@type': NodeType.TERM.value}}],
            'should': [
                {'match': {'termType.keyword': type.value}} for type in PRODUCT_TERM
            ],
            'minimum_should_match': 1
        }
    }
    params = {
        'query': query,
        'limit': 10000,
        'fields': ['@type', '@id', 'name', 'termType'],
        'sort': [{'termType.keyword': 'asc'}]
    }
    terms = _run_query(params)
    return list(filter(_should_aggregate, terms))


def _get_time_ranges(earliest_date: str, latest_date: str, period_length: int = 10):
    """
    Get time ranges starting from the earliest date to today.

    Parameters
    ----------
    earliest_date : str
        The start date of the time range.
    latest_date : str
        The end date of the time range.
    period_length : int
        Optional - length of the period, 10 by default.
        Example: with 10 year period and the earliest impact in 2006 returns [[2001, 2010], [2011, 2020], [2021, 2030]]

    Returns
    -------
    list
        A list of time periods.
        Example: `[(1990, 1999), (2000, 2009)]`
    """
    earliest_year = int(earliest_date[0:4])
    latest_year = int(latest_date[0:4])
    min_year = round(math.floor(earliest_year / 10) * 10)
    max_year = round((math.floor(latest_year / 10) + 1) * 10)
    logger.debug('Time range between %s and %s', min_year, max_year)
    return [(i, i+period_length-1) for i in range(min_year, max_year, period_length)]


def get_time_ranges(node_type: str, country_name: str, product_name: str):
    from_date = _earliest_date(node_type, product_name, country_name)
    return _get_time_ranges(from_date, _latest_date(node_type, product_name, country_name)) if from_date else []
