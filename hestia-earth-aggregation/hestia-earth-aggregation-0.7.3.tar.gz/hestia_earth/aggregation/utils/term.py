import re
from hestia_earth.utils.model import linked_node
from unidecode import unidecode
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import find_node, find_node_exact
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

SEARCH_LIMIT = 10000
DEFAULT_COUNTRY_ID = 'region-world'
DEFAULT_COUNTRY_NAME = 'World'
DEFAULT_COUNTRY = {'@id': 'region-world', 'name': DEFAULT_COUNTRY_NAME}
MODEL = 'aggregatedModels'
METHOD_MODEL = {'@type': SchemaType.TERM.value, '@id': MODEL}


def _fetch_all(term_type: TermTermType): return find_node(SchemaType.TERM, {'termType': term_type.value}, SEARCH_LIMIT)


def _fetch_single(term_name: str): return find_node_exact(SchemaType.TERM, {'name': term_name})


def _fetch_default_country(): return _fetch_single(DEFAULT_COUNTRY_NAME)


def _format_country_name(name: str):
    return re.sub(r'[\(\)\,\.\'\"]', '', unidecode(name).lower().replace(' ', '-')) if name else None


def _format_organic(organic: bool): return 'organic' if organic else 'conventional'


def _format_irrigated(irrigated: bool): return 'irrigated' if irrigated else 'non-irrigated'


def _is_global(country_name: str): return country_name is None or country_name == DEFAULT_COUNTRY_NAME


def _should_aggregate(term: dict):
    lookup = download_lookup(f"{term.get('termType')}.csv", True)
    value = get_table_value(lookup, 'termid', term.get('@id'), column_name('skipAggregation'))
    return True if value is None or value == '' else not value


def _group_by_term_id(group: dict, node: dict):
    term = node.get('term', {})
    term_id = term.get('@id')
    if _should_aggregate(term):
        if term_id not in group:
            group[term_id] = []
        group[term_id].append(node)
    return group


def _group_completeness(group: dict, node: dict):
    for key in node.get('dataCompleteness', {}).keys():
        group[key] = group.get(key, 0) + (1 if node.get('dataCompleteness').get(key) else 0)
    return group


def _update_country(country_name: str):
    return linked_node({
        **(_fetch_single(country_name) if isinstance(country_name, str) else country_name),
        '@type': SchemaType.TERM.value
    })


DATA_COMPLETENESS_MAPPING = {
    SchemaType.INPUT.value: {
        TermTermType.ELECTRICITY.value: 'electricityFuel',
        TermTermType.FUEL.value: 'electricityFuel',
        TermTermType.MATERIAL.value: 'material',
        TermTermType.ORGANICFERTILIZER.value: 'fertilizer',
        TermTermType.INORGANICFERTILIZER.value: 'fertilizer',
        TermTermType.SOILAMENDMENT.value: 'soilAmendments',
        TermTermType.PESTICIDEAI.value: 'pesticidesAntibiotics',
        TermTermType.PESTICIDEBRANDNAME.value: 'pesticidesAntibiotics',
        TermTermType.ANTIBIOTIC.value: 'pesticidesAntibiotics',
        TermTermType.WATER.value: 'water',
        TermTermType.OTHER.value: 'other',
        TermTermType.CROP.value: 'animalFeed'
    },
    SchemaType.PRODUCT.value: {
        TermTermType.ANIMALPRODUCT.value: 'products',
        TermTermType.CROP.value: 'products',
        TermTermType.LIVEANIMAL.value: 'products',
        TermTermType.LIVEAQUATICSPECIES.value: 'products',
        TermTermType.PROCESSEDFOOD.value: 'products',
        TermTermType.CROPRESIDUE.value: 'cropResidue'
    }
}


def _blank_node_completeness(blank_node: dict):
    term_type = blank_node.get('term', {}).get('termType')
    return DATA_COMPLETENESS_MAPPING.get(blank_node.get('@type'), {}).get(term_type)


IS_COMPLETE = {
    'animalFeed': lambda product: product.get('termType') in [
        TermTermType.ANIMALPRODUCT.value,
        TermTermType.LIVEANIMAL.value,
        TermTermType.LIVEAQUATICSPECIES.value
    ]
}


def _is_complete(node: dict, product: dict, blank_node: dict):
    completeness_key = _blank_node_completeness(blank_node)
    product_complete = IS_COMPLETE.get(completeness_key, lambda *args: True)(product)
    return node.get('dataCompleteness', {}).get(completeness_key, False) and product_complete
