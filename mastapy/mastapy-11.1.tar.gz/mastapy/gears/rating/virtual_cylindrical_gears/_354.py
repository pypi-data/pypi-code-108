'''_354.py

VirtualCylindricalGear
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import _355
from mastapy._internal.python_net import python_net_import

_VIRTUAL_CYLINDRICAL_GEAR = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'VirtualCylindricalGear')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualCylindricalGear',)


class VirtualCylindricalGear(_355.VirtualCylindricalGearBasic):
    '''VirtualCylindricalGear

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_CYLINDRICAL_GEAR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualCylindricalGear.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def effective_pressure_angle(self) -> 'float':
        '''float: 'EffectivePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectivePressureAngle

    @property
    def transverse_pressure_angle(self) -> 'float':
        '''float: 'TransversePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransversePressureAngle

    @property
    def base_diameter_of_virtual_cylindrical_gear(self) -> 'float':
        '''float: 'BaseDiameterOfVirtualCylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseDiameterOfVirtualCylindricalGear

    @property
    def base_pitch_transverse_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'BasePitchTransverseForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasePitchTransverseForVirtualCylindricalGears

    @property
    def base_pitch_normal_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'BasePitchNormalForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasePitchNormalForVirtualCylindricalGears

    @property
    def path_of_addendum_contact_transverse(self) -> 'float':
        '''float: 'PathOfAddendumContactTransverse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PathOfAddendumContactTransverse

    @property
    def path_of_addendum_contact_normal(self) -> 'float':
        '''float: 'PathOfAddendumContactNormal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PathOfAddendumContactNormal

    @property
    def contact_ratio_of_addendum_transverse_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'ContactRatioOfAddendumTransverseForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioOfAddendumTransverseForVirtualCylindricalGears

    @property
    def contact_ratio_of_addendum_normal_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'ContactRatioOfAddendumNormalForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioOfAddendumNormalForVirtualCylindricalGears
