from oarepo_taxonomies.utils import get_taxonomy_json

from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/type/cs_CZ/value", phase="pre")
def call_resourceType(el, **kwargs):
    return resourceType(el, **kwargs)  # pragma: no cover


def resourceType(el, **kwargs):
    assert isinstance(el, list)
    assert len(el) <= 1
    el = el[-1]
    rt_dict = {
     "diplomová práce": "master_theses",
     "bakalářská práce": "bachelor_theses",
     "dizertační práce": "doctoral_theses",
     "rigorózní práce": "rigorous_theses",
    }
    slug = rt_dict.get(el)
    if slug:
        slug = "theses_etds." + slug
        return {"resourceType": get_taxonomy_json(code="resourceType", slug=slug).paginated_data}
