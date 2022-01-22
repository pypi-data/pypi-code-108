"""
A collection of classes and interfaces supporting the construction of data transfer objects for moving data between
HEA microservices as well as between a HEA microservice and a web browser or other client. The HEAObject is the root
interface for these data transfer objects, and AbstractHEAObject provides a root abstract implementation for them.
See HEAObject's docstring for details.
"""

import json
from datetime import date, time
from .error import DeserializeException
from . import user
from enum import auto, Enum
from typing import Optional, List, Union, Any, Type, Iterator, Callable, Dict, TypeVar
import dateutil.parser
import importlib
import copy
import inspect
import abc
import logging


PRIMITIVE_ATTRIBUTE_TYPES = (int, float, str, bool, Enum, type(None), date, time)


Primitive = Optional[Union[int, float, str, bool, Enum, date, time]]
MemberObjectDict = Dict[str, Union[Primitive, List[Primitive]]]
HEAObjectDictValueTypeVar = TypeVar('HEAObjectDictValueTypeVar', List[MemberObjectDict], MemberObjectDict, List[Primitive], Primitive)
HEAObjectDictValue = Optional[Union[List[MemberObjectDict], MemberObjectDict, List[Primitive], Primitive]]
DesktopObjectDict = Dict[str, HEAObjectDictValueTypeVar]
HEAObjectDict = Union[DesktopObjectDict, MemberObjectDict]


class EnumAutoName(Enum):
    """
    Subclass of Enum in which auto() returns the name as a string.
    """
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self) -> str:
        return self.name

class Permission(EnumAutoName):
    """
    The standard permissions that apply to all HEA desktop objects.
    """
    VIEWER = auto()
    EDITOR = auto()
    COOWNER = auto()
    EXECUTOR = auto()
    SHARER = auto()


class HEAObject(abc.ABC):
    """
    Interface for all HEA objects. HEA objects are data transfer objects for moving data between HEA microservices as
    well as between a HEA microservice and a web browser or other client. HEA objects have no behavior except support
    for storage, retrieval, serialization, and deserialization. The AbstractHEAObject class provides default
    implementations for setting and getting attributes, as well as default implementations of behaviors.

    There are two sub-types of HEA objects: desktop objects (DesktopObject) and owned
    objects (MemberObject). The AbstractDesktopObject and AbstractMemberObject classes provide default implementations
    for setting and getting attributes, and default implementations of behaviors. There may be additional sub-types in
    the future.

    Desktop objects represent objects that appear on the HEA desktop. Desktop objects have permissions, timestamps for
    when the object was created and modified, versions, and more. One or more HEA microservices provide CRUD (create,
    read, update, and delete) operations on each desktop object type. Additional HEA microservices may implement actions
    that consume or produce specific desktop object types.

    Member objects cannot appear by themselves on the HEA desktop. Instead, they have a part-of relationship with a
    desktop object, and their lifecycle is managed by the desktop object. Example member objects represent permissions
    and data sharing. While owned objects provide for their own storage, retrieval, serialization, and deserialization,
    these behaviors are always invoked by the desktop object of which they are a part. HEA objects may contain only one
    level of nested members.

    HEA objects must conform to several conventions to ease their use and reuse across the HEA desktop.
    All subclasses of HEAObject must have a zero-argument constructor. Attribute values may be strings, numbers, booleans,
    enums, or a HEA object; or a list of strings, numbers, booleans, enums, or HEA objects. Attributes of type enum
    must be implemented as a property with a setter that accepts both strings and the enum values, and will convert the
    strings to enum values.

    In general, HEA objects implement composition relationships by making the container a desktop object and the "owned"
    object a member object. Other association relationships are implemented by storing the id of the associated object
    rather than nesting it. By convention, the id attributes are named hea_object_class_name_id, where hea_object_class_name
    is the name of the class converted from camel case to underscores. There is one exception to this convention in the
    heaobject library. Item objects contain a nested copy of the desktop object that they refer to.

    Copies and deep copies using the copy module will copy all non-callable instance members of any subclass of HEAObject.

    In addition, HEA objects should include type annotations throughout.

    It is imperative that users gain access to desktop objects by calling an appropriate HEA microservice as themselves, which
    will filter any nested member objects that are returned according to their permissions.
    """

    @abc.abstractmethod
    def to_dict(self) -> HEAObjectDict:
        """
        Returns a dict containing the attributes of this HEAObject instance. It gets the attributes to include by
        calling the get_attributes class method.

        :return: a dict of attribute names to attribute values.
        """
        pass

    @abc.abstractmethod
    def json_dumps(self, dumps: Callable[[HEAObjectDict], str] = json.dumps) -> str:
        """
        Returns a JSON-formatted string from the attributes of this instance. Passes the json_encode function as the
        default parameter.

        :param dumps: any callable that accepts a HEAObject and returns a string.
        :return: a string.
        """
        pass

    @abc.abstractmethod
    def json_loads(self, jsn: str, loads: Callable[[Union[str]], HEAObjectDict] = json.loads) -> None:
        """
        Populates the object's attributes with the property values in the provided JSON. If the provided JSON has a
        type property, this method requires that it match this object's type.

        :param jsn: a JSON string.
        :param loads: any callable that accepts str and returns dict with parsed JSON (json.loads() by default).
        :raises DeserializeException: if any of the JSON object's values are wrong, or the provided JSON
        document is not a valid JSON document.
        """
        pass

    @abc.abstractmethod
    def from_dict(self, d: HEAObjectDict) -> None:
        """
        Populates the object's attributes with the property values in the given dict.

        The supplied mapping may have nested dicts and lists. Dicts must have a type key whose value is a HEAObject type name, and
        the other entries should correspond to attributes of that HEAObject type. Lists may contain strings, numbers, booleans, or dicts
        corresponding to an HEAObject type. Dict entries that correspond to read-only properties are ignored, as are
        entries that do not have a corresponding attribute in the HEAObject type.

        TODO: return self from this method.

        :param d: a mapping.
        :raises DeserializeException: if any of the mapping's values are wrong.
        """
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def type(self) -> str:
        """
        The string representation of this object's type.

        :return: a string.
        """
        pass

    @abc.abstractmethod
    def get_attributes(self) -> Iterator[str]:
        """
        Returns a tuple containing the attributes that to_dict will write to a dictionary.

        :return: an iterator of attribute names.
        """
        pass

    @abc.abstractmethod
    def get_all_attributes(self) -> Iterator[str]:
        """
        Returns a tuple containing all of this object's attributes.

        :return: an iterator of attribute names.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_prompt(cls, field_name: Optional[str]) -> Optional[str]:
        pass

    @classmethod
    @abc.abstractmethod
    def is_displayed(cls, field_name: Optional[str]) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def get_type_name(cls) -> str:
        """
        Returns a string representation of a HEAObject type.

        :return: a type string.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_type_display_name(cls) -> Optional[str]:
        """
        Returns a display name for the HEAObject type, or None if there is no display name for this type.

        :return: the display name string
        """
        pass


class MemberObject(HEAObject, abc.ABC):
    """
    Interface for HEA objects that have a part-of relationship with a desktop objects and whose lifecycle is
    managed by the desktop object. Owned objects have the same permissions as the owning desktop object. As a result,
    they can be accessed by anyone who can access the desktop object, and they can be modified by anyone who can modify
    the desktop object.
    """
    pass


class PermissionAssignment(MemberObject, abc.ABC):
    """
    Interface for permission assignments for desktop objects. Desktop objects are owned by the user who created them.
    After creating an object, the object's owner can share the object with other users with the desired set of
    permissions. Optionally, users can invite another users to access the object with the desired set of permissions,
    and the user will receive access upon accepting the invite. Permission assignment objects are owned by a desktop
    object. As a result, they can be accessed by anyone who can access the desktop object, and they can be
    modified by anyone who can modify the desktop object.
    """

    @property # type: ignore
    @abc.abstractmethod
    def user(self) -> str:
        """
        The user whose permissions will be impacted.
        """
        pass

    @user.setter  # type: ignore
    @abc.abstractmethod
    def user(self, user: str) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def permissions(self) -> List[Permission]:
        """
        The list of assigned permissions.
        """
        pass

    @permissions.setter  # type: ignore
    @abc.abstractmethod
    def permissions(self, perms: List[Permission]):
        pass


class Invite(PermissionAssignment, abc.ABC):
    """
    Interface for invites to access a desktop object. Invite objects are owned by a desktop object, and as a result they
    do not have permissions of their own.
    """

    @property  # type: ignore
    @abc.abstractmethod
    def accepted(self) -> bool:
        """
        Whether the user has accepted the invite.
        """
        pass

    @accepted.setter  # type: ignore
    @abc.abstractmethod
    def accepted(self, accepted: bool) -> bool:
        pass


class Share(PermissionAssignment, abc.ABC):
    """
    Interface for representing the permissions of users to whom a desktop object has been shared. Share objects are
    owned by a desktop object, and as a result they do not have permissions of their own.
    """

    @property  # type: ignore
    @abc.abstractmethod
    def invite(self) -> Invite:
        """
        The invite, if any.
        """
        pass

    @invite.setter  # type: ignore
    @abc.abstractmethod
    def invite(self, invite: Invite) -> None:
        pass


class DesktopObject(HEAObject, abc.ABC):
    """
    Interface for objects that can appear on the HEA desktop. Desktop objects have permissions, with those permissions
    represented by owned objects implementing the MemberObject interface. Other attributes may also employ owned
    objects. One or more HEA microservices provide CRUD (create, read, update, and delete) operations on each desktop
    object type. Additional HEA microservices may implement actions that use specific desktop object types.

    Desktop objects implement no capability to check the current user when getting and setting owned objects, and
    different users may only have access to a subset of its owned objects. Similarly, owned objects have no knowledge of
    permissions at all. It is imperative that users gain access to desktop objects by calling an appropriate HEA
    microservice as themselves, which will filter the owned objects that are returned according to their permissions.
    """

    @property  # type: ignore
    @abc.abstractmethod
    def id(self) -> Optional[str]:
        """
        The object's resource unique identifier. It must be unique among all objects of the same type.
        """
        pass

    @id.setter  # type: ignore
    @abc.abstractmethod
    def id(self, id_: Optional[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def source(self) -> Optional[str]:
        """
        The id of a Source object representing this object's source.
        """
        pass

    @source.setter  # type: ignore
    @abc.abstractmethod
    def source(self, source: Optional[str]) -> Optional[str]:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def version(self) -> Optional[str]:
        """
        The version of this object.
        """
        pass

    @version.setter  # type: ignore
    @abc.abstractmethod
    def version(self, version: Optional[str]) -> Optional[str]:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def name(self) -> Optional[str]:
        """
        This object's name. The name must be unique across all objects of the same type.
        """
        pass

    @name.setter  # type: ignore
    @abc.abstractmethod
    def name(self, name: Optional[str]) -> Optional[str]:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def display_name(self) -> str:
        """
        The object's display name. The default value is the object's name.
        """
        pass

    @display_name.setter  # type: ignore
    @abc.abstractmethod
    def display_name(self, display_name: Optional[str]) -> str:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def description(self) -> Optional[str]:
        """
        The object's description.
        """
        pass

    @name.setter  # type: ignore
    @abc.abstractmethod
    def description(self, description: Optional[str]) -> Optional[str]:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def owner(self) -> str:
        """
        The username of the object's owner. Cannot be None.
        """
        pass

    @owner.setter  # type: ignore
    @abc.abstractmethod
    def owner(self, owner: str) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def created(self) -> Optional[date]:
        """
        This object's created timestamp as a date object. Setting this property with an ISO 8601
        string will also work -- the ISO string will be parsed automatically as a datetime object.
        """
        pass

    @created.setter  # type: ignore
    @abc.abstractmethod
    def created(self, value: Optional[date]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def modified(self) -> Optional[date]:
        """
        This object's last modified timestamp as a date object. Setting this property with an ISO 8601
        string will also work -- the ISO string will be parsed automatically as a datetime object.
        """
        pass

    @modified.setter  # type: ignore
    @abc.abstractmethod
    def modified(self, value: Optional[date]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def derived_by(self) -> Optional[str]:
        """
        The id of the mechanism by which this object was derived, if any.
        """
        pass

    @derived_by.setter  # type: ignore
    @abc.abstractmethod
    def derived_by(self, derived_by: Optional[str]) -> Optional[str]:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def derived_from(self) -> List[str]:
        """
        A list of the ids of the HEAObjects from which this object was derived. Cannot be None.
        """
        pass

    @derived_from.setter  # type: ignore
    @abc.abstractmethod
    def derived_from(self, derived_from: List[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def invites(self) -> List[Invite]:
        """
        A list of Invite objects representing the users who have been invited to access this object. Cannot be None.
        """
        pass

    @invites.setter  # type: ignore
    @abc.abstractmethod
    def invites(self, invites: List[Invite]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def shares(self) -> List[Share]:
        """
        A list of Share objects representing the users with whom this object has been shared.
        """
        pass

    @shares.setter  # type: ignore
    @abc.abstractmethod
    def shares(self, shares: List[Share]) -> None:
        pass


class AbstractHEAObject(HEAObject, abc.ABC):
    """
    Abstract base class for all HEA objects. HEA objects are data transfer objects for moving data between HEA
    microservices as well as between a HEA microservice and a web browser or other client. HEA objects have no behavior
    except support for storage, retrieval, serialization, and deserialization. The AbstractHEAObject class provides
    default implementations for setting and getting attributes, as well as default implementations of behaviors.

    There are two sub-types of HEA objects: desktop objects (DesktopObject) and owned
    objects (MemberObject). The AbstractDesktopObject and AbstractMemberObject classes provide default implementations
    for setting and getting attributes, and default implementations of behaviors. There may be additional sub-types in
    the future.

    Desktop objects represent objects that appear on the HEA desktop. Desktop objects have permissions, timestamps for
    when the object was created and modified, versions, and more. One or more HEA microservices provide CRUD (create,
    read, update, and delete) operations on each desktop object type. Additional HEA microservices may implement actions
    that consume or produce specific desktop object types.

    Owned objects cannot appear by themselves on the HEA desktop. Instead, they have a part-of relationship with a
    desktop object, and their lifecycle is managed by the desktop object. Example owned objects represent permissions
    and data sharing. While owned objects provide for their own storage, retrieval, serialization, and deserialization,
    these behaviors are always invoked by the desktop object of which they are a part.

    HEA object implementations must conform to several conventions to ease their use and reuse across the HEA desktop.
    All subclasses of HEAObject must have a zero-argument constructor. All non-callable instance members must be
    included in the to_dict() and json_dumps() methods. Copies and deep copies using the copy module will copy all
    non-callable instance members of any subclass of HEAObject. Override __copy__ and __deepcopy__ to change that
    behavior. In addition, HEA objects should include type annotations for all properties and callables.

    Desktop objects implement no capability to check the current user when getting and setting owned objects, and
    different users may only have access to a subset of its owned objects. Similarly, owned objects have no knowledge of
    permissions at all. It is imperative that users gain access to desktop objects by calling an appropriate HEA
    microservice as themselves, which will filter the owned objects that are returned according to their permissions.
    """
    def __init__(self):
        pass

    def to_dict(self) -> HEAObjectDict:
        def nested(obj):
            if isinstance(obj, HEAObject):
                return obj.to_dict()
            elif isinstance(obj, list):
                return [nested(o) for o in obj]
            else:
                return obj

        return {a: nested(getattr(self, a)) for a in self.get_attributes()}

    def json_dumps(self, dumps: Callable[[HEAObjectDict], str] = json.dumps) -> str:
        return dumps(self.to_dict())

    def json_loads(self, jsn: str, loads: Callable[[Union[str]], HEAObjectDict] = json.loads) -> None:
        try:
            self.from_dict(loads(jsn))
        except json.JSONDecodeError as e:
            raise DeserializeException from e

    def from_dict(self, d: HEAObjectDict) -> None:
        try:
            for k, v in d.items():
                if k in self.get_attributes():
                    if isinstance(v, list):
                        lst: List[Union[HEAObject, Primitive]] = []
                        for e in v:
                            if isinstance(e, dict):
                                if 'type' not in e:
                                    raise ValueError(
                                        'type property is required in nested dicts but is missing from {}'.format(e))
                                e_type = e['type']
                                if not isinstance(e_type, str):
                                    raise TypeError(f'type is a {type(e_type)}not a string')
                                obj = type_for_name(e_type)()
                                obj.from_dict(e)
                                lst.append(obj)
                            else:
                                lst.append(e)
                        self.__setattr_known_and_writeable(k, lst)
                    elif isinstance(v, dict):
                        if 'type' not in v:
                            raise ValueError(
                                'type property is required in nested dicts but is missing from {}'.format(v))
                        v_type = v['type']
                        if not isinstance(v_type, str):
                            raise TypeError(f'type is {type(v_type)} but must be a str')
                        obj = type_for_name(v_type)()
                        obj.from_dict(v)
                        self.__setattr_known_and_writeable(k, obj)
                    elif k != 'type':
                        self.__setattr_known_and_writeable(k, v)
                    else:
                        if v != self.type:
                            raise ValueError(
                                f"type property does not match object type: object type is {self.type} but the dict's type property has value {v}")
        except (ValueError, TypeError) as e:
            raise DeserializeException from e

    @property
    def type(self) -> str:
        return self.get_type_name()

    def get_attributes(self) -> Iterator[str]:
        return (m[0] for m in inspect.getmembers(self, self.__is_not_callable)
                if not m[0].startswith('_') and m not in inspect.getmembers(type(self), self.__is_not_callable))

    def get_all_attributes(self) -> Iterator[str]:
        return (m[0] for m in inspect.getmembers(self, self.__is_not_callable)
                if not m[0].startswith('_') and m not in inspect.getmembers(type(self), self.__is_not_callable))

    @classmethod
    def get_prompt(cls, field_name: Optional[str]) -> Optional[str]:
        return field_name

    @classmethod
    def is_displayed(cls, field_name: Optional[str]) -> bool:
        return True if field_name != 'id' else False

    @classmethod
    def get_type_name(cls) -> str:
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def get_type_display_name(cls) -> Optional[str]:
        """
        Returns a display name for the HEAObject type, or None if there is no display name for this type. The default
        implementation returns None. A concrete type implementation should override this method to return a display
        name for the type.

        :return: the display name string
        """
        return cls.__name__

    @staticmethod
    def __is_not_callable(x) -> bool:
        return not callable(x)

    def __setattr_known_and_writeable(self, name: str, value: Any) -> None:
        """
        Sets any of this object's attributes, ignoring attempts to set read-only attributes or to monkey patch the object with additional attributes.

        :param name: the name of the attribute.
        :param value: the attribute's value.
        """
        logger = logging.getLogger()
        if hasattr(self, name):
            try:
                setattr(self, name, value)
            except AttributeError:
                logger.debug('Tried setting attribute %s.%s=%s and got an error, most likely because the attribute is read-only. HEA will ignore this attribute.', self, name, value, exc_info=True)
        else:
            logger.debug('Attempted to set an unexpected attribute %s.%s=%s. HEA will ignore this attribute.', self, name, value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        attrs = set(self.get_all_attributes()).union(other.get_all_attributes())
        return all(getattr(self, a, None) == getattr(other, a, None) for a in attrs)

    def __repr__(self) -> str:
        return 'heaobject.root.from_dict(' + repr(self.to_dict()) + ')'

    def __copy__(self):
        clz = type(self)
        result = clz()
        for a in self.get_attributes():
            try:
                setattr(result, a, getattr(self, a))
            except AttributeError:
                pass  # Skip read-only attributes
        return result

    def __deepcopy__(self, memo):
        result = type(self)()
        for a in self.get_attributes():
            try:
                setattr(result, a, copy.deepcopy(getattr(self, a), memo))
            except AttributeError:
                pass  # Skip read-only attributes
        return result


class AbstractMemberObject(AbstractHEAObject, MemberObject, abc.ABC):
    """
    Abstract base class for all classes that are owned by a desktop class. Owned classes have a part-of relationship
    with a desktop class, and their lifecycle is managed by the desktop class. The desktop class and this class have a
    composition relationship in UML. Owned objects have the same permissions as the owning desktop object. As a result,
    they can be accessed by anyone who can access the desktop object, and they can be modified by anyone who can modify
    the desktop object.
    """
    pass


class AbstractPermissionAssignment(AbstractMemberObject, PermissionAssignment, abc.ABC):
    """
    Abstract base class for permissions-related classes. Desktop objects are owned by the user who created them.
    After creating an object, the object's owner can share the object with other users with the desired set of
    permissions. Optionally, users can invite another users to access the object with the desired set of permissions,
    and the user will receive access upon accepting the invite. Permission assignment objects are owned by a desktop
    object. As a result, they can be accessed by anyone who can access the desktop object, and they can be
    modified by anyone who can modify the desktop object.
    """
    def __init__(self):
        super().__init__()
        self.__user = user.NONE_USER
        self.__permissions: List[Permission] = []

    @property
    def user(self) -> str:
        return self.__user

    @user.setter
    def user(self, user: str) -> None:
        self.__user = str(user)

    @property
    def permissions(self) -> List[Permission]:
        """
        List of granted permissions. Any strings in the list will be parsed into Permission objects. Cannot be None.
        Attempting to set this property to None will result in setting it to the empty list.
        """
        return copy.deepcopy(self.__permissions)

    @permissions.setter
    def permissions(self, perms: List[Permission]):
        if perms is None:
            self.__permissions = []
        else:
            perms_ = []
            for p in perms:
                if isinstance(p, str):
                    perms_.append(Permission[p])
                elif isinstance(p, Permission):
                    perms_.append(p)
                else:
                    raise KeyError("permissions can only be a list of Permission objects or strings that can be converted to Permission objects")
            self.__permissions = perms_


class InviteImpl(AbstractPermissionAssignment, Invite):
    """
    Implementation of an invite.
    """
    def __init__(self):
        super().__init__()
        self.__accepted = False

    @property
    def accepted(self) -> bool:
        return self.__accepted

    @accepted.setter
    def accepted(self, accepted: bool) -> None:
        self.__accepted = bool(accepted)


class ShareImpl(AbstractPermissionAssignment, Share):
    """
    Implementation of a share.
    """
    def __init__(self):
        super().__init__()
        self.__invite: Invite = None

    @property
    def invite(self) -> Invite:
        return self.__invite

    @invite.setter
    def invite(self, invite: Invite) -> None:
        if invite is not None and not isinstance(invite, Invite):
            raise TypeError('invite not an Invite')
        self.__invite = copy.deepcopy(invite)


class AbstractDesktopObject(AbstractHEAObject, DesktopObject, abc.ABC):
    """
    Abstract base class representing HEA desktop objects. Desktop objects have permissions, with those permissions
    represented by owned objects implementing the MemberObject interface. Other attributes may also employ owned
    objects.

    Desktop objects implement no capability to check the current user when getting and setting owned objects, and
    different users may only have access to a subset of its owned objects. Similarly, owned objects have no knowledge of
    permissions at all. It is imperative that users gain access to desktop objects by calling an appropriate HEA
    microservice as themselves, which will filter the owned objects that are returned according to their permissions.
    """

    def __init__(self):
        super().__init__()
        self.__id: Optional[str] = None
        self.__source: Optional[str] = None
        self.__version: Optional[str] = None
        self.__name: Optional[str] = None
        self.__display_name: str = self.__default_display_name()
        self.__description: Optional[str] = None
        self.__owner = user.NONE_USER
        self.__created: Optional[date] = None  # The date when the object was created
        self.__modified: Optional[date] = None  # The date when the object was last modified
        self.__invites: List[Invite] = []
        self.__shares: List[Share] = []
        self.__derived_by = None
        self.__derived_from = []

    @property
    def id(self) -> Optional[str]:
        return self.__id

    @id.setter
    def id(self, id_: Optional[str]) -> None:
        self.__id = str(id_) if id_ is not None else None

    @property
    def source(self) -> Optional[str]:
        return self.__source

    @source.setter
    def source(self, source: Optional[str]) -> None:
        self.__source = str(source) if source is not None else None

    @property
    def version(self) -> Optional[str]:
        return self.__version

    @version.setter
    def version(self, version: Optional[str]) -> None:
        self.__version = str(version) if version is not None else None

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self.__name = str(name) if name is not None else None

    @property
    def display_name(self) -> str:
        return self.__display_name

    @display_name.setter
    def display_name(self, display_name: str) -> None:
        if display_name is not None:
            self.__display_name = str(display_name)
        elif self.name is not None:
            self.__display_name = self.name
        else:
            self.__display_name = self.__default_display_name()

    @property
    def description(self) -> Optional[str]:
        return self.__description

    @description.setter
    def description(self, description: Optional[str]) -> None:
        self.__description = str(description) if description is not None else None

    @property
    def owner(self) -> str:
        return self.__owner

    @owner.setter
    def owner(self, owner: str) -> None:
        self.__owner = str(owner)

    @property
    def created(self) -> Optional[date]:
        return self.__created

    @created.setter
    def created(self, value: Optional[date]) -> None:
        if value is None or isinstance(value, date):
            self.__created = value
        else:
            self.__created = dateutil.parser.isoparse(value)

    @property
    def modified(self) -> Optional[date]:
        return self.__modified

    @modified.setter
    def modified(self, value: Optional[date]) -> None:
        if value is None or isinstance(value, date):
            self.__modified = value
        else:
            self.__modified = dateutil.parser.isoparse(value)

    @property
    def derived_by(self) -> Optional[str]:
        return self.__derived_by

    @derived_by.setter
    def derived_by(self, derived_by: Optional[str]) -> None:
        self.__derived_by = str(derived_by) if derived_by is not None else None

    @property
    def derived_from(self) -> List[str]:
        return list(self.__derived_from)

    @derived_from.setter
    def derived_from(self, derived_from: List[str]) -> None:
        if derived_from is None:
            raise ValueError('derived_from cannot be None')
        if not all(isinstance(s, str) for s in derived_from):
            raise KeyError('derived_from can only contain str objects')
        self.__derived_from = copy.deepcopy(list(derived_from) if isinstance(derived_from, list) else derived_from)

    @property
    def invites(self) -> List[Invite]:
        """
        A list of Invite objects representing the users who have been invited to access this object. Cannot be None.
        """
        return copy.deepcopy(self.__invites)

    @invites.setter
    def invites(self, invites: List[Invite]) -> None:
        if invites is None:
            raise ValueError('invites cannot be None')
        if not all(isinstance(s, Invite) for s in invites):
            raise KeyError('invites can only contain Invite objects')
        self.__invites = copy.deepcopy(list(invites) if isinstance(invites, list) else invites)

    @property
    def shares(self) -> List[Share]:
        """
        A list of Share objects representing the users with whom this object has been shared.
        """
        return copy.deepcopy(self.__shares)

    @shares.setter
    def shares(self, shares: List[Share]) -> None:
        if shares is None:
            raise ValueError("shares cannot be None")
        if not all(isinstance(s, Share) for s in shares):
            raise KeyError("shares can only contain Share objects")
        self.__shares = copy.deepcopy(list(shares) if isinstance(shares, list) else shares)

    def __default_display_name(self):
        return 'Untitled ' + self.get_type_display_name()

    def __str__(self) -> str:
        """
        Returns the object's display name.
        :return: the display name.
        """
        return self.display_name


def json_dumps(o: Any):
    """
    Serialize a HEAObject, a date, or a JSON-serializable object supported by default by json.dumps.

    :param o: the object to serialize.
    :return: a JSON document.
    """
    return json.dumps(o, default=json_encode)


def json_encode(o: Any) -> Union[str, HEAObjectDict]:
    """
    Function to pass into the json.dumps default parameter that customizes encoding for HEAObjects, dates, and enums.

    :param o: the object to encode.
    :return: the object after encoding.
    :raise TypeError: if the object is neither a HEAObject nor a date.
    """
    if isinstance(o, HEAObject):
        return o.to_dict()
    elif isinstance(o, date):
        return o.isoformat()
    elif isinstance(o, Enum):
        return str(o)
    raise TypeError('values must be HEAObject, date, or a value type supported by json.dumps by default')


def is_primitive(obj: Any) -> bool:
    """
    Returns whether the argument is an instance of a HEA primitive type (int, float, str, bool, Enum, or NoneType).
    :return: True or False.
    """
    return isinstance(obj, PRIMITIVE_ATTRIBUTE_TYPES)


def is_primitive_list(obj: Any) -> bool:
    """
    Returns whether the argument is a list of HEA primitive types. Will return True if passed an empty list.
    :return: True or False.
    """
    return isinstance(obj, list) and all(is_primitive(elt) for elt in obj)


def is_member_object(obj: Any) -> bool:
    """
    Returns whether the argument is a MemberObject.
    :return: True or False.
    """
    return isinstance(obj, MemberObject)


def is_member_object_list(obj: Any) -> bool:
    """
    Returns whether the argument is an iterable of MemberObjects. Will return False if passed an empty list.
    :return: True or False.
    """
    return isinstance(obj, list) and len(obj) > 0 and all(isinstance(elt, MemberObject) for elt in obj)


def is_heaobject_dict(obj: Any) -> bool:
    """
    Returns whether the argument is an HEAObject dict, defined as a dict with a type key.
    :return: True or False.
    """
    return isinstance(obj, dict) and 'type' in obj


def is_heaobject_dict_list(obj: Any):
    """
    Returns whether the argument is a list of HEAObject dicts. Will return False if passed an empty list.
    :return: True or False.
    """
    return isinstance(obj, list) and len(obj) > 0 and all(is_heaobject_dict(elt) for elt in obj)


def is_heaobject_type(name: str) -> bool:
    """
    Returns whether the supplied string is the name of an HEAObject type.

    :param name: a string.
    :return: True if the string is the name of an HEAObject type, or False if not.
    """
    try:
        mod_str, cls_str = name.rsplit('.', 1)
        result = getattr(importlib.import_module(mod_str), cls_str)
        if not issubclass(result, HEAObject):
            return False
        return True
    except ValueError:
        return False


def type_for_name(name: str) -> Type[HEAObject]:
    """
    Returns the HEAObject type for the given string.

    :param name: a type string.
    :return: a HEAObject type.
    """
    try:
        mod_str, cls_str = name.rsplit('.', 1)
        result = getattr(importlib.import_module(mod_str), cls_str)
        if not issubclass(result, HEAObject):
            raise TypeError(f'Name must be the name of an HEAObject type, but was {name}')
        return result
    except ValueError:
        raise ValueError(f'{name} does not look like a module path')


def desktop_object_type_for_name(name: str) -> Type[DesktopObject]:
    """
    Returns the HEA desktop object type for the given string.

    :param name: a type string.
    :return: a HEAObject type.
    """
    try:
        name_ = str(name)
        mod_str, cls_str = name_.rsplit('.', 1)
        result = getattr(importlib.import_module(mod_str), cls_str)
        if not issubclass(result, DesktopObject):
            raise TypeError(f'Name must be the name of an DesktopObject type, but was {name_}')
        return result
    except ValueError:
        raise ValueError(f'{name_} does not look like a module path')


def from_dict(d: HEAObjectDict) -> HEAObject:
    """
    Creates a HEA object from the given dict.

    :param d: a dict. It must have, at minimum, a type key with the type name of the HEA object to create. It must
    additionally have key-value pairs for any mandatory attributes of the HEA object.
    :return: a HEAObject.
    """
    type_name = d.get('type', None)
    if not type_name:
        raise ValueError('type key is required')
    if not isinstance(type_name, str):
        raise TypeError(f'type is {type(type_name)} but must be a str')
    obj = type_for_name(type_name)()
    obj.from_dict(d)
    return obj


HEAObjectTypeVar = TypeVar('HEAObjectTypeVar', bound=HEAObject)
DesktopObjectTypeVar = TypeVar('DesktopObjectTypeVar', bound=DesktopObject)
MemberObjectTypeVar = TypeVar('MemberObjectTypeVar', bound=MemberObject)
