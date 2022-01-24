from nr_oai_pmh_harvester.rules.utils.study_field import get_study_field
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/uk/degree-discipline/cs/cs_CZ/value", phase="pre")
def call_study_field_2(el, **kwargs):
    return study_field_2(el, **kwargs)  # pragma no cover


def study_field_2(el, **kwargs):
    assert isinstance(el, list) and len(el) <= 1
    el = el[-1]
    programme = \
    kwargs.get('record', {}).get('uk', [{}])[0].get('degree-program', [{}])[0].get('cs', [{}])[
        0].get('cs_CZ', [{}])[0].get('value', [{}])[0]
    return get_study_field(el, programme=programme)
