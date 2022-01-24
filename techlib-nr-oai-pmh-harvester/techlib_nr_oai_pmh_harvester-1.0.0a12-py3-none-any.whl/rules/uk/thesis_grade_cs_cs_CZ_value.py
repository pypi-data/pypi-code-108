from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/thesis/grade/cs/cs_CZ/value", phase="pre")
def call_defended(el, **kwargs):
    return defended(el, **kwargs)  # pragma no cover


def defended(el, **kwargs):
    assert isinstance(el, list) and len(el) <= 1
    el = el[-1]
    mapping = {
        "Výborně": True,
        "Velmi dobře": True,
        "Prospěl/a": True,
        "Dobře": True,
        "Prospěl": True,
        "Neprospěl": False,
        "Neprospěl/a": False,
        "Výtečně": True,
        "Uspokojivě": True,
        "Dostatečně": True,
        "Nedostatečně": False,
    }
    return {"defended": mapping.get(el)}
