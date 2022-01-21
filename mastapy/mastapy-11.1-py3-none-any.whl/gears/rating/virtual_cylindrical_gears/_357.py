'''_357.py

VirtualCylindricalGearISO10300MethodB2
'''


from mastapy._internal import constructor
from mastapy.gears.rating.virtual_cylindrical_gears import _355
from mastapy._internal.python_net import python_net_import

_VIRTUAL_CYLINDRICAL_GEAR_ISO10300_METHOD_B2 = python_net_import('SMT.MastaAPI.Gears.Rating.VirtualCylindricalGears', 'VirtualCylindricalGearISO10300MethodB2')


__docformat__ = 'restructuredtext en'
__all__ = ('VirtualCylindricalGearISO10300MethodB2',)


class VirtualCylindricalGearISO10300MethodB2(_355.VirtualCylindricalGearBasic):
    '''VirtualCylindricalGearISO10300MethodB2

    This is a mastapy class.
    '''

    TYPE = _VIRTUAL_CYLINDRICAL_GEAR_ISO10300_METHOD_B2

    __hash__ = None

    def __init__(self, instance_to_wrap: 'VirtualCylindricalGearISO10300MethodB2.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def relative_mean_back_cone_distance(self) -> 'float':
        '''float: 'RelativeMeanBackConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMeanBackConeDistance

    @property
    def relative_mean_virtual_pitch_radius(self) -> 'float':
        '''float: 'RelativeMeanVirtualPitchRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMeanVirtualPitchRadius

    @property
    def relative_mean_virtual_dedendum(self) -> 'float':
        '''float: 'RelativeMeanVirtualDedendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMeanVirtualDedendum

    @property
    def relative_virtual_tooth_thickness(self) -> 'float':
        '''float: 'RelativeVirtualToothThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeVirtualToothThickness

    @property
    def relative_mean_virtual_tip_radius(self) -> 'float':
        '''float: 'RelativeMeanVirtualTipRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMeanVirtualTipRadius

    @property
    def relative_edge_radius_of_tool(self) -> 'float':
        '''float: 'RelativeEdgeRadiusOfTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeEdgeRadiusOfTool

    @property
    def adjusted_pressure_angle(self) -> 'float':
        '''float: 'AdjustedPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdjustedPressureAngle

    @property
    def relative_mean_base_radius_of_virtual_cylindrical_gear(self) -> 'float':
        '''float: 'RelativeMeanBaseRadiusOfVirtualCylindricalGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMeanBaseRadiusOfVirtualCylindricalGear

    @property
    def relative_length_of_action_from_tip_to_pitch_circle_in_normal_section(self) -> 'float':
        '''float: 'RelativeLengthOfActionFromTipToPitchCircleInNormalSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeLengthOfActionFromTipToPitchCircleInNormalSection

    @property
    def relative_mean_normal_pitch_for_virtual_cylindrical_gears(self) -> 'float':
        '''float: 'RelativeMeanNormalPitchForVirtualCylindricalGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelativeMeanNormalPitchForVirtualCylindricalGears
