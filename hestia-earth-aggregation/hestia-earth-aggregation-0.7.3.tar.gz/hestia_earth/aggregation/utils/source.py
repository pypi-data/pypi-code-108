from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import find_node_exact
from hestia_earth.utils.model import linked_node

from hestia_earth.aggregation.log import logger

HESTIA_BIBLIO_TITLE = 'Hestia: A new data platform for storing and analysing data on the productivity \
and sustainability of agriculture'


def get_source():
    source = find_node_exact(SchemaType.SOURCE, {'bibliography.title': HESTIA_BIBLIO_TITLE})
    logger.debug('source=%s', source)
    return linked_node(source) if source else None
