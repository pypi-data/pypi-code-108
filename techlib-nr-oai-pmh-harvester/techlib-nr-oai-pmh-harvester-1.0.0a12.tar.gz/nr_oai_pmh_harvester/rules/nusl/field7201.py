from nr_oai_pmh_harvester.rules.nusl.field720 import people
from oarepo_oai_pmh_harvester.decorators import rule


@rule("nusl", "marcxml", "/7201_", phase="pre")
def call_people_2(el, **kwargs):
    return people(el, **kwargs)  # pragma: no cover
