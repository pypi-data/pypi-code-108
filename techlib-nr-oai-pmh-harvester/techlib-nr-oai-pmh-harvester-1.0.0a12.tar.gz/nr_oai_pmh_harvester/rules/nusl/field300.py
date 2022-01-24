from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/300__", phase="pre")
def call_date_extent(el, **kwargs):
    return extent(el, **kwargs)  # pragma: no cover


def extent(el, **kwargs):
    res = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            ext = get_extent(_)
            if ext:
                res.append(ext)
    if isinstance(el, dict):
        ext = get_extent(el)
        if ext:
            res.append(ext)
    return {"extent": res}


def get_extent(el):
    return el.get("a")
