from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/creator/value", phase="pre")
def call_creator(el, **kwargs):
    return creator(el, **kwargs)  # pragma: no cover


def creator(el, **kwargs):
    el = el[0]
    res = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            res.append({"name": _})
    if isinstance(el, str):
        res.append({"name": el})
    return {"creator": res}
