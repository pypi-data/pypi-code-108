from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_taxonomies.utils import get_taxonomy_json


@rule("nusl", "marcxml", "/336__/a", phase="pre")
def call_certified_methodologies(el, **kwargs):
    return certified_methodologies(el, **kwargs) # pragma: no cover


def certified_methodologies(el, **kwargs):
    if el.lower().strip() == "certifikovaná metodika":
        res = get_taxonomy_json(code="resourceType",
                                slug="methodologies-and-procedures/certified-methodologies"
                                     "").paginated_data
        N_type = get_taxonomy_json(code="Ntype", slug="a").paginated_data
        return {
            "resourceType": res,
            "N_type": N_type
        }
