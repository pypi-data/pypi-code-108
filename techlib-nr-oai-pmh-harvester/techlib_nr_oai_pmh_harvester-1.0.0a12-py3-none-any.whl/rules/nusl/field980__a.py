from oarepo_oai_pmh_harvester.transformer import OAITransformer
from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.query import find_in_json_list

from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/980__/a", phase="pre")
def call_resource_type(el, **kwargs):
    return resource_type(el, **kwargs)  # pragma: no cover


def resource_type(el, **kwargs):
    if el == "metodiky":
        record = kwargs["record"]
        if "336__" not in record:
            return {
                "resourceType": get_taxonomy_json(code="resourceType",
                                                  slug="methodologies-and-procedures/methodologies-without-certification").paginated_data
            }
        else:
            return OAITransformer.PROCESSED
    term = find_in_json_list("resourceType", "nuslType", el).one_or_none()
    return {
        "resourceType": get_taxonomy_json(code="resourceType", slug=term.slug).paginated_data
    }
