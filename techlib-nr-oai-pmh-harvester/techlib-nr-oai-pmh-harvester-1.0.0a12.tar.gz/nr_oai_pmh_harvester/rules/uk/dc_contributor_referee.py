from nr_oai_pmh_harvester.rules.utils.contributor import get_contributor
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/contributor/referee/value", phase="pre")
def call_referee(el, **kwargs):
    return referee(el, **kwargs)  # pragma: no cover


def referee(el, **kwargs):
    return get_contributor(el, "referee")
