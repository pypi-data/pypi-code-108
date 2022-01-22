from __future__ import division, absolute_import, print_function, \
    unicode_literals

from mosaik_eid.eid.entity_type_registry import EntityTypeRegistry
from mosaik_eid.eid.entity_exception import EntityTypeException


class EidManager(object):
    """
    Manage entity identifiers.

    This class tracks entity types as well as numbers of issued identifiers.

    This class implements the borg pattern in which all instances share state.
    """

    # entity type -->  shared state
    __shared_state_dict = {}

    def __init__(self, e_type):
        try:
            e_type_name = e_type.name
        except AttributeError:
            e_type_name = e_type

        if not EntityTypeRegistry.registered(e_type=e_type_name):
            raise EntityTypeException(
                'No such entity type registered: %s' % e_type_name)

        # Initialize the hive mind on first run, only
        try:
            self.__shared_state_dict[e_type_name]
        except KeyError:
            self.__shared_state_dict[e_type_name] = {}
        self.__dict__ = self.__shared_state_dict[e_type_name]

        try:
            self._entity_identifiers
        except AttributeError:
            # Map entity name to entity identifiers
            self._entity_identifiers = {}

    def has_entity_identifiers(self):
        return self._entity_identifiers != {}

    def __iter__(self):
        return self

    def next(self):
        """
        Wrapper method around __next__ for backwards compatibility to Python 2.
        """
        return self.__next__()

    def __next__(self):
        """
        Get the next entity identifier for the given entity type.
        """
        # Get our own key for our state
        for entity_type, state in self.__shared_state_dict.items():
            if state is self.__dict__:
                break

        try:
            next_index = len(self._entity_identifiers[entity_type])
        except KeyError:
            next_index = 0

        # avoid circular import
        from mosaik_eid.eid.entity_identifier import EntityIdentifier
        eid = EntityIdentifier(entity_type, next_index)

        try:
            self._entity_identifiers[entity_type].append(eid)
        except KeyError:
            self._entity_identifiers[entity_type] = []
            self._entity_identifiers[entity_type].append(eid)

        return eid
