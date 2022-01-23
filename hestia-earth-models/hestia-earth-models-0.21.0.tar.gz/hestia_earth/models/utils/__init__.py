from os.path import dirname, abspath
import sys
from functools import reduce
import operator
from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia, find_node_exact
from hestia_earth.utils.model import linked_node

from .constant import Units

CURRENT_DIR = dirname(abspath(__file__)) + '/'
sys.path.append(CURRENT_DIR)


def _term_id(term): return term.get('@id') if isinstance(term, dict) else term


def _include_methodModel(node: dict, term_id: str):
    term = download_hestia(term_id) if term_id else {}
    return {**node, **({} if term.get('@id') is None else {'methodModel': linked_node(term)})}


def _include_source(node: dict, biblio_title: str):
    source = find_node_exact(SchemaType.SOURCE, {'bibliography.title': biblio_title}) if biblio_title else None
    return {**node, **({} if source is None else {'source': linked_node({'@type': SchemaType.SOURCE.value, **source})})}


def _run_in_serie(data: dict, models: list): return reduce(lambda prev, model: model(prev), models, data)


def _load_calculated_node(node, type: SchemaType, data_state='recalculated'):
    # return original value if recalculated is not available
    return download_hestia(node.get('@id'), type, data_state=data_state) or download_hestia(node.get('@id'), type)


def _term_match_unit(node: dict, unit: Units):
    uunit = unit if isinstance(unit, str) else unit.value
    return node.get('term', {}).get('units') == uunit


def _filter_list_term_unit(values: list, unit: Units):
    return list(filter(lambda i: _term_match_unit(i, unit), values))


def is_from_model(node: dict) -> bool:
    """
    Check if the Blank Node came from one of the Hestia Models.

    Parameters
    ----------
    node : dict
        The Blank Node containing `added` and `updated`.

    Returns
    -------
    bool
        `True` if the value came from a model, `False` otherwise.
    """
    return 'value' in node.get('added', []) or 'value' in node.get('updated', [])


def sum_values(values: list):
    """
    Sum up the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return sum(filtered_values) if len(filtered_values) > 0 else None


def multiply_values(values: list):
    """
    Multiply the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return reduce(operator.mul, filtered_values, 1) if len(filtered_values) > 1 else None
