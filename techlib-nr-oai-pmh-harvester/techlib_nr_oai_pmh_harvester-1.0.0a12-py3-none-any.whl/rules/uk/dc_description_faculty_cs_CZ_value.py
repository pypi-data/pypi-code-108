from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.rules.utils.degree_grantor import get_institution_term
from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer


@rule("uk", "xoai", "/dc/description/faculty/cs_CZ/value", phase="pre")
def call_degree_grantor(el, **kwargs):
    return degree_grantor_2(el, **kwargs)  # pragma: no cover


def degree_grantor_2(el, **kwargs):
    unit = el[-1]
    term = get_institution_term(unit, reversed_grantor_array=[unit, "Univerzita Karlova"])
    if term:
        return {"degreeGrantor": get_taxonomy_json("institutions", slug=term.slug).paginated_data}
    else:
        return OAITransformer.PROCESSED
