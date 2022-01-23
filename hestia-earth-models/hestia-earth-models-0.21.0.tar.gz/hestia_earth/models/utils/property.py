from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import safe_parse_float

from . import _term_id, _include_methodModel


def _new_property(term, model=None):
    node = {'@type': SchemaType.PROPERTY.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(node, model)


def find_term_property(term, property: str, default=None) -> dict:
    """
    Get the property by `@id` linked to the `Term` in the glossary.

    Parameters
    ----------
    term
        The `Term` either as a `str` (`@id` field) or as a `dict` (containing `@id` as a key).
    property : str
        The `term.@id` of the property. Example: `nitrogenContent`.
    default : Any
        The default value if the property is not found. Defaults to `None`.

    Returns
    -------
    dict
        The property if found, `default` otherwise.
    """
    props = term.get('defaultProperties', []) if isinstance(term, dict) else []
    term_id = _term_id(term)
    props = download_hestia(term_id).get('defaultProperties', []) if len(props) == 0 and term_id else props
    return find_term_match(props, property, default)


def get_node_property(node: dict, property: str):
    """
    Get the property by `@id` linked to the Blank Node in the glossary.

    It will search for the `Property` in the following order:
    1. Search in the `properties` of the Blank Node if any was provided
    2. Search in the `defaultProperties` of the `term` by default.

    Parameters
    ----------
    node : dict
        The Blank Node, e.g. an `Input`, `Product`, `Measurement`, etc.
    property : str
        The `term.@id` of the property. Example: `nitrogenContent`.

    Returns
    -------
    dict
        The property if found, `None` otherwise.
    """
    prop = find_term_match(node.get('properties', []), property, None)
    return find_term_property(node.get('term', {}), property, {}) if prop is None else prop


def _get_nitrogen_content(node: dict):
    return safe_parse_float(
        get_node_property(node, 'nitrogenContent').get('value', 0)) if node else 0


def _get_nitrogen_tan_content(node: dict):
    return safe_parse_float(
        get_node_property(node, 'totalAmmoniacalNitrogenContentAsN').get('value', 0)) if node else 0
