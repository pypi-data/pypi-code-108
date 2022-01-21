'''_932.py

KlingelnbergCycloPalloidSpiralBevelGearSetDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.klingelnberg_spiral_bevel import _930, _931
from mastapy.gears.gear_designs.klingelnberg_conical import _940
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergSpiralBevel', 'KlingelnbergCycloPalloidSpiralBevelGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidSpiralBevelGearSetDesign',)


class KlingelnbergCycloPalloidSpiralBevelGearSetDesign(_940.KlingelnbergConicalGearSetDesign):
    '''KlingelnbergCycloPalloidSpiralBevelGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidSpiralBevelGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mean_normal_module(self) -> 'float':
        '''float: 'MeanNormalModule' is the original name of this property.'''

        return self.wrapped.MeanNormalModule

    @mean_normal_module.setter
    def mean_normal_module(self, value: 'float'):
        self.wrapped.MeanNormalModule = float(value) if value else 0.0

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalPressureAngle

    @normal_pressure_angle.setter
    def normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalPressureAngle = float(value) if value else 0.0

    @property
    def mean_transverse_module(self) -> 'float':
        '''float: 'MeanTransverseModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanTransverseModule

    @property
    def number_of_teeth_of_crown_wheel(self) -> 'float':
        '''float: 'NumberOfTeethOfCrownWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfTeethOfCrownWheel

    @property
    def wheel_inner_cone_distance(self) -> 'float':
        '''float: 'WheelInnerConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelInnerConeDistance

    @property
    def hw(self) -> 'float':
        '''float: 'HW' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HW

    @property
    def cutter_blade_tip_width(self) -> 'float':
        '''float: 'CutterBladeTipWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterBladeTipWidth

    @property
    def virtual_number_of_teeth_on_inside_diameter(self) -> 'float':
        '''float: 'VirtualNumberOfTeethOnInsideDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualNumberOfTeethOnInsideDiameter

    @property
    def minimum_addendum_modification_factor(self) -> 'float':
        '''float: 'MinimumAddendumModificationFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumAddendumModificationFactor

    @property
    def transverse_pressure_angle(self) -> 'float':
        '''float: 'TransversePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransversePressureAngle

    @property
    def settling_angle(self) -> 'float':
        '''float: 'SettlingAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SettlingAngle

    @property
    def helix_angle_at_base_circle_of_virtual_gear(self) -> 'float':
        '''float: 'HelixAngleAtBaseCircleOfVirtualGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleAtBaseCircleOfVirtualGear

    @property
    def virtual_number_of_pinion_teeth_at_mean_cone_distance(self) -> 'float':
        '''float: 'VirtualNumberOfPinionTeethAtMeanConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualNumberOfPinionTeethAtMeanConeDistance

    @property
    def tooth_tip_width_for_reduction(self) -> 'float':
        '''float: 'ToothTipWidthForReduction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothTipWidthForReduction

    @property
    def width_of_tooth_tip_chamfer(self) -> 'float':
        '''float: 'WidthOfToothTipChamfer' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WidthOfToothTipChamfer

    @property
    def virtual_number_of_wheel_teeth_at_mean_cone_distance(self) -> 'float':
        '''float: 'VirtualNumberOfWheelTeethAtMeanConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualNumberOfWheelTeethAtMeanConeDistance

    @property
    def partial_contact_ratio_of_virtual_pinion_teeth(self) -> 'float':
        '''float: 'PartialContactRatioOfVirtualPinionTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PartialContactRatioOfVirtualPinionTeeth

    @property
    def partial_contact_ratio_of_virtual_wheel_teeth(self) -> 'float':
        '''float: 'PartialContactRatioOfVirtualWheelTeeth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PartialContactRatioOfVirtualWheelTeeth

    @property
    def profile_contact_ratio_in_transverse_section(self) -> 'float':
        '''float: 'ProfileContactRatioInTransverseSection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileContactRatioInTransverseSection

    @property
    def face_contact_angle(self) -> 'float':
        '''float: 'FaceContactAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceContactAngle

    @property
    def cutter_tooth_fillet_radius(self) -> 'float':
        '''float: 'CutterToothFilletRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterToothFilletRadius

    @property
    def outer_cone_distance_face_width(self) -> 'float':
        '''float: 'OuterConeDistanceFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterConeDistanceFaceWidth

    @property
    def face_width_normal_module(self) -> 'float':
        '''float: 'FaceWidthNormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthNormalModule

    @property
    def circular_pitch(self) -> 'float':
        '''float: 'CircularPitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CircularPitch

    @property
    def gears(self) -> 'List[_930.KlingelnbergCycloPalloidSpiralBevelGearDesign]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearDesign]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_930.KlingelnbergCycloPalloidSpiralBevelGearDesign))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gears(self) -> 'List[_930.KlingelnbergCycloPalloidSpiralBevelGearDesign]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearDesign]: 'KlingelnbergCycloPalloidSpiralBevelGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelGears, constructor.new(_930.KlingelnbergCycloPalloidSpiralBevelGearDesign))
        return value

    @property
    def klingelnberg_conical_meshes(self) -> 'List[_931.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearMeshDesign]: 'KlingelnbergConicalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergConicalMeshes, constructor.new(_931.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign))
        return value

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_meshes(self) -> 'List[_931.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign]':
        '''List[KlingelnbergCycloPalloidSpiralBevelGearMeshDesign]: 'KlingelnbergCycloPalloidSpiralBevelMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidSpiralBevelMeshes, constructor.new(_931.KlingelnbergCycloPalloidSpiralBevelGearMeshDesign))
        return value
