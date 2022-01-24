from nr_oai_pmh_harvester.rules.uk.uk_publication_place_cs_CZ_value import publication_place
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/uk/publication/place/cs_CS/value", phase="pre")
def call_publication_place_2(el, **kwargs):
    return publication_place(el, **kwargs)  # pragma: no cover
