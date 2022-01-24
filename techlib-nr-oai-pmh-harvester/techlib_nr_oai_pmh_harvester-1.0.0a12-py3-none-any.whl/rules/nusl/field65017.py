from oarepo_oai_pmh_harvester.decorators import rule

from nr_oai_pmh_harvester.rules.nusl.field650_7 import subject


@rule("nusl", "marcxml", "/65017", phase="pre")
def call_subject_2(el, **kwargs):
    return subject(el, **kwargs)  # pragma: no cover
