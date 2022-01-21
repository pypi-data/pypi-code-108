'''_597.py

ProfileModificationSegment
'''


from mastapy._internal import constructor
from mastapy.gears.manufacturing.cylindrical import _596
from mastapy._internal.python_net import python_net_import

_PROFILE_MODIFICATION_SEGMENT = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'ProfileModificationSegment')


__docformat__ = 'restructuredtext en'
__all__ = ('ProfileModificationSegment',)


class ProfileModificationSegment(_596.ModificationSegment):
    '''ProfileModificationSegment

    This is a mastapy class.
    '''

    TYPE = _PROFILE_MODIFICATION_SEGMENT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ProfileModificationSegment.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def diameter(self) -> 'float':
        '''float: 'Diameter' is the original name of this property.'''

        return self.wrapped.Diameter

    @diameter.setter
    def diameter(self, value: 'float'):
        self.wrapped.Diameter = float(value) if value else 0.0

    @property
    def roll_angle(self) -> 'float':
        '''float: 'RollAngle' is the original name of this property.'''

        return self.wrapped.RollAngle

    @roll_angle.setter
    def roll_angle(self, value: 'float'):
        self.wrapped.RollAngle = float(value) if value else 0.0

    @property
    def roll_distance(self) -> 'float':
        '''float: 'RollDistance' is the original name of this property.'''

        return self.wrapped.RollDistance

    @roll_distance.setter
    def roll_distance(self, value: 'float'):
        self.wrapped.RollDistance = float(value) if value else 0.0

    @property
    def use_iso217712007_slope_sign_convention(self) -> 'bool':
        '''bool: 'UseISO217712007SlopeSignConvention' is the original name of this property.'''

        return self.wrapped.UseISO217712007SlopeSignConvention

    @use_iso217712007_slope_sign_convention.setter
    def use_iso217712007_slope_sign_convention(self, value: 'bool'):
        self.wrapped.UseISO217712007SlopeSignConvention = bool(value) if value else False
