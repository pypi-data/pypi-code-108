from __future__ import division, absolute_import, print_function, \
    unicode_literals

from enum import Enum, unique


@unique
class EntityType(Enum):
    Agent = 1
    Controller = 2
    Model = 3
    Monitor = 4
