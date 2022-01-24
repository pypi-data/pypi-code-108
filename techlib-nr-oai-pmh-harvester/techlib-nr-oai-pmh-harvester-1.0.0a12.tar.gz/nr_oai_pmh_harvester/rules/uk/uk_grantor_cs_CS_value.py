from nr_oai_pmh_harvester.rules.uk.uk_grantor_cs_CZ_value import degree_grantor_3
from oarepo_oai_pmh_harvester.decorators import rule


@rule("uk", "xoai", "/uk/grantor/cs_CS/value", phase="pre")
def call_degree_grantor(el, **kwargs):
    return degree_grantor_3(el, **kwargs)  # pragma: no cover
