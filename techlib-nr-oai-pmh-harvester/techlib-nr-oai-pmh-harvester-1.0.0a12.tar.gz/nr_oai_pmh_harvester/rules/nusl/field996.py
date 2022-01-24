from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer
from oarepo_taxonomies.utils import get_taxonomy_json


@rule("nusl", "marcxml", "/996__", phase="pre")
def call_accessibility(el, **kwargs):
    return accessibility(el, **kwargs) # pragma: no cover


def accessibility(el, **kwargs):
    res = {}
    cs = el.get("a")
    en = el.get("b")
    pole9 = el.get("9")
    if cs:
        res["cs"] = cs
    if en:
        res["en"] = en
    if res:
        return {
            "accessibility": res,
            "accessRights": get_access_rights(cs)
        }
    elif pole9:
        slug = get_access_rights_dict().get(pole9, "c_abf2")
        return {
            "accessRights": get_access_rights(slug=slug)
        }
    return OAITransformer.PROCESSED  # pragma: no cover


def get_access_rights_dict():
    return {
        "0": "c_14cb",
        "1": "c_abf2",
        "2": "c_16ec"
    }


def get_access_rights(text=None, slug=None):
    access_right_dict = get_access_rights_dict()

    if not slug:
        sentence_dict = {
            "Dokument je dostupný v repozitáři Akademie věd.": "1",
            "Dokumenty jsou dostupné v systému NK ČR.": "1",
            "Plný text je dostupný v Digitální knihovně VUT.": "1",
            "Dostupné v digitálním repozitáři VŠE.": "1",
            "Plný text je dostupný v digitálním repozitáři JČU.": "1",
            "Dostupné v digitálním repozitáři UK.": "1",
            "Dostupné v digitálním repozitáři Mendelovy univerzity.": "1",
            "Dostupné v repozitáři ČZU.": "1",
            "Dostupné registrovaným uživatelům v digitálním repozitáři AMU.": "2",
            "Dokument je dostupný v NLK. Dokument je dostupný též v digitální formě v Digitální "
            "knihovně NLK. Přístup může být vázán na prohlížení z počítačů NLK.": "2",
            "Dostupné v digitálním repozitáři UK (pouze z IP adres univerzity).": "2",
            "Text práce je neveřejný, pro více informací kontaktujte osobu uvedenou v repozitáři "
            "Mendelovy univerzity.": "2",
            "Dokument je dostupný na vyžádání prostřednictvím repozitáře Akademie věd.": "2",
            "Dokument je dostupný v příslušném ústavu Akademie věd ČR.": "0",
            "Dokument je po domluvě dostupný v budově Ministerstva životního prostředí.": "0",
            "Plný text není k dispozici.": "0",
            "Dokument je dostupný v NLK.": "0",
            'Dokument je po domluvě dostupný v budově <a '
            'href=\"http://www.mzp.cz/__C125717D00521D29.nsf/index.html\" '
            'target=\"_blank\">Ministerstva životního prostředí</a>.': "0",
            "Dostupné registrovaným uživatelům v knihovně Mendelovy univerzity v Brně.": "0",
            'Dostupné registrovaným uživatelům v repozitáři ČZU.': "2",
            'Dokument je dostupný na externích webových stránkách.': "0",
        }

        slug = access_right_dict.get(sentence_dict.get(text, "0"))

    return get_taxonomy_json(code="accessRights", slug=slug).paginated_data
