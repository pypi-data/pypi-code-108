from oarepo_oai_pmh_harvester.decorators import rule
from oarepo_oai_pmh_harvester.transformer import OAITransformer


@rule("nusl", "marcxml", "/653__", phase="pre")
def call_keyword(el, **kwargs):
    return keyword(el, **kwargs)


def keyword(el, **kwargs):
    record = kwargs["record"]
    en_keywords = record.get("6530_")
    res = []
    if en_keywords:
        if isinstance(el, (tuple, list)) and isinstance(en_keywords, (tuple, list)):
            for cz, en in zip(el, en_keywords):
                res.append({"cs": cz["a"], "en": en["a"]})
        elif isinstance(el, dict) and isinstance(en_keywords, dict):
            res.append({"cs": el["a"], "en": en_keywords["a"]})
        else:
            return {"keywords": {'error': "Keywords must be fixed in draft mode"}}
    else:
        if isinstance(el, (tuple, list)):
            for cz in el:
                res.append({"cs": cz["a"]})
        if isinstance(el, dict):
            res.append({"cs": el["a"]})
    if res:
        return {"keywords": res}
    else:
        return OAITransformer.PROCESSED
