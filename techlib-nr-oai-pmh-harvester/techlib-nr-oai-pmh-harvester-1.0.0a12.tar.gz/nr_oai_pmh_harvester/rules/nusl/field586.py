from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/586__", phase="pre")
def call_defended(el, **kwargs):
    return defended(el, **kwargs)


def defended(el, **kwargs):
    value = el.get("a")
    if value == "obhájeno":
        return {"defended": True}
    elif value == "neobhájeno":
        return {"defended": False}
    else:
        return {"defended": "Nutná kontrola"}
