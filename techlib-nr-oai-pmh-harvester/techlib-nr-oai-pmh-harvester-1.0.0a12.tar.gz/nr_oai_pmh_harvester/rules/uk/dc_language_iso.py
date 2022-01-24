from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.query import find_in_json
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/language/iso/value", phase="pre")
def call_language(el, **kwargs):
    return language(el, **kwargs)  # pragma: no cover


def language(el, **kwargs):
    res = []
    assert len(el) <= 1
    el = el[-1]
    if isinstance(el, (list, tuple)):
        for _ in el:
            res.extend(get_language_taxonomy_json(_))
    if isinstance(el, str):
        res.extend(get_language_taxonomy_json(el))
    return {"language": res}


def get_language_taxonomy_json(value):
    term = find_in_json("languages", "alpha2", value[:2]).one_or_none()
    if term:
        return get_taxonomy_json("languages", term.slug).paginated_data
    else:
        return []
