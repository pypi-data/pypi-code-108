'''_1062.py

GearAlignment
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_GEAR_ALIGNMENT = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'GearAlignment')


__docformat__ = 'restructuredtext en'
__all__ = ('GearAlignment',)


class GearAlignment(_0.APIBase):
    '''GearAlignment

    This is a mastapy class.
    '''

    TYPE = _GEAR_ALIGNMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearAlignment.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def roll_distance(self) -> 'float':
        '''float: 'RollDistance' is the original name of this property.'''

        return self.wrapped.RollDistance

    @roll_distance.setter
    def roll_distance(self, value: 'float'):
        self.wrapped.RollDistance = float(value) if value else 0.0

    @property
    def roll_angle(self) -> 'float':
        '''float: 'RollAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RollAngle

    @property
    def radius(self) -> 'float':
        '''float: 'Radius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Radius

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Diameter

    @property
    def index_of_reference_tooth(self) -> 'int':
        '''int: 'IndexOfReferenceTooth' is the original name of this property.'''

        return self.wrapped.IndexOfReferenceTooth

    @index_of_reference_tooth.setter
    def index_of_reference_tooth(self, value: 'int'):
        self.wrapped.IndexOfReferenceTooth = int(value) if value else 0
