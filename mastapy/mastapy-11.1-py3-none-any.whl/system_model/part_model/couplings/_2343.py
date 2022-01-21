'''_2343.py

SynchroniserCone
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SYNCHRONISER_CONE = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'SynchroniserCone')


__docformat__ = 'restructuredtext en'
__all__ = ('SynchroniserCone',)


class SynchroniserCone(_0.APIBase):
    '''SynchroniserCone

    This is a mastapy class.
    '''

    TYPE = _SYNCHRONISER_CONE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SynchroniserCone.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.'''

        return self.wrapped.Angle

    @angle.setter
    def angle(self, value: 'float'):
        self.wrapped.Angle = float(value) if value else 0.0

    @property
    def coefficient_dynamic_friction(self) -> 'float':
        '''float: 'CoefficientDynamicFriction' is the original name of this property.'''

        return self.wrapped.CoefficientDynamicFriction

    @coefficient_dynamic_friction.setter
    def coefficient_dynamic_friction(self, value: 'float'):
        self.wrapped.CoefficientDynamicFriction = float(value) if value else 0.0

    @property
    def length(self) -> 'float':
        '''float: 'Length' is the original name of this property.'''

        return self.wrapped.Length

    @length.setter
    def length(self, value: 'float'):
        self.wrapped.Length = float(value) if value else 0.0

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.'''

        return self.wrapped.Diameter

    @diameter.setter
    def diameter(self, value: 'float'):
        self.wrapped.Diameter = float(value) if value else 0.0

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
