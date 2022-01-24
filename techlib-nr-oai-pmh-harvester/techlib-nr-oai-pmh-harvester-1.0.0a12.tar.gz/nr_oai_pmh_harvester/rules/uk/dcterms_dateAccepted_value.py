from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dcterms/dateAccepted/value", phase="pre")
def call_date_defended(el, **kwargs):
    return date_defended(el, **kwargs)  # pragma: no cover


def date_defended(el, **kwargs):
    assert isinstance(el, list)
    assert len(el) <= 1
    return {"dateDefended": el[0][0]}
