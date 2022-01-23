from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.api import find_node, search

from ..log import debugMissingLookup
from .constant import Units

LIMIT = 100


def get_lookup_value(term: dict, column: str, skip_debug: bool = False):
    value = get_table_value(
        download_lookup(f"{term.get('termType')}.csv"), 'termid', term.get('@id'), column_name(column)
    ) if term else None
    debugMissingLookup(
        f"{term.get('termType')}.csv", 'termid', term.get('@id'), column, value) if term and not skip_debug else None
    return value


def get_liquid_fuel_terms():
    """
    Find all "liquid" `fuel` terms from the Glossary:
    - https://hestia.earth/glossary?termType=fuel&query=gasoline
    - https://hestia.earth/glossary?termType=fuel&query=diesel

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType.keyword": TermTermType.FUEL.value
                    }
                }
            ],
            "should": [
                {
                    "regexp": {
                        "name": "gasoline*"
                    }
                },
                {
                    "regexp": {
                        "name": "diesel*"
                    }
                }
            ],
            "minimum_should_match": 1
        }
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_irrigation_terms():
    """
    Find all `water` terms from the Glossary:
    https://hestia.earth/glossary?termType=water

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.WATER.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_urea_terms():
    """
    Find all `inorganicFertilizer` urea terms from the Glossary:
    https://hestia.earth/glossary?termType=inorganicFertilizer&query=urea

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.INORGANICFERTILIZER.value,
        'name': 'urea'
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_excreta_terms(units: Units = Units.KG_N):
    """
    Find all `excreta` terms in `kg N` from the Glossary:
    https://hestia.earth/glossary?termType=excreta

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.EXCRETA.value,
        'units.keyword': units.value
    }, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))


def get_tillage_terms():
    """
    Find all `landUseManagement` terms of "tillage" from the Glossary:
    https://hestia.earth/glossary?termType=tillage&query=tillage

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.TILLAGE.value,
        'name': 'tillage'
    }, limit=LIMIT)
    return [n['@id'] for n in terms if 'depth' not in n['@id'].lower()]


def get_generic_crop():
    terms = find_node(SchemaType.TERM, {
        'termType.keyword': TermTermType.CROP.value,
        'name': 'Generic crop grain'
    }, limit=1)
    return terms[0] if len(terms) > 0 else None


def get_rice_paddy_terms():
    """
    Find all `crop` terms of "rice paddy" from the Glossary:
    https://hestia.earth/glossary?termType=crop&query=rice%20paddy

    Returns
    -------
    list
        List of matching term `@id` as `str`.
    """
    terms = search({
        "bool": {
            "must": [
                {
                    "match": {
                        "@type": SchemaType.TERM.value
                    }
                },
                {
                    "match": {
                        "termType": TermTermType.CROP.value
                    }
                },
                {
                    "regexp": {
                        "name": "rice*"
                    }
                },
                {
                    "regexp": {
                        "name": "paddy*"
                    }
                }
            ]
        }
    }, limit=LIMIT)
    return [n['@id'] for n in terms if 'depth' not in n['@id'].lower()]


def get_crop_residue_terms():
    terms = find_node(SchemaType.TERM, {'termType.keyword': TermTermType.CROPRESIDUE.value}, limit=LIMIT)
    return list(map(lambda n: n['@id'], terms))
