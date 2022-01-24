from oarepo_taxonomies.utils import get_taxonomy_json

from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/uk/publication-place/cs_CZ/value", phase="pre")
def call_publication_place(el, **kwargs):
    return publication_place(el, **kwargs)  # pragma: no cover


def publication_place(el, **kwargs):
    value = el[-1]
    assert isinstance(value, str)
    return {
        "publicationPlace": {
            "place": value,
            "country": get_taxonomy_json(code="countries", slug="cz").paginated_data
        }
    }
