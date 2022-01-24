from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.rules.utils.degree_grantor import get_institution_term


@rule("nusl", "marcxml", "/7102_", phase="pre")
def call_degree_grantor_2(el, **kwargs):
    return degree_grantor_2(el, **kwargs)


def degree_grantor_2(el, **kwargs):
    term = None
    if isinstance(el, (list, tuple)):
        for _ in el:
            term = get_grantor_term(_)
            if term:
                break
    if isinstance(el, dict):
        term = get_grantor_term(el)
    if term:
        return {
            "degreeGrantor": get_taxonomy_json(code="institutions",
                                               slug=term.slug).paginated_data
        }


def get_grantor_term(el):
    grantor_array = [el.get("a"), el.get("g"), el.get("b")]
    grantor_array = [_ for _ in grantor_array if _ is not None]
    reversed_grantor_array = list(reversed(grantor_array))
    for reversed_level, unit in enumerate(reversed_grantor_array):
        term = get_institution_term(unit, reversed_grantor_array, reversed_level)
        if term:
            return term
