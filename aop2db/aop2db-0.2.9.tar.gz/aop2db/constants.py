"""String definitions."""

from .aop.utils import LATEST_XML_VERSION

DATABASE = "DATABASE"

ID = "@id"
AOP_ID = "aop_id"
AOP_HASH = "aop_hash"
APPLICABILITY = "applicability"
TAXONOMY = "taxonomy"
EVIDENCE = "evidence"
SEX = "sex"
LIFESTAGE = "life-stage"
LAST_MODIFIED = "last_modified"
LM_TIMESTAMP = "last-modification-timestamp"
CREATION = "creation"
CREATION_TIMESTAMP = "creation-timestamp"
REFERENCES = "references"

# API
TAX_ID_LOOKUP = "https://rest.ensembl.org/taxonomy/id/{}?content-type=application/json"

# AOP Downloads
AOP_XML_DOWNLOAD = f"https://aopwiki.org/downloads/aop-wiki-xml-{LATEST_XML_VERSION}.gz"

AOP_JSON = "https://aopwiki.org/aops.json"
KE_JSON = "https://aopwiki.org/events.json"
# KER_JSON = "https://aopwiki.org/relationships.json"  # No useful way to map information
STRESSOR_JSON = "https://aopwiki.org/stressors.json"

AOP_JSONS = (AOP_JSON, KE_JSON, STRESSOR_JSON)
