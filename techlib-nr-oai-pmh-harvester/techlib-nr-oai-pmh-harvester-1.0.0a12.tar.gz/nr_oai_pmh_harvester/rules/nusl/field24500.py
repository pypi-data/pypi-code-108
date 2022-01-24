from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer

from nr_oai_pmh_harvester.utils import get_alpha2_lang


@rule("nusl", "marcxml", "/24500", phase="pre")
def call_title(el, **kwargs):
    return title(el, **kwargs)  # pragma: no cover


def title(el, **kwargs):
    return get_title(el, kwargs)


def get_title(el, kwargs, field="title"):
    res = []
    record = kwargs["record"]
    if isinstance(el, (list, tuple)):
        for _ in el:
            res.append(get_title_dict(_, record))
    if isinstance(el, dict):
        res.append(get_title_dict(el, record))
    if res:
        return {
            field: res
        }
    else:
        return OAITransformer.PROCESSED  # pragma: no cover


def get_title_dict(el, record, first_lang_field="a", second_lang_field="b"):
    res = {}
    primary_lang_title = el.get(first_lang_field)
    if primary_lang_title:
        lang_object = record.get("04107")
        if isinstance(lang_object, dict):
            lang = lang_object.get("a", "cze")
        elif isinstance(lang_object, (list, tuple)):
            for _ in lang_object:
                lang = _.get("a")
                if lang:
                    break
        else:
            lang = "cze"
        res[get_alpha2_lang(lang)] = primary_lang_title

    secondary_lang = el.get(second_lang_field)
    if secondary_lang:
        res["en"] = secondary_lang

    return res
