from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.rules.utils.degree_grantor import get_institution_term
from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer


@rule("nusl", "marcxml", "/502__/c", phase="pre")
def call_degree_grantor(el, **kwargs):
    return degree_grantor(el, **kwargs)  # pragma: no cover


# TODO: https://www.postgresql.org/docs/9.6/functions-json.html, sepsat do Notion nebo článek

def degree_grantor(el, **kwargs):
    if "," in el:
        grantor_array = [x.strip() for x in el.split(",", maxsplit=2) if x.strip()]
    elif "." in el:
        grantor_array = [x.strip() for x in el.split(".", maxsplit=2) if x.strip()]
    else:
        grantor_array = [el]
    reversed_grantor_array = list(reversed(grantor_array))
    for reversed_level, unit in enumerate(reversed_grantor_array):
        term = get_institution_term(unit, reversed_grantor_array, reversed_level)
        if term:
            return {
                "degreeGrantor": get_taxonomy_json(code="institutions",
                                                   slug=term.slug).paginated_data
            }
        else:
            return OAITransformer.PROCESSED
