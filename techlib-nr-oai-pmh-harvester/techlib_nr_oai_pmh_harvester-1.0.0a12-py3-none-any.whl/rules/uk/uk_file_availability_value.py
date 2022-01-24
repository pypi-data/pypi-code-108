from oarepo_taxonomies.utils import get_taxonomy_json

from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer


@rule("uk", "xoai", "/uk/file-availability/value", phase="pre")
def call_accessibility(el, **kwargs):
    return accessibility(el, **kwargs)  # pragma no cover


def accessibility(el, **kwargs):
    el = el[0][0]
    date = kwargs["results"][0]["dateIssued"]
    if date <= "2005":
        return OAITransformer.PROCESSED
    if el == 'V':
        access_rights = get_taxonomy_json(code="accessRights", slug="c_abf2").paginated_data
        accessibility = {
            "cs": "Volně dostupné v digitálním repozitáři UK.",
            "en": "Freely available in the Charles University Digital Repository."
        }
    elif el == 'N':
        access_rights = get_taxonomy_json(code="accessRights", slug="c_16ec").paginated_data
        accessibility = {
            "cs": "Práce je dočasně nebo trvale vyloučena ze zveřejnění. Pro vyžádání kopie "
                  "dokumentu je potřeba vyplnit formulář v digitálním repozitáři UK.",
            "en": "The work is temporarily or permanently excluded from publication. To request a "
                  "copy of the document, it is necessary to fill in the form in the Charles "
                  "University Digital Repository."
        }
    elif el == 'P':
        access_rights = get_taxonomy_json(code="accessRights", slug="c_abf2").paginated_data
        accessibility = {
            "cs": "Práce je dočasně nebo trvale vyloučena ze zveřejnění. Pro vyžádání kopie "
                  "dokumentu je potřeba vyplnit formulář v digitálním repozitáři UK.",
            "en": "Freely available without attachments of the thesis in the Charles University "
                  "Digital Repository."
        }
    else:
        access_rights = get_taxonomy_json(code="accessRights", slug="c_16ec").paginated_data
        accessibility = {
            "cs": "Volně dostupné vyjma příloh práce v digitálním repozitáři UK.",
            "en": "The work is temporarily or permanently excluded from publication. To request a "
                  "copy of the document, it is necessary to fill in the form in the Charles "
                  "University Digital Repository."
        }
    return {
        "accessRights": access_rights,
        "accessibility": accessibility
    }
