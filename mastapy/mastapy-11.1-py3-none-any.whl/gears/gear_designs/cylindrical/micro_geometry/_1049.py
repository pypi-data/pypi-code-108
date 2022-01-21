'''_1049.py

CylindricalGearLeadModificationAtProfilePosition
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _981
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1048
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_LEAD_MODIFICATION_AT_PROFILE_POSITION = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearLeadModificationAtProfilePosition')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearLeadModificationAtProfilePosition',)


class CylindricalGearLeadModificationAtProfilePosition(_1048.CylindricalGearLeadModification):
    '''CylindricalGearLeadModificationAtProfilePosition

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_LEAD_MODIFICATION_AT_PROFILE_POSITION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearLeadModificationAtProfilePosition.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def position_on_profile_factor(self) -> 'float':
        '''float: 'PositionOnProfileFactor' is the original name of this property.'''

        return self.wrapped.PositionOnProfileFactor

    @position_on_profile_factor.setter
    def position_on_profile_factor(self, value: 'float'):
        self.wrapped.PositionOnProfileFactor = float(value) if value else 0.0

    @property
    def profile_measurement(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'ProfileMeasurement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.ProfileMeasurement) if self.wrapped.ProfileMeasurement is not None else None
