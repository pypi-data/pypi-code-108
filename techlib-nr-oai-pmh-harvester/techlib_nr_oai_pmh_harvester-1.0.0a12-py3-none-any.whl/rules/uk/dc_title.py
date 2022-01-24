from nr_oai_pmh_harvester.rules.utils import filter_language, remove_country_from_lang_codes
from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer


@rule("uk", "xoai", "/dc/title", phase="pre")
def call_title(el, **kwargs):
    return title(el, **kwargs)  # pragma: no cover


def title(el, **kwargs):
    assert len(el) <= 1
    el = filter_language(el)
    try:
        res = [remove_country_from_lang_codes(el)]
    except:
        return OAITransformer.PROCESSED
    return {"title": res}
