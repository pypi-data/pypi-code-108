import arrow
from oarepo_taxonomies.utils import get_taxonomy_json

from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/date/issued/value", phase="pre")
def call_date_issued(el, **kwargs):
    return date_issued(el, **kwargs)  # pragma: no cover


def date_issued(el, **kwargs):
    assert isinstance(el, list), "Element should be list"
    el = el[-1][-1]
    arrow_date = arrow.get(el)
    access_rights = []
    if arrow_date < arrow.get("2006-01-01"):
        access_rights = get_taxonomy_json(code="accessRights", slug="c_16ec").paginated_data
        accessibility = {
            "cs": "Dostupné v digitálním repozitáři UK (pouze z IP adres univerzity).",
            "en": "Available in the Charles University Digital Repository (accessible only from "
                  "computers with university IP address)."
        }
    if access_rights:
        return {
            "dateIssued": el,
            "accessRights": access_rights,
            "accessibility": accessibility
        }
    else:
        return {"dateIssued": el}
