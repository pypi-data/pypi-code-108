'''_936.py

KlingelnbergCycloPalloidHypoidGearSetDesign
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.gear_designs.klingelnberg_hypoid import _934, _935
from mastapy.gears.gear_designs.klingelnberg_conical import _940
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergHypoid', 'KlingelnbergCycloPalloidHypoidGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSetDesign',)


class KlingelnbergCycloPalloidHypoidGearSetDesign(_940.KlingelnbergConicalGearSetDesign):
    '''KlingelnbergCycloPalloidHypoidGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSetDesign.TYPE'):
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
    def offset(self) -> 'float':
        '''float: 'Offset' is the original name of this property.'''

        return self.wrapped.Offset

    @offset.setter
    def offset(self, value: 'float'):
        self.wrapped.Offset = float(value) if value else 0.0

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.'''

        return self.wrapped.NormalPressureAngle

    @normal_pressure_angle.setter
    def normal_pressure_angle(self, value: 'float'):
        self.wrapped.NormalPressureAngle = float(value) if value else 0.0

    @property
    def pinion_pitch_diameter(self) -> 'float':
        '''float: 'PinionPitchDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionPitchDiameter

    @property
    def angle_modification_applied_to_pinion(self) -> 'float':
        '''float: 'AngleModificationAppliedToPinion' is the original name of this property.'''

        return self.wrapped.AngleModificationAppliedToPinion

    @angle_modification_applied_to_pinion.setter
    def angle_modification_applied_to_pinion(self, value: 'float'):
        self.wrapped.AngleModificationAppliedToPinion = float(value) if value else 0.0

    @property
    def pinion_factor(self) -> 'float':
        '''float: 'PinionFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionFactor

    @property
    def mean_offset_angle(self) -> 'float':
        '''float: 'MeanOffsetAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanOffsetAngle

    @property
    def mean_offset_angle_on_crown_wheel_plane(self) -> 'float':
        '''float: 'MeanOffsetAngleOnCrownWheelPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanOffsetAngleOnCrownWheelPlane

    @property
    def angle_modification_applied_to_wheel(self) -> 'float':
        '''float: 'AngleModificationAppliedToWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngleModificationAppliedToWheel

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
    def offset_crown_wheel_plane(self) -> 'float':
        '''float: 'OffsetCrownWheelPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OffsetCrownWheelPlane

    @property
    def pinion_face_width_crown_wheel_plane(self) -> 'float':
        '''float: 'PinionFaceWidthCrownWheelPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionFaceWidthCrownWheelPlane

    @property
    def pinion_face_width_inside_portion(self) -> 'float':
        '''float: 'PinionFaceWidthInsidePortion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionFaceWidthInsidePortion

    @property
    def additional_face_width_on_pinion(self) -> 'float':
        '''float: 'AdditionalFaceWidthOnPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AdditionalFaceWidthOnPinion

    @property
    def pinion_mean_cone_distance(self) -> 'float':
        '''float: 'PinionMeanConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionMeanConeDistance

    @property
    def pinion_inner_cone_distance(self) -> 'float':
        '''float: 'PinionInnerConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionInnerConeDistance

    @property
    def pinion_outer_cone_distance(self) -> 'float':
        '''float: 'PinionOuterConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionOuterConeDistance

    @property
    def inner_offset_angle(self) -> 'float':
        '''float: 'InnerOffsetAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerOffsetAngle

    @property
    def outer_offset_angle(self) -> 'float':
        '''float: 'OuterOffsetAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OuterOffsetAngle

    @property
    def spiral_angle_at_inner_diameter_pinion(self) -> 'float':
        '''float: 'SpiralAngleAtInnerDiameterPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpiralAngleAtInnerDiameterPinion

    @property
    def spiral_angle_at_outer_diameter_pinion(self) -> 'float':
        '''float: 'SpiralAngleAtOuterDiameterPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpiralAngleAtOuterDiameterPinion

    @property
    def hw(self) -> 'float':
        '''float: 'HW' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HW

    @property
    def driving_flank_normal_pressure_angle(self) -> 'float':
        '''float: 'DrivingFlankNormalPressureAngle' is the original name of this property.'''

        return self.wrapped.DrivingFlankNormalPressureAngle

    @driving_flank_normal_pressure_angle.setter
    def driving_flank_normal_pressure_angle(self, value: 'float'):
        self.wrapped.DrivingFlankNormalPressureAngle = float(value) if value else 0.0

    @property
    def coasting_flank_normal_pressure_angle(self) -> 'float':
        '''float: 'CoastingFlankNormalPressureAngle' is the original name of this property.'''

        return self.wrapped.CoastingFlankNormalPressureAngle

    @coasting_flank_normal_pressure_angle.setter
    def coasting_flank_normal_pressure_angle(self, value: 'float'):
        self.wrapped.CoastingFlankNormalPressureAngle = float(value) if value else 0.0

    @property
    def cutter_blade_tip_width(self) -> 'float':
        '''float: 'CutterBladeTipWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterBladeTipWidth

    @property
    def inner_pitch_cone_diameter(self) -> 'float':
        '''float: 'InnerPitchConeDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerPitchConeDiameter

    @property
    def inner_pitch_surface_diameter(self) -> 'float':
        '''float: 'InnerPitchSurfaceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InnerPitchSurfaceDiameter

    @property
    def respective_cone_distance(self) -> 'float':
        '''float: 'RespectiveConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RespectiveConeDistance

    @property
    def minimum_addendum_modification_factor(self) -> 'float':
        '''float: 'MinimumAddendumModificationFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumAddendumModificationFactor

    @property
    def settling_angle(self) -> 'float':
        '''float: 'SettlingAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SettlingAngle

    @property
    def pinion_helix_angle_at_base_circle_of_virtual_gear(self) -> 'float':
        '''float: 'PinionHelixAngleAtBaseCircleOfVirtualGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionHelixAngleAtBaseCircleOfVirtualGear

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
    def wheel_helix_angle_at_base_circle_of_virtual_gear(self) -> 'float':
        '''float: 'WheelHelixAngleAtBaseCircleOfVirtualGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelHelixAngleAtBaseCircleOfVirtualGear

    @property
    def virtual_number_of_wheel_teeth_at_mean_cone_distance(self) -> 'float':
        '''float: 'VirtualNumberOfWheelTeethAtMeanConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VirtualNumberOfWheelTeethAtMeanConeDistance

    @property
    def profile_contact_ratio_in_transverse_section_driving_flank(self) -> 'float':
        '''float: 'ProfileContactRatioInTransverseSectionDrivingFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileContactRatioInTransverseSectionDrivingFlank

    @property
    def profile_contact_ratio_in_transverse_section_coasting_flank(self) -> 'float':
        '''float: 'ProfileContactRatioInTransverseSectionCoastingFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileContactRatioInTransverseSectionCoastingFlank

    @property
    def partial_face_contact_angle_a(self) -> 'float':
        '''float: 'PartialFaceContactAngleA' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PartialFaceContactAngleA

    @property
    def partial_face_contact_angle_b(self) -> 'float':
        '''float: 'PartialFaceContactAngleB' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PartialFaceContactAngleB

    @property
    def face_contact_angle(self) -> 'float':
        '''float: 'FaceContactAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceContactAngle

    @property
    def gears(self) -> 'List[_934.KlingelnbergCycloPalloidHypoidGearDesign]':
        '''List[KlingelnbergCycloPalloidHypoidGearDesign]: 'Gears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Gears, constructor.new(_934.KlingelnbergCycloPalloidHypoidGearDesign))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_gears(self) -> 'List[_934.KlingelnbergCycloPalloidHypoidGearDesign]':
        '''List[KlingelnbergCycloPalloidHypoidGearDesign]: 'KlingelnbergCycloPalloidHypoidGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidGears, constructor.new(_934.KlingelnbergCycloPalloidHypoidGearDesign))
        return value

    @property
    def klingelnberg_conical_meshes(self) -> 'List[_935.KlingelnbergCycloPalloidHypoidGearMeshDesign]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshDesign]: 'KlingelnbergConicalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergConicalMeshes, constructor.new(_935.KlingelnbergCycloPalloidHypoidGearMeshDesign))
        return value

    @property
    def klingelnberg_cyclo_palloid_hypoid_meshes(self) -> 'List[_935.KlingelnbergCycloPalloidHypoidGearMeshDesign]':
        '''List[KlingelnbergCycloPalloidHypoidGearMeshDesign]: 'KlingelnbergCycloPalloidHypoidMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergCycloPalloidHypoidMeshes, constructor.new(_935.KlingelnbergCycloPalloidHypoidGearMeshDesign))
        return value
