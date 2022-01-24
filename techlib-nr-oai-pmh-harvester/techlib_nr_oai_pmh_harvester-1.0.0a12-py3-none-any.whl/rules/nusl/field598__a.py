from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/598__/a", phase="pre")
def call_note(el, **kwargs):
    return note(el, **kwargs) # pragma: no cover


def note(el, **kwargs):
    return {"note": [el]}
