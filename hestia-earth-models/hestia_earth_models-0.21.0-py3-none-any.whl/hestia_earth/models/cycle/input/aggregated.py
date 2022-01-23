import math
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import search
from hestia_earth.utils.model import find_primary_product, find_term_match, linked_node
from hestia_earth.utils.tools import safe_parse_date

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.cycle import is_organic, valid_site_type
from hestia_earth.models.utils.term import get_generic_crop

MODEL = 'aggregated'
MODEL_KEY = 'impactAssessment'
SEED_TERM_ID = 'seed'
MATCH_WORLD_QUERY = {'match': {'country.name.keyword': {'query': 'World', 'boost': 1}}}


def _end_date(end_date: str):
    year = safe_parse_date(end_date).year
    return round(math.floor(year / 10) * 10) + 9


def _match_country(country: dict):
    country_name = country.get('name') if country else None
    return {
        'bool': {
            # either get with exact country, or default to global
            'should': [
                {'match': {'country.name.keyword': {'query': country_name, 'boost': 1000}}},
                MATCH_WORLD_QUERY
            ],
            'minimum_should_match': 1
        }
    } if country_name else MATCH_WORLD_QUERY


def _find_closest_impact(cycle: dict, end_date: str, input: dict, country: dict, must_queries=[]):
    query = {
        'bool': {
            'must': [
                {'match': {'@type': SchemaType.IMPACTASSESSMENT.value}},
                {'match': {'aggregated': 'true'}},
                {'match': {'product.name.keyword': input.get('term', {}).get('name')}},
                _match_country(country)
            ] + must_queries,
            'should': [
                # if the Cycle is organic, we can try to match organic aggregate first
                {'match': {'name': {'query': 'Organic' if is_organic(cycle) else 'Conventional', 'boost': 1000}}},
                {'match': {'endDate': {'query': end_date, 'boost': 1000}}}
            ]
        }
    }
    results = search(query, fields=['@type', '@id', 'name', 'endDate'])
    # sort by distance to date and score and take min
    results = sorted(
        results,
        key=lambda v: abs(int(end_date) - int(v.get('endDate', '0'))) * v.get('_score', 0),
    )
    result = results[0] if len(results) > 0 else {}
    logger.debug('model=%s, term=%s, impact=%s', MODEL, input.get('term', {}).get('@id'), result.get('@id'))
    return result


def _run_seed(cycle: dict, primary_product: dict, seed_input: dict, end_date: str):
    country = seed_input.get('country')
    # to avoid double counting seed => aggregated impact => seed, we need to get the impact of the previous decade
    # if the data does not exist, use the aggregated impact of generic crop instead
    date = _end_date(end_date)
    impact = _find_closest_impact(cycle, date, primary_product, country, [
        {'match': {'endDate': date - 10}}
    ]) or _find_closest_impact(cycle, date, {'term': get_generic_crop()}, country)
    return [{**seed_input, MODEL_KEY: linked_node(impact)}] if impact else []


def _should_run_seed(cycle: dict):
    primary_product = find_primary_product(cycle) or {}
    product_id = primary_product.get('term', {}).get('@id')
    term_type = primary_product.get('term', {}).get('termType')
    input = find_term_match(cycle.get('inputs', []), SEED_TERM_ID, None)
    has_input = input is not None

    debugRequirements(model=MODEL, term=SEED_TERM_ID,
                      primary_product_id=product_id,
                      primary_product_term_type=term_type,
                      has_input=has_input)

    should_run = all([valid_site_type(cycle, True), term_type == TermTermType.CROP.value, primary_product, has_input])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, SEED_TERM_ID, should_run)
    return should_run, primary_product, input


def _run(cycle: dict, inputs: list, end_date: str):
    date = _end_date(end_date)
    inputs = [
        {**i, MODEL_KEY: linked_node(_find_closest_impact(cycle, date, i, i.get('country')))} for i in inputs
    ]
    return list(filter(lambda i: i.get(MODEL_KEY).get('@id') is not None, inputs))


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    # do not override inputs that already have an impactAssessment
    inputs = [i for i in cycle.get('inputs', []) if not i.get(MODEL_KEY)]

    debugRequirements(model=MODEL, term=MODEL_KEY,
                      end_date=end_date,
                      nb_inputs=len(inputs))

    should_run = all([end_date, len(inputs) > 0])
    logger.info('model=%s, should_run=%s', MODEL, should_run)
    return should_run, inputs, end_date


def run(cycle: dict):
    should_run, inputs, end_date = _should_run(cycle)
    should_run_seed, primary_product, seed_input = _should_run_seed(cycle)
    return (
        _run(cycle, inputs, end_date) if should_run else []
    ) + (
        _run_seed(cycle, primary_product, seed_input, end_date) if should_run_seed else []
    )
