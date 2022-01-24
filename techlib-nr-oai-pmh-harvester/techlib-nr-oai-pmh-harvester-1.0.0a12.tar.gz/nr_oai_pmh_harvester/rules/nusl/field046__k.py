from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/046__/k", phase="pre")
def call_date_issued(el, **kwargs):
    return date_issued(el, **kwargs) # pragma: no cover


def date_issued(el, **kwargs):
    return {"dateIssued": el}
