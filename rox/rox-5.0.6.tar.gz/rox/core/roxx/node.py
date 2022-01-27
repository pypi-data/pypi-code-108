from collections import namedtuple

Node = namedtuple('Node', ['type', 'value'])


class NodeTypes:
    RAND = 'Rand'
    RATOR = 'Rator'
    UNKNOWN = 'Unknown'

