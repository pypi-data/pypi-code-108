from nr_oai_pmh_harvester.rules.utils.study_field import get_study_field
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/uk/degree-program/cs/cs_CZ/value", phase="pre")
def call_study_field(el, **kwargs):
    return study_field(el, **kwargs)  # pragma no cover


def study_field(el, **kwargs):
    assert isinstance(el, list) and len(el) <= 1
    el = el[-1]
    return get_study_field(el, is_program=True)
