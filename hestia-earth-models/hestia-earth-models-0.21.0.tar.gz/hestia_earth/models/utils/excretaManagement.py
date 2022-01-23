from hestia_earth.schema import TermTermType
from hestia_earth.utils.model import filter_list_term_type

from .term import get_lookup_value


def get_lookup_factor(practices: list, lookup_col: str):
    practices = filter_list_term_type(practices, TermTermType.EXCRETAMANAGEMENT)
    practice = practices[0].get('term', {}) if len(practices) > 0 else None
    return get_lookup_value(practice, lookup_col) if practice else None
