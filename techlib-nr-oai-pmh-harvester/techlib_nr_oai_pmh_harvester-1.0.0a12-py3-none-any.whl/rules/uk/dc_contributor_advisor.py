from nr_oai_pmh_harvester.rules.utils.contributor import get_contributor
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/contributor/advisor/value", phase="pre")
def call_advisor(el, **kwargs):
    return advisor(el, **kwargs)  # pragma: no cover


def advisor(el, **kwargs):
    return get_contributor(el, "advisor")


