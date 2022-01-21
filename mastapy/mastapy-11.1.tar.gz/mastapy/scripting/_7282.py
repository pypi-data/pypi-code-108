'''_7282.py

MastaPropertyAttribute
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.units_and_measurements import _7276
from mastapy._internal.python_net import python_net_import

_MASTA_PROPERTY_ATTRIBUTE = python_net_import('SMT.MastaAPIUtility.Scripting', 'MastaPropertyAttribute')


__docformat__ = 'restructuredtext en'
__all__ = ('MastaPropertyAttribute',)


class MastaPropertyAttribute:
    '''MastaPropertyAttribute

    This is a mastapy class.
    '''

    TYPE = _MASTA_PROPERTY_ATTRIBUTE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MastaPropertyAttribute.TYPE'):
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
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def description(self) -> 'str':
        '''str: 'Description' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Description

    @property
    def symbol(self) -> 'str':
        '''str: 'Symbol' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Symbol

    @property
    def measurement(self) -> '_7276.MeasurementType':
        '''MeasurementType: 'Measurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.Measurement)
        return constructor.new(_7276.MeasurementType)(value) if value is not None else None
