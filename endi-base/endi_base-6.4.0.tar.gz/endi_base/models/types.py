"""
    Custom types and usefull functions
"""
import simplejson as json

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import (
    TypeDecorator,
    Text as Text_type,
)
from pyramid.authorization import (
    Allow,
    ALL_PERMISSIONS,
)


class JsonEncodedDict(TypeDecorator):
    """
    Stores a dict as a json string in the database
    """
    impl = Text_type

    def process_bind_param(self, value, dialect):
        """
            Process params when setting the value
        """
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """
            Processing the value when getting the value
        """
        if value is not None:
            value = json.loads(value)
        return value


class JsonEncodedList(TypeDecorator):
    """
    Stores a list as a json string
    """
    impl = Text_type

    def process_bind_param(self, value, dialect):
        """
            Process params when setting the value
        """
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        """
            Processing the value when getting the value
        """
        if value is not None:
            value = json.loads(value)
        return value


class ACLType(JsonEncodedList):
    all_permissions_serialized = '__ALL_PERMISSIONS__'
    defaults = [
        (Allow, 'group:admin', ALL_PERMISSIONS),
        (Allow, "group:manager", ("manage", "add", "edit", "view")),
    ]

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = [list(ace) for ace in value if ace not in self.defaults]
            for ace in value:
                if ace[2] == ALL_PERMISSIONS:
                    ace[2] = self.all_permissions_serialized
        return JsonEncodedList.process_bind_param(self, value, dialect)

    def process_result_value(self, value, dialect):
        acl = JsonEncodedList.process_result_value(self, value, dialect)
        if acl is not None:
            for ace in acl:
                if ace[2] == self.all_permissions_serialized:
                    ace[2] = ALL_PERMISSIONS
            return self.defaults + [tuple(ace) for ace in acl]


class MutableDict(Mutable, dict):
    """
        Allows sqlalchemy to check if a data has changed in our dict
        If not used, the dbsession will never detect modifications

        Note : only associating a value to one key will work (no subdict
            handling)
    """
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()


class MutableList(Mutable, list):
    """
        Allows sqlalchemy to check if a data has changed in our list
        If not used, the dbsession will never detect modifications
    """
    @classmethod
    def coerce(cls, key, value):
        """
        Convert list to mutablelist
        """
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def append(self, value):
        """
        Detect list append changes
        """
        list.append(self, value)
        self.changed()

    def extend(self, value):
        """
        Detect list append changes
        """
        list.extend(self, value)
        self.changed()

    def remove(self, value):
        """
        Detect list remove change
        """
        list.remove(self, value)
        self.changed()


# Here we always associate our MutableDict to our JsonEncodedDict column type
# If a column is of type JsonEncodedDict, its value will be casted as a
# mutabledict that will signify modifications on setitem and delitem
MutableDict.associate_with(JsonEncodedDict)
# The same for lists
MutableList.associate_with(JsonEncodedList)
