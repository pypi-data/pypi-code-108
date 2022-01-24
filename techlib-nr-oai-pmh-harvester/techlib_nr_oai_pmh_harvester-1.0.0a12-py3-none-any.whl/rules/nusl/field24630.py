from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer

from nr_oai_pmh_harvester.rules.nusl.field24500 import get_title_dict


@rule("nusl", "marcxml", "/24630", phase="pre")
def call_title_alternate_2(el, **kwargs):
    return title_alternate_2(el, **kwargs)  # pragma: no cover


def title_alternate_2(el, **kwargs):
    res = []
    record = kwargs["record"]
    if isinstance(el, (list, tuple)):
        for _ in el:  # pragma: no cover
            get_volume_issue(el, record, res)
    if isinstance(el, dict):
        get_volume_issue(el, record, res)
    if res:
        return {"titleAlternate": res}
    return OAITransformer.PROCESSED  # pragma: no cover


def get_volume_issue(el, record, res):
    res.append(get_title_dict(el, record, first_lang_field="n"))
    res.append(get_title_dict(el, record, first_lang_field="p"))
