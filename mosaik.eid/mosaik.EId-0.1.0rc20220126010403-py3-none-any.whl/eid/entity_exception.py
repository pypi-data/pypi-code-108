from __future__ import division, absolute_import, print_function, \
    unicode_literals


class EntityException(Exception):
    """
    Indicates that something is wrong with the entity identifier in general.
    """
    pass


class EntityTypeException(EntityException):
    """
    Indicates that something is wrong with the type of an entity identifier.
    """
    pass


class EntityIndexException(EntityException):
    """
    Indicates that something is wrong with the index of an entity identifier.
    """
    pass
