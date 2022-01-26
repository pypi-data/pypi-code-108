from __future__ import division, absolute_import, print_function, \
    unicode_literals

from enum import Enum

from mosaik_eid.eid.entity_exception import EntityTypeException
from mosaik_eid.eid.entity_type import EntityType


class EntityTypeRegistry(object):

    types = EntityType

    @classmethod
    def _resolve(cls, e_type):
        """
        Common helper method for register and unregister. Avoids duplicate code.

        Returns registered entity type names and the given entity type's name.
        """
        e_type_names = [entity_type.name for entity_type in cls.types]

        # With the third party library enum34 e_type is an EntityType object.
        # With enum from standard library e_type is a string.
        # For this to work across versions, try and handle the errors.

        try:
            e_type_name = e_type.name
        except AttributeError:
            e_type_name = e_type

        return e_type_names, e_type_name

    @classmethod
    def register(cls, e_type):
        """
        Registers a given entity type with this entity registry.

        Raises a KeyError, if the given entity type is already registered.

        Returns the registered entity type object.
        """
        e_type_names, e_type = cls._resolve(e_type)

        try:
            int(e_type[0])
            raise EntityTypeException(
                "Entity types must not start with a number: " + e_type)
        except ValueError:
            pass

        if cls.registered(e_type):
            raise EntityTypeException(
                'Entity type "%s" already registered.' % e_type)

        # build enumeration object with old e_type_names and the given member
        e_type_names += [e_type]

        cls.types = Enum('EntityType', ' '.join(e_type_names))

        return cls.types[e_type]

    @classmethod
    def unregister(cls, e_type):
        """
        Unregisters the given entity type.

        Raises an EntityTypeException if the given entity type isn't registered.

        Returns the unregistered entity type object.
        """
        e_type_names, e_type = cls._resolve(e_type)

        if not cls.registered(e_type):
            raise EntityTypeException(
                'Entity type "%s" not registered.' % e_type)

        # avoid circular import
        from mosaik_eid.eid.eid_manager import EidManager

        # check if there have been entity identifiers issued for this type
        if EidManager(e_type=e_type).has_entity_identifiers():
            raise EntityTypeException(
                'Cannot unregister entity type with entity identifiers issued.')

        # build enumeration object with old e_type_names excluding the given
        # member
        e_type_names.remove(e_type)

        cls.types = Enum('EntityType', ' '.join(e_type_names))

    @classmethod
    def registered(cls, e_type):
        """
        Returns True if the given entity type is registered, False otherwise.
        """
        result = None
        try:
            result = e_type.name in [e_type.name for e_type in cls.types]
        except AttributeError:
            result = e_type in [e_type.name for e_type in cls.types]

        return result
