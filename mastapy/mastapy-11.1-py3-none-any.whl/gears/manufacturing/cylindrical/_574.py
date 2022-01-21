'''_574.py

CylindricalGearSpecifiedProfile
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SPECIFIED_PROFILE = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Cylindrical', 'CylindricalGearSpecifiedProfile')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSpecifiedProfile',)


class CylindricalGearSpecifiedProfile(_0.APIBase):
    '''CylindricalGearSpecifiedProfile

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SPECIFIED_PROFILE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSpecifiedProfile.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def offset_at_minimum_roll_distance(self) -> 'float':
        '''float: 'OffsetAtMinimumRollDistance' is the original name of this property.'''

        return self.wrapped.OffsetAtMinimumRollDistance

    @offset_at_minimum_roll_distance.setter
    def offset_at_minimum_roll_distance(self, value: 'float'):
        self.wrapped.OffsetAtMinimumRollDistance = float(value) if value else 0.0
