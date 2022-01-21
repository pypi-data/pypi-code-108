'''_0.py

APIBase
'''


from typing import TypeVar
from sys import modules

from mastapy._internal import constructor
from mastapy._internal.cast_exception import CastException
from mastapy._internal.python_net import python_net_import

_API_BASE = python_net_import('SMT.MastaAPI', 'APIBase')


__docformat__ = 'restructuredtext en'
__all__ = ('APIBase',)


class APIBase:
    '''APIBase

    This is a mastapy class.
    '''

    TYPE = _API_BASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'APIBase.TYPE'):
        self.wrapped = instance_to_wrap
        self._freeze()

    __frozen = False

    def __setattr__(self, attr, value):
        prop = getattr(self.__class__, attr, None)
        if isinstance(prop, property):
            prop.fset(self, value)
        else:
            if self.__frozen and attr not in self.__dict__:
                raise AttributeError((
                    'Attempted to set unknown '
                    'attribute: \'{}\''.format(attr))) from None

            super().__setattr__(attr, value)

    def __delattr__(self, name):
        raise AttributeError(
            'Cannot delete the attributes of a mastapy object.') from None

    def _freeze(self):
        self.__frozen = True

    def disconnect_from_masta(self):
        ''' 'DisconnectFromMASTA' is the original name of this method.'''

        self.wrapped.DisconnectFromMASTA()

    def is_instance_of_wrapped_type(self, type_: 'type') -> 'bool':
        ''' 'IsInstanceOfWrappedType' is the original name of this method.

        Args:
            type_ (type)

        Returns:
            bool
        '''

        method_result = self.wrapped.IsInstanceOfWrappedType(type_)
        return method_result

    T_get_property = TypeVar('T_get_property')

    def get_property(self, name: 'str') -> 'T_get_property':
        ''' 'GetProperty' is the original name of this method.

        Args:
            name (str)

        Returns:
            T_get_property
        '''

        name = str(name)
        method_result = self.wrapped.GetProperty(name if name else '')
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def set_property(self, name: 'str', value: 'object'):
        ''' 'SetProperty' is the original name of this method.

        Args:
            name (str)
            value (object)
        '''

        name = str(name)
        self.wrapped.SetProperty(name if name else '', value)

    def is_valid(self, property_name: 'str') -> 'bool':
        ''' 'IsValid' is the original name of this method.

        Args:
            property_name (str)

        Returns:
            bool
        '''

        property_name = str(property_name)
        method_result = self.wrapped.IsValid(property_name if property_name else '')
        return method_result

    def is_read_only(self, property_name: 'str') -> 'bool':
        ''' 'IsReadOnly' is the original name of this method.

        Args:
            property_name (str)

        Returns:
            bool
        '''

        property_name = str(property_name)
        method_result = self.wrapped.IsReadOnly(property_name if property_name else '')
        return method_result

    def documentation_url(self) -> 'str':
        ''' 'DocumentationUrl' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.DocumentationUrl()
        return method_result

    def to_string(self) -> 'str':
        ''' 'ToString' is the original name of this method.

        Returns:
            str
        '''

        method_result = self.wrapped.ToString()
        return method_result

    def initialize_lifetime_service(self) -> 'object':
        ''' 'InitializeLifetimeService' is the original name of this method.

        Returns:
            object
        '''

        method_result = self.wrapped.InitializeLifetimeService()
        return method_result

    def get_hash_code(self) -> 'int':
        ''' 'GetHashCode' is the original name of this method.

        Returns:
            int
        '''

        method_result = self.wrapped.GetHashCode()
        return method_result

    def __eq__(self, other: 'APIBase') -> 'bool':
        ''' 'op_Equality' is the original name of this method.

        Args:
            other (mastapy.APIBase)

        Returns:
            bool
        '''

        method_result = self.wrapped.op_Equality(self.wrapped, other.wrapped if other else None)
        return method_result

    def __ne__(self, other: 'APIBase') -> 'bool':
        ''' 'op_Inequality' is the original name of this method.

        Args:
            other (mastapy.APIBase)

        Returns:
            bool
        '''

        method_result = self.wrapped.op_Inequality(self.wrapped, other.wrapped if other else None)
        return method_result

    def __str__(self):
        part_name = next(filter(None, map(lambda x: getattr(self, x, None),
            ('order', 'node_name', 'name', 'editable_name', 'unique_name'))), None)

        return '{}: {}'.format(self.__class__.__qualname__, part_name) if part_name else repr(self)

    def __repr__(self):
        return '{}()'.format(self.__class__.__qualname__)

    def is_of_type(self, type_) -> bool:
        ''' Method for checking if a mastapy object can be cast to another type.

        Note:
            This method follows all standard casting rules from other languages.

        Args:
            type_: The type to check.

        Returns:
            bool
        '''

        a = type(self.wrapped)
        b = getattr(modules[type_.__module__], type_.__name__).TYPE

        return b in a.__mro__

    def cast_or_none(self, type_):
        ''' Method for casting one mastapy object to another.

        Note:
            This method follows all standard casting rules from other languages.
            This method will return None if the cast fails.

        Args:
            type_: The type to cast to.
        '''

        if not self.is_of_type(type_):
            return None

        return type_(self.wrapped)

    def cast(self, type_):
        ''' Method for casting one mastapy object to another.

        Note:
            This method follows all standard casting rules from other languages.
            This method will raise a CastException if the cast fails.

        Args:
            type_: The type to cast to.
        '''

        if not self.is_of_type(type_):
            raise CastException('Could not cast {} to type {}. Is it a mastapy type?'.format(type(self), type_))

        return type_(self.wrapped)
