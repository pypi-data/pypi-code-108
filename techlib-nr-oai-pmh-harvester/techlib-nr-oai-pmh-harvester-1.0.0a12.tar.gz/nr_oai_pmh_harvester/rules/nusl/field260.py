from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/260__", phase="pre")
def call_date_publisher(el, **kwargs):
    return publisher(el, **kwargs)  # pragma: no cover


def publisher(el, **kwargs):
    res = []
    if isinstance(el, (list, tuple)):
        for _ in el:
            item = get_publisher(_)
            if item:
                res.append(item)
    if isinstance(el, dict):
        item = get_publisher(el)
        if item:
            res.append(item)
    return {"publisher": res}


def get_publisher(el):
    publisher = el.get("b")
    if not publisher:
        publisher = el.get("a")
    return publisher
