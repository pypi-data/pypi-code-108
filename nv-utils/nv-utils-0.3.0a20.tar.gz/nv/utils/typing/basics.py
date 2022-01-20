from collections.abc import MutableSet, Set, MutableSequence, Sequence, Mapping

from .empty import Missing


__ALL__ = ['BASIC_TYPES', 'BASIC_SEQUENCES', 'BASIC_ELEMENTS', 'BASIC_COLLECTIONS', 'MISSING']


# Definitions for parsing behaviour
BASIC_TYPES = (
    int,
    float,
    complex,
    bool,
    type(None),
)

BASIC_SEQUENCES = (
    str,
    bytes,
    bytearray,
)

# Types dealt as elements (although some of the behave like sequences as well)
BASIC_ELEMENTS = (
    *BASIC_TYPES,
    *BASIC_SEQUENCES,
)

# Types whose elements will be parsed individually into one of the basic sructures
BASIC_COLLECTIONS = (
    MutableSet,
    Set,
    MutableSequence,
    Sequence,
    Mapping,
)


# Use missing if to communicate across different modules that a value is missing when None has another meaning
MISSING = Missing()
