from __future__ import division, absolute_import, print_function, \
    unicode_literals

from mosaik_eid.eid.entity_type_registry import EntityTypeRegistry
from mosaik_eid.eid.entity_exception import EntityIndexException, \
    EntityException, EntityTypeException


class EidParser(object):
    """
    Parse, generate and check entity identifiers.

    Entity identifiers are structured like this:
        <entity type>-<consecutive number>
    Where the consecutive number is a non-negative number to avoid confusion
    about the minus.
    """

    @classmethod
    def parse_entity_index(cls, e_index):
        """
        Parse entity index integer from an entity index string or integer.
        """
        try:
            e_index = int(e_index)
        except ValueError:
            raise EntityIndexException('The entity index must be an integer.')

        if e_index < 0:
            raise EntityIndexException('The entity index must be positive.')

        return e_index

    @classmethod
    def parse_entity_type(cls, e_type):
        """
        Parse an entity type object from an entity type string or object.
        """
        try:
            e_type = EntityTypeRegistry.types[e_type.name]
        except AttributeError:
            try:
                e_type = EntityTypeRegistry.types[e_type]
            except KeyError:
                raise EntityTypeException(
                    'No such entity type was registered:', e_type)

        return e_type

    @classmethod
    def parse(cls, eid):
        """
        Parse a given entity identifier into entity type and entity index.
        """
        try:
            e_type, e_index = eid.split('-')
        except ValueError:
            raise EntityException('Entity identifiers may only contain 1 "-".')

        e_type = EidParser.parse_entity_type(e_type)
        e_index = EidParser.parse_entity_index(e_index)

        return e_type, e_index
