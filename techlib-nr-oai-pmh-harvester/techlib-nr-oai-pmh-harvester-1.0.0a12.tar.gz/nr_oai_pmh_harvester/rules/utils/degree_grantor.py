from typing import Iterable

from flask_taxonomies.proxies import current_flask_taxonomies
from sqlalchemy.orm.exc import MultipleResultsFound

from nr_oai_pmh_harvester.query import find_in_json_list


def get_institution_term(unit, reversed_grantor_array: Iterable = None, reversed_level: int = None):
    if isinstance(unit, (list, tuple)) and len(unit) == 1:
        unit = unit[0]
    elif isinstance(unit, str):
        pass
    else:
        TypeError(f'Unit has bad type: "{type(unit)}"')
    if not reversed_grantor_array:
        reversed_grantor_array = [unit]
    if reversed_level is None:
        reversed_level = 0
    sqlalchemy_query = current_flask_taxonomies.list_taxonomy('institutions')
    sqlalchemy_query_title_cs = current_flask_taxonomies.apply_term_query(sqlalchemy_query,
                                                                          f'title.cs:"{unit}"',
                                                                          "institutions")
    try:
        term = sqlalchemy_query_title_cs.one_or_none()
    except MultipleResultsFound:
        terms = sqlalchemy_query_title_cs.all()
        term = choose_term(terms, reversed_grantor_array, reversed_level)
        if not term:
            return
    if not term:
        sqlalchemy_query_title_en = current_flask_taxonomies.apply_term_query(sqlalchemy_query,
                                                                              f'title.en:"'
                                                                              f'{unit}"',
                                                                              "institutions")
        term = sqlalchemy_query_title_en.one_or_none()
    if not term:
        sqlalchemy_query_alias = find_in_json_list("institutions", "aliases", unit)
        term = sqlalchemy_query_alias.one_or_none()
    if not term:
        sqlalchemy_query_formerName = find_in_json_list("institutions", "formerNames", unit)
        term = sqlalchemy_query_formerName.one_or_none()
    return term


def get_parent_terms(term, res: list = None):
    if not res:
        res = [term]
    if term.parent:
        parent_term = term.parent
        res.append(parent_term)
        if parent_term.parent:
            get_parent_terms(parent_term, res=res)
    return res


def choose_term(terms, reversed_grantor_array, reversed_level):
    searched_term_slug_tree = []
    if len(reversed_grantor_array) > 1:
        reversed_grantor_array = reversed_grantor_array[1:]
        for i, name in enumerate(reversed_grantor_array):
            if i != 0:
                reversed_grantor_array = reversed_grantor_array[1:]
            term = get_institution_term(name, reversed_grantor_array)
            if term:
                searched_term_slug_tree.append(term.slug)

    for term in terms:
        parent_terms = get_parent_terms(term)
        for _ in parent_terms:
            if _.slug in searched_term_slug_tree:
                return term
    raise Exception("Rigt term could not have been choosen due to ambiguity")