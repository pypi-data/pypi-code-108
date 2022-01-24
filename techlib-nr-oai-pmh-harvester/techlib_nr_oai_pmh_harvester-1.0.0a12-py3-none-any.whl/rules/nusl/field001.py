from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/001", phase="pre")
def control_number_caller(el, **kwargs):
    return control_number(el, **kwargs) # pragma: no cover


def control_number(el, **kwargs):
    return {"control_number": el}
