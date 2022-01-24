from oarepo_taxonomies.utils import get_taxonomy_json

from nr_oai_pmh_harvester.query import get_query_by_slug


def get_contributor_role(role: str):
    query = get_query_by_slug(taxonomy_code="contributor-type", slug=role)
    term = query.one_or_none()
    if term:
        taxonomy_json = get_taxonomy_json(code="contributor-type", slug=term.slug).paginated_data
    else:
        taxonomy_json = []
    return taxonomy_json


def get_contributor(el, role):
    el = el[0]
    res = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            dict_ = {
                "name": _,
                "role": get_contributor_role(role)
            }
            res.append(dict_)
    if isinstance(el, str):
        res.append({
            "name": el,
            "role": get_contributor_role(role)
        })
    return {"contributor": res}