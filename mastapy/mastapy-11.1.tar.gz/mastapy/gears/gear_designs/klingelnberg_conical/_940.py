'''_940.py

KlingelnbergConicalGearSetDesign
'''


from typing import List

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.gear_designs.conical import _1115, _1103
from mastapy._internal.implicit import list_with_selected_item
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.gears.gear_designs.klingelnberg_conical import _939
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CONICAL_GEAR_SET_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.KlingelnbergConical', 'KlingelnbergConicalGearSetDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergConicalGearSetDesign',)


class KlingelnbergConicalGearSetDesign(_1103.ConicalGearSetDesign):
    '''KlingelnbergConicalGearSetDesign

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CONICAL_GEAR_SET_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergConicalGearSetDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def wheel_pitch_diameter(self) -> 'float':
        '''float: 'WheelPitchDiameter' is the original name of this property.'''

        return self.wrapped.WheelPitchDiameter

    @wheel_pitch_diameter.setter
    def wheel_pitch_diameter(self, value: 'float'):
        self.wrapped.WheelPitchDiameter = float(value) if value else 0.0

    @property
    def stub_factor(self) -> 'float':
        '''float: 'StubFactor' is the original name of this property.'''

        return self.wrapped.StubFactor

    @stub_factor.setter
    def stub_factor(self, value: 'float'):
        self.wrapped.StubFactor = float(value) if value else 0.0

    @property
    def addendum_modification_factor(self) -> 'float':
        '''float: 'AddendumModificationFactor' is the original name of this property.'''

        return self.wrapped.AddendumModificationFactor

    @addendum_modification_factor.setter
    def addendum_modification_factor(self, value: 'float'):
        self.wrapped.AddendumModificationFactor = float(value) if value else 0.0

    @property
    def tooth_thickness_modification_factor(self) -> 'float':
        '''float: 'ToothThicknessModificationFactor' is the original name of this property.'''

        return self.wrapped.ToothThicknessModificationFactor

    @tooth_thickness_modification_factor.setter
    def tooth_thickness_modification_factor(self, value: 'float'):
        self.wrapped.ToothThicknessModificationFactor = float(value) if value else 0.0

    @property
    def angle_modification(self) -> 'float':
        '''float: 'AngleModification' is the original name of this property.'''

        return self.wrapped.AngleModification

    @angle_modification.setter
    def angle_modification(self, value: 'float'):
        self.wrapped.AngleModification = float(value) if value else 0.0

    @property
    def shaft_angle(self) -> 'float':
        '''float: 'ShaftAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ShaftAngle

    @property
    def pinion_number_of_teeth(self) -> 'int':
        '''int: 'PinionNumberOfTeeth' is the original name of this property.'''

        return self.wrapped.PinionNumberOfTeeth

    @pinion_number_of_teeth.setter
    def pinion_number_of_teeth(self, value: 'int'):
        self.wrapped.PinionNumberOfTeeth = int(value) if value else 0

    @property
    def wheel_number_of_teeth(self) -> 'int':
        '''int: 'WheelNumberOfTeeth' is the original name of this property.'''

        return self.wrapped.WheelNumberOfTeeth

    @wheel_number_of_teeth.setter
    def wheel_number_of_teeth(self, value: 'int'):
        self.wrapped.WheelNumberOfTeeth = int(value) if value else 0

    @property
    def wheel_face_width(self) -> 'float':
        '''float: 'WheelFaceWidth' is the original name of this property.'''

        return self.wrapped.WheelFaceWidth

    @wheel_face_width.setter
    def wheel_face_width(self, value: 'float'):
        self.wrapped.WheelFaceWidth = float(value) if value else 0.0

    @property
    def module(self) -> 'float':
        '''float: 'Module' is the original name of this property.'''

        return self.wrapped.Module

    @module.setter
    def module(self, value: 'float'):
        self.wrapped.Module = float(value) if value else 0.0

    @property
    def wheel_mean_spiral_angle(self) -> 'float':
        '''float: 'WheelMeanSpiralAngle' is the original name of this property.'''

        return self.wrapped.WheelMeanSpiralAngle

    @wheel_mean_spiral_angle.setter
    def wheel_mean_spiral_angle(self, value: 'float'):
        self.wrapped.WheelMeanSpiralAngle = float(value) if value else 0.0

    @property
    def lead_angle_on_cutter_head(self) -> 'float':
        '''float: 'LeadAngleOnCutterHead' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeadAngleOnCutterHead

    @property
    def machine_distance(self) -> 'float':
        '''float: 'MachineDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MachineDistance

    @property
    def base_circle_radius(self) -> 'float':
        '''float: 'BaseCircleRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseCircleRadius

    @property
    def auxiliary_angle_at_re(self) -> 'float':
        '''float: 'AuxiliaryAngleAtRe' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryAngleAtRe

    @property
    def auxiliary_angle_at_ri(self) -> 'float':
        '''float: 'AuxiliaryAngleAtRi' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryAngleAtRi

    @property
    def spiral_angle_at_wheel_outer_diameter(self) -> 'float':
        '''float: 'SpiralAngleAtWheelOuterDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpiralAngleAtWheelOuterDiameter

    @property
    def spiral_angle_at_wheel_inner_diameter(self) -> 'float':
        '''float: 'SpiralAngleAtWheelInnerDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SpiralAngleAtWheelInnerDiameter

    @property
    def normal_module_at_outer_diameter(self) -> 'float':
        '''float: 'NormalModuleAtOuterDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalModuleAtOuterDiameter

    @property
    def normal_module_at_inner_diameter(self) -> 'float':
        '''float: 'NormalModuleAtInnerDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalModuleAtInnerDiameter

    @property
    def cone_distance_maximum_tooth_gap(self) -> 'float':
        '''float: 'ConeDistanceMaximumToothGap' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ConeDistanceMaximumToothGap

    @property
    def addendum_of_tool(self) -> 'float':
        '''float: 'AddendumOfTool' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AddendumOfTool

    @property
    def cutter_blade_tip_width_causes_cut_off(self) -> 'bool':
        '''bool: 'CutterBladeTipWidthCausesCutOff' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterBladeTipWidthCausesCutOff

    @property
    def cutter_blade_tip_width_causes_ridge(self) -> 'bool':
        '''bool: 'CutterBladeTipWidthCausesRidge' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterBladeTipWidthCausesRidge

    @property
    def use_minimum_addendum_modification_factor(self) -> 'bool':
        '''bool: 'UseMinimumAddendumModificationFactor' is the original name of this property.'''

        return self.wrapped.UseMinimumAddendumModificationFactor

    @use_minimum_addendum_modification_factor.setter
    def use_minimum_addendum_modification_factor(self, value: 'bool'):
        self.wrapped.UseMinimumAddendumModificationFactor = bool(value) if value else False

    @property
    def whole_depth(self) -> 'float':
        '''float: 'WholeDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WholeDepth

    @property
    def pinion_generating_cone_angle(self) -> 'float':
        '''float: 'PinionGeneratingConeAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionGeneratingConeAngle

    @property
    def wheel_generating_cone_angle(self) -> 'float':
        '''float: 'WheelGeneratingConeAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelGeneratingConeAngle

    @property
    def auxiliary_value_for_angle_modification(self) -> 'float':
        '''float: 'AuxiliaryValueForAngleModification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxiliaryValueForAngleModification

    @property
    def tip_circle_diameter_of_virtual_gear(self) -> 'float':
        '''float: 'TipCircleDiameterOfVirtualGear' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipCircleDiameterOfVirtualGear

    @property
    def normal_pressure_angle_at_tooth_tip(self) -> 'float':
        '''float: 'NormalPressureAngleAtToothTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngleAtToothTip

    @property
    def tooth_thickness_half_angle_on_pitch_cone(self) -> 'float':
        '''float: 'ToothThicknessHalfAngleOnPitchCone' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothThicknessHalfAngleOnPitchCone

    @property
    def tooth_thickness_half_angle_on_tooth_tip(self) -> 'float':
        '''float: 'ToothThicknessHalfAngleOnToothTip' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothThicknessHalfAngleOnToothTip

    @property
    def tooth_tip_thickness_at_inner(self) -> 'float':
        '''float: 'ToothTipThicknessAtInner' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothTipThicknessAtInner

    @property
    def tooth_tip_chamfering_factor(self) -> 'float':
        '''float: 'ToothTipChamferingFactor' is the original name of this property.'''

        return self.wrapped.ToothTipChamferingFactor

    @tooth_tip_chamfering_factor.setter
    def tooth_tip_chamfering_factor(self, value: 'float'):
        self.wrapped.ToothTipChamferingFactor = float(value) if value else 0.0

    @property
    def use_required_tooth_tip_chamfering_factor(self) -> 'bool':
        '''bool: 'UseRequiredToothTipChamferingFactor' is the original name of this property.'''

        return self.wrapped.UseRequiredToothTipChamferingFactor

    @use_required_tooth_tip_chamfering_factor.setter
    def use_required_tooth_tip_chamfering_factor(self, value: 'bool'):
        self.wrapped.UseRequiredToothTipChamferingFactor = bool(value) if value else False

    @property
    def tooth_tip_thickness_at_mean_cone_distance(self) -> 'float':
        '''float: 'ToothTipThicknessAtMeanConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothTipThicknessAtMeanConeDistance

    @property
    def tip_cone_angle_from_tooth_tip_chamfering_reduction(self) -> 'float':
        '''float: 'TipConeAngleFromToothTipChamferingReduction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipConeAngleFromToothTipChamferingReduction

    @property
    def auxilliary_angle_at_re_2(self) -> 'float':
        '''float: 'AuxilliaryAngleAtRe2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxilliaryAngleAtRe2

    @property
    def auxilliary_angle_at_ri_2(self) -> 'float':
        '''float: 'AuxilliaryAngleAtRi2' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AuxilliaryAngleAtRi2

    @property
    def face_contact_ratio(self) -> 'float':
        '''float: 'FaceContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceContactRatio

    @property
    def gear_finish(self) -> '_1115.KlingelnbergFinishingMethods':
        '''KlingelnbergFinishingMethods: 'GearFinish' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.GearFinish)
        return constructor.new(_1115.KlingelnbergFinishingMethods)(value) if value is not None else None

    @gear_finish.setter
    def gear_finish(self, value: '_1115.KlingelnbergFinishingMethods'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.GearFinish = value

    @property
    def effective_face_width(self) -> 'float':
        '''float: 'EffectiveFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveFaceWidth

    @property
    def gear_cutting_machine_options(self) -> 'list_with_selected_item.ListWithSelectedItem_str':
        '''list_with_selected_item.ListWithSelectedItem_str: 'GearCuttingMachineOptions' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_str)(self.wrapped.GearCuttingMachineOptions) if self.wrapped.GearCuttingMachineOptions is not None else None

    @gear_cutting_machine_options.setter
    def gear_cutting_machine_options(self, value: 'list_with_selected_item.ListWithSelectedItem_str.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_str.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_str.implicit_type()
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else '')
        self.wrapped.GearCuttingMachineOptions = value

    @property
    def cutter_radius(self) -> 'float':
        '''float: 'CutterRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterRadius

    @property
    def cutter_module(self) -> 'float':
        '''float: 'CutterModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CutterModule

    @property
    def number_of_starts(self) -> 'float':
        '''float: 'NumberOfStarts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfStarts

    @property
    def conical_meshes(self) -> 'List[_939.KlingelnbergConicalGearMeshDesign]':
        '''List[KlingelnbergConicalGearMeshDesign]: 'ConicalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConicalMeshes, constructor.new(_939.KlingelnbergConicalGearMeshDesign))
        return value

    @property
    def klingelnberg_conical_meshes(self) -> 'List[_939.KlingelnbergConicalGearMeshDesign]':
        '''List[KlingelnbergConicalGearMeshDesign]: 'KlingelnbergConicalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KlingelnbergConicalMeshes, constructor.new(_939.KlingelnbergConicalGearMeshDesign))
        return value
