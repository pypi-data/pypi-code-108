from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/publisher/cs_CZ/value", phase="pre")
def call_publisher(el, **kwargs):
    return publisher(el, **kwargs)  # pragma: no cover


def publisher(el, **kwargs):
    res = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            res.append(_)
    if isinstance(el, str):
        res.append(el)
    return {"publisher": res}
