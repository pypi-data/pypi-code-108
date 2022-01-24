from nr_oai_pmh_harvester.rules.uk.dc_publisher_cs_CZ_value import publisher
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/dc/publisher/cs_CS/value", phase="pre")
def call_publisher_2(el, **kwargs):
    return publisher(el, **kwargs)  # pragma: no cover
