from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/description/abstract", phase="pre")
def call_abstract(el, **kwargs):
    return abstract(el, **kwargs)  # pragma: no cover


def abstract(el, **kwargs):
    res = {}
    if isinstance(el, (tuple, list)):
        for _ in el:
            add_abstract(res, _)
    if isinstance(el, dict):
        add_abstract(res, el)
    return {"abstract": res}


def add_abstract(res, el):
    for k, v in el.items():
        res[k[:2]] = v[0]["value"][0]
