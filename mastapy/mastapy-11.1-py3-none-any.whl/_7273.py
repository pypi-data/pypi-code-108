'''_7273.py

ScriptedPropertyNameAttribute
'''


from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_SCRIPTED_PROPERTY_NAME_ATTRIBUTE = python_net_import('SMT.MastaAPIUtility', 'ScriptedPropertyNameAttribute')


__docformat__ = 'restructuredtext en'
__all__ = ('ScriptedPropertyNameAttribute',)


class ScriptedPropertyNameAttribute:
    '''ScriptedPropertyNameAttribute

    This is a mastapy class.
    '''

    TYPE = _SCRIPTED_PROPERTY_NAME_ATTRIBUTE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ScriptedPropertyNameAttribute.TYPE'):
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

    @property
    def property_name(self) -> 'str':
        '''str: 'PropertyName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PropertyName
