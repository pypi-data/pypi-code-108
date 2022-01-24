from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.rules.utils.degree_grantor import get_institution_term
from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer


@rule("uk", "xoai", "/uk/grantor/cs_CZ/value", phase="pre")
def call_degree_grantor(el, **kwargs):
    return degree_grantor_3(el, **kwargs)  # pragma: no cover


def degree_grantor_3(el, **kwargs):
    value = el[-1]
    assert isinstance(value, str)
    grantor_array = value.split(",")
    grantor_array = [unit.strip() for unit in grantor_array]
    reversed_grantor_array = list(reversed(grantor_array))
    if "Univerzita Karlova" not in reversed_grantor_array:
        reversed_grantor_array.append("Univerzita Karlova")
    for reversed_level, unit in enumerate(reversed_grantor_array):
        term = get_institution_term(unit, reversed_grantor_array, reversed_level)
        if term:
            return {
                "degreeGrantor": get_taxonomy_json(code="institutions",
                                                   slug=term.slug).paginated_data
            }
        else:
            return OAITransformer.PROCESSED
