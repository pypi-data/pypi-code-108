'''_969.py

CylindricalGearDesign
'''


from typing import List

from PIL.Image import Image

from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy._internal.implicit import overridable
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy.geometry.two_d import _278
from mastapy.gears import _299, _280
from mastapy._internal.python_net import python_net_import
from mastapy.gears.gear_designs.cylindrical import (
    _1010, _1009, _1011, _1012,
    _1032, _984, _995, _975,
    _958, _1034, _978, _1001,
    _1039, _1021, _1000, _967,
    _976
)
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1052
from mastapy.gears.manufacturing.cylindrical import _572
from mastapy.gears.materials import (
    _554, _543, _545, _547,
    _551, _557, _561, _563
)
from mastapy.gears.gear_designs.cylindrical.accuracy_and_tolerances import (
    _1088, _1092, _1083, _1085,
    _1081, _1082, _1084, _1086,
    _1089, _1090, _1091, _1087
)
from mastapy.gears.gear_designs.agma_gleason_conical import _1139
from mastapy.gears.gear_designs import _904

_DATABASE_WITH_SELECTED_ITEM = python_net_import('SMT.MastaAPI.UtilityGUI.Databases', 'DatabaseWithSelectedItem')
_CYLINDRICAL_GEAR_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearDesign',)


class CylindricalGearDesign(_904.GearDesign):
    '''CylindricalGearDesign

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def web_status(self) -> 'str':
        '''str: 'WebStatus' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WebStatus

    @property
    def effective_web_thickness(self) -> 'float':
        '''float: 'EffectiveWebThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveWebThickness

    @property
    def web_centre_offset(self) -> 'float':
        '''float: 'WebCentreOffset' is the original name of this property.'''

        return self.wrapped.WebCentreOffset

    @web_centre_offset.setter
    def web_centre_offset(self, value: 'float'):
        self.wrapped.WebCentreOffset = float(value) if value else 0.0

    @property
    def specified_web_thickness(self) -> 'float':
        '''float: 'SpecifiedWebThickness' is the original name of this property.'''

        return self.wrapped.SpecifiedWebThickness

    @specified_web_thickness.setter
    def specified_web_thickness(self, value: 'float'):
        self.wrapped.SpecifiedWebThickness = float(value) if value else 0.0

    @property
    def rim_thickness(self) -> 'float':
        '''float: 'RimThickness' is the original name of this property.'''

        return self.wrapped.RimThickness

    @rim_thickness.setter
    def rim_thickness(self, value: 'float'):
        self.wrapped.RimThickness = float(value) if value else 0.0

    @property
    def rim_thickness_normal_module_ratio(self) -> 'float':
        '''float: 'RimThicknessNormalModuleRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RimThicknessNormalModuleRatio

    @property
    def minimum_required_rim_thickness_by_standard_iso8140042005(self) -> 'float':
        '''float: 'MinimumRequiredRimThicknessByStandardISO8140042005' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumRequiredRimThicknessByStandardISO8140042005

    @property
    def rim_diameter(self) -> 'float':
        '''float: 'RimDiameter' is the original name of this property.'''

        return self.wrapped.RimDiameter

    @rim_diameter.setter
    def rim_diameter(self, value: 'float'):
        self.wrapped.RimDiameter = float(value) if value else 0.0

    @property
    def absolute_rim_diameter(self) -> 'float':
        '''float: 'AbsoluteRimDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AbsoluteRimDiameter

    @property
    def lead(self) -> 'float':
        '''float: 'Lead' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Lead

    @property
    def tip_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'TipDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.TipDiameter) if self.wrapped.TipDiameter is not None else None

    @tip_diameter.setter
    def tip_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.TipDiameter = value

    @property
    def signed_tip_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'SignedTipDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.SignedTipDiameter) if self.wrapped.SignedTipDiameter is not None else None

    @signed_tip_diameter.setter
    def signed_tip_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.SignedTipDiameter = value

    @property
    def tip_alteration_coefficient(self) -> 'float':
        '''float: 'TipAlterationCoefficient' is the original name of this property.'''

        return self.wrapped.TipAlterationCoefficient

    @tip_alteration_coefficient.setter
    def tip_alteration_coefficient(self, value: 'float'):
        self.wrapped.TipAlterationCoefficient = float(value) if value else 0.0

    @property
    def root_diameter(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RootDiameter' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RootDiameter) if self.wrapped.RootDiameter is not None else None

    @root_diameter.setter
    def root_diameter(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RootDiameter = value

    @property
    def signed_root_diameter(self) -> 'float':
        '''float: 'SignedRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SignedRootDiameter

    @property
    def tip_thickness(self) -> 'float':
        '''float: 'TipThickness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipThickness

    @property
    def normal_thickness_at_tip_form_diameter_at_upper_backlash_allowance(self) -> 'float':
        '''float: 'NormalThicknessAtTipFormDiameterAtUpperBacklashAllowance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThicknessAtTipFormDiameterAtUpperBacklashAllowance

    @property
    def normal_thickness_at_tip_form_diameter_at_lower_backlash_allowance(self) -> 'float':
        '''float: 'NormalThicknessAtTipFormDiameterAtLowerBacklashAllowance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThicknessAtTipFormDiameterAtLowerBacklashAllowance

    @property
    def normal_thickness_at_tip_form_diameter_at_lower_backlash_allowance_over_normal_module(self) -> 'float':
        '''float: 'NormalThicknessAtTipFormDiameterAtLowerBacklashAllowanceOverNormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalThicknessAtTipFormDiameterAtLowerBacklashAllowanceOverNormalModule

    @property
    def tip_thickness_at_upper_backlash_allowance(self) -> 'float':
        '''float: 'TipThicknessAtUpperBacklashAllowance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipThicknessAtUpperBacklashAllowance

    @property
    def tip_thickness_at_lower_backlash_allowance(self) -> 'float':
        '''float: 'TipThicknessAtLowerBacklashAllowance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipThicknessAtLowerBacklashAllowance

    @property
    def tip_thickness_at_lower_backlash_allowance_over_normal_module(self) -> 'float':
        '''float: 'TipThicknessAtLowerBacklashAllowanceOverNormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipThicknessAtLowerBacklashAllowanceOverNormalModule

    @property
    def internal_external(self) -> '_278.InternalExternalType':
        '''InternalExternalType: 'InternalExternal' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.InternalExternal)
        return constructor.new(_278.InternalExternalType)(value) if value is not None else None

    @internal_external.setter
    def internal_external(self, value: '_278.InternalExternalType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.InternalExternal = value

    @property
    def material_name(self) -> 'str':
        '''str: 'MaterialName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaterialName

    @property
    def helix_angle_at_tip_form_diameter(self) -> 'float':
        '''float: 'HelixAngleAtTipFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngleAtTipFormDiameter

    @property
    def addendum(self) -> 'float':
        '''float: 'Addendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Addendum

    @property
    def dedendum(self) -> 'float':
        '''float: 'Dedendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Dedendum

    @property
    def thermal_contact_coefficient(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'ThermalContactCoefficient' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.ThermalContactCoefficient) if self.wrapped.ThermalContactCoefficient is not None else None

    @thermal_contact_coefficient.setter
    def thermal_contact_coefficient(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.ThermalContactCoefficient = value

    @property
    def normal_space_width_at_root_form_diameter(self) -> 'float':
        '''float: 'NormalSpaceWidthAtRootFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalSpaceWidthAtRootFormDiameter

    @property
    def mass(self) -> 'float':
        '''float: 'Mass' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Mass

    @property
    def reference_diameter(self) -> 'float':
        '''float: 'ReferenceDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ReferenceDiameter

    @property
    def is_asymmetric(self) -> 'bool':
        '''bool: 'IsAsymmetric' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsAsymmetric

    @property
    def gear_hand(self) -> 'str':
        '''str: 'GearHand' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GearHand

    @property
    def hand(self) -> '_299.Hand':
        '''Hand: 'Hand' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.Hand)
        return constructor.new(_299.Hand)(value) if value is not None else None

    @hand.setter
    def hand(self, value: '_299.Hand'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.Hand = value

    @property
    def face_width(self) -> 'float':
        '''float: 'FaceWidth' is the original name of this property.'''

        return self.wrapped.FaceWidth

    @face_width.setter
    def face_width(self, value: 'float'):
        self.wrapped.FaceWidth = float(value) if value else 0.0

    @property
    def helix_angle(self) -> 'float':
        '''float: 'HelixAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HelixAngle

    @property
    def number_of_teeth_unsigned(self) -> 'float':
        '''float: 'NumberOfTeethUnsigned' is the original name of this property.'''

        return self.wrapped.NumberOfTeethUnsigned

    @number_of_teeth_unsigned.setter
    def number_of_teeth_unsigned(self, value: 'float'):
        self.wrapped.NumberOfTeethUnsigned = float(value) if value else 0.0

    @property
    def normal_module(self) -> 'float':
        '''float: 'NormalModule' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalModule

    @property
    def number_of_teeth_maintaining_ratio_calculating_normal_module(self) -> 'int':
        '''int: 'NumberOfTeethMaintainingRatioCalculatingNormalModule' is the original name of this property.'''

        return self.wrapped.NumberOfTeethMaintainingRatioCalculatingNormalModule

    @number_of_teeth_maintaining_ratio_calculating_normal_module.setter
    def number_of_teeth_maintaining_ratio_calculating_normal_module(self, value: 'int'):
        self.wrapped.NumberOfTeethMaintainingRatioCalculatingNormalModule = int(value) if value else 0

    @property
    def number_of_teeth_with_normal_module_adjustment(self) -> 'int':
        '''int: 'NumberOfTeethWithNormalModuleAdjustment' is the original name of this property.'''

        return self.wrapped.NumberOfTeethWithNormalModuleAdjustment

    @number_of_teeth_with_normal_module_adjustment.setter
    def number_of_teeth_with_normal_module_adjustment(self, value: 'int'):
        self.wrapped.NumberOfTeethWithNormalModuleAdjustment = int(value) if value else 0

    @property
    def mean_normal_thickness_at_half_depth(self) -> 'float':
        '''float: 'MeanNormalThicknessAtHalfDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanNormalThicknessAtHalfDepth

    @property
    def normal_tooth_thickness_at_the_base_circle(self) -> 'float':
        '''float: 'NormalToothThicknessAtTheBaseCircle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalToothThicknessAtTheBaseCircle

    @property
    def transverse_tooth_thickness_at_the_base_circle(self) -> 'float':
        '''float: 'TransverseToothThicknessAtTheBaseCircle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseToothThicknessAtTheBaseCircle

    @property
    def use_default_design_material(self) -> 'bool':
        '''bool: 'UseDefaultDesignMaterial' is the original name of this property.'''

        return self.wrapped.UseDefaultDesignMaterial

    @use_default_design_material.setter
    def use_default_design_material(self, value: 'bool'):
        self.wrapped.UseDefaultDesignMaterial = bool(value) if value else False

    @property
    def material_iso(self) -> 'str':
        '''str: 'MaterialISO' is the original name of this property.'''

        return self.wrapped.MaterialISO.SelectedItemName

    @material_iso.setter
    def material_iso(self, value: 'str'):
        self.wrapped.MaterialISO.SetSelectedItem(str(value) if value else '')

    @property
    def material_agma(self) -> 'str':
        '''str: 'MaterialAGMA' is the original name of this property.'''

        return self.wrapped.MaterialAGMA.SelectedItemName

    @material_agma.setter
    def material_agma(self, value: 'str'):
        self.wrapped.MaterialAGMA.SetSelectedItem(str(value) if value else '')

    @property
    def tooth_depth(self) -> 'float':
        '''float: 'ToothDepth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothDepth

    @property
    def root_heat_transfer_coefficient(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RootHeatTransferCoefficient' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RootHeatTransferCoefficient) if self.wrapped.RootHeatTransferCoefficient is not None else None

    @root_heat_transfer_coefficient.setter
    def root_heat_transfer_coefficient(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RootHeatTransferCoefficient = value

    @property
    def flank_heat_transfer_coefficient(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FlankHeatTransferCoefficient' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FlankHeatTransferCoefficient) if self.wrapped.FlankHeatTransferCoefficient is not None else None

    @flank_heat_transfer_coefficient.setter
    def flank_heat_transfer_coefficient(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FlankHeatTransferCoefficient = value

    @property
    def permissible_linear_wear(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'PermissibleLinearWear' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.PermissibleLinearWear) if self.wrapped.PermissibleLinearWear is not None else None

    @permissible_linear_wear.setter
    def permissible_linear_wear(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.PermissibleLinearWear = value

    @property
    def initial_clocking_angle(self) -> 'float':
        '''float: 'InitialClockingAngle' is the original name of this property.'''

        return self.wrapped.InitialClockingAngle

    @initial_clocking_angle.setter
    def initial_clocking_angle(self, value: 'float'):
        self.wrapped.InitialClockingAngle = float(value) if value else 0.0

    @property
    def mean_generating_circle_diameter(self) -> 'float':
        '''float: 'MeanGeneratingCircleDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanGeneratingCircleDiameter

    @property
    def factor_for_the_increase_of_the_yield_point_under_compression(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'FactorForTheIncreaseOfTheYieldPointUnderCompression' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.FactorForTheIncreaseOfTheYieldPointUnderCompression) if self.wrapped.FactorForTheIncreaseOfTheYieldPointUnderCompression is not None else None

    @factor_for_the_increase_of_the_yield_point_under_compression.setter
    def factor_for_the_increase_of_the_yield_point_under_compression(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.FactorForTheIncreaseOfTheYieldPointUnderCompression = value

    @property
    def rotation_angle(self) -> 'float':
        '''float: 'RotationAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RotationAngle

    @property
    def gear_tooth_drawing(self) -> 'Image':
        '''Image: 'GearToothDrawing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.GearToothDrawing)
        return value

    @property
    def gear_drawing(self) -> 'Image':
        '''Image: 'GearDrawing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_smt_bitmap(self.wrapped.GearDrawing)
        return value

    @property
    def radii_of_curvature_at_tip(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadiiOfCurvatureAtTip' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadiiOfCurvatureAtTip) if self.wrapped.RadiiOfCurvatureAtTip is not None else None

    @radii_of_curvature_at_tip.setter
    def radii_of_curvature_at_tip(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RadiiOfCurvatureAtTip = value

    @property
    def radii_of_curvature_at_tip_right_flank(self) -> 'overridable.Overridable_float':
        '''overridable.Overridable_float: 'RadiiOfCurvatureAtTipRightFlank' is the original name of this property.'''

        return constructor.new(overridable.Overridable_float)(self.wrapped.RadiiOfCurvatureAtTipRightFlank) if self.wrapped.RadiiOfCurvatureAtTipRightFlank is not None else None

    @radii_of_curvature_at_tip_right_flank.setter
    def radii_of_curvature_at_tip_right_flank(self, value: 'overridable.Overridable_float.implicit_type()'):
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](enclosed_type(value) if value is not None else 0.0, is_overridden)
        self.wrapped.RadiiOfCurvatureAtTipRightFlank = value

    @property
    def maximum_tip_diameter(self) -> 'float':
        '''float: 'MaximumTipDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumTipDiameter

    @property
    def minimum_root_diameter(self) -> 'float':
        '''float: 'MinimumRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinimumRootDiameter

    @property
    def number_of_teeth_with_centre_distance_adjustment(self) -> 'int':
        '''int: 'NumberOfTeethWithCentreDistanceAdjustment' is the original name of this property.'''

        return self.wrapped.NumberOfTeethWithCentreDistanceAdjustment

    @number_of_teeth_with_centre_distance_adjustment.setter
    def number_of_teeth_with_centre_distance_adjustment(self, value: 'int'):
        self.wrapped.NumberOfTeethWithCentreDistanceAdjustment = int(value) if value else 0

    @property
    def iso6336_geometry(self) -> '_1010.ISO6336GeometryBase':
        '''ISO6336GeometryBase: 'ISO6336Geometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1010.ISO6336GeometryBase.TYPE not in self.wrapped.ISO6336Geometry.__class__.__mro__:
            raise CastException('Failed to cast iso6336_geometry to ISO6336GeometryBase. Expected: {}.'.format(self.wrapped.ISO6336Geometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ISO6336Geometry.__class__)(self.wrapped.ISO6336Geometry) if self.wrapped.ISO6336Geometry is not None else None

    @property
    def iso6336_geometry_of_type_iso6336_geometry(self) -> '_1009.ISO6336Geometry':
        '''ISO6336Geometry: 'ISO6336Geometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1009.ISO6336Geometry.TYPE not in self.wrapped.ISO6336Geometry.__class__.__mro__:
            raise CastException('Failed to cast iso6336_geometry to ISO6336Geometry. Expected: {}.'.format(self.wrapped.ISO6336Geometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ISO6336Geometry.__class__)(self.wrapped.ISO6336Geometry) if self.wrapped.ISO6336Geometry is not None else None

    @property
    def iso6336_geometry_of_type_iso6336_geometry_for_shaped_gears(self) -> '_1011.ISO6336GeometryForShapedGears':
        '''ISO6336GeometryForShapedGears: 'ISO6336Geometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1011.ISO6336GeometryForShapedGears.TYPE not in self.wrapped.ISO6336Geometry.__class__.__mro__:
            raise CastException('Failed to cast iso6336_geometry to ISO6336GeometryForShapedGears. Expected: {}.'.format(self.wrapped.ISO6336Geometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ISO6336Geometry.__class__)(self.wrapped.ISO6336Geometry) if self.wrapped.ISO6336Geometry is not None else None

    @property
    def iso6336_geometry_of_type_iso6336_geometry_manufactured(self) -> '_1012.ISO6336GeometryManufactured':
        '''ISO6336GeometryManufactured: 'ISO6336Geometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1012.ISO6336GeometryManufactured.TYPE not in self.wrapped.ISO6336Geometry.__class__.__mro__:
            raise CastException('Failed to cast iso6336_geometry to ISO6336GeometryManufactured. Expected: {}.'.format(self.wrapped.ISO6336Geometry.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ISO6336Geometry.__class__)(self.wrapped.ISO6336Geometry) if self.wrapped.ISO6336Geometry is not None else None

    @property
    def surface_roughness(self) -> '_1032.SurfaceRoughness':
        '''SurfaceRoughness: 'SurfaceRoughness' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1032.SurfaceRoughness)(self.wrapped.SurfaceRoughness) if self.wrapped.SurfaceRoughness is not None else None

    @property
    def cylindrical_gear_set(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'CylindricalGearSet' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.wrapped.CylindricalGearSet.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_set to CylindricalGearSetDesign. Expected: {}.'.format(self.wrapped.CylindricalGearSet.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearSet.__class__)(self.wrapped.CylindricalGearSet) if self.wrapped.CylindricalGearSet is not None else None

    @property
    def left_flank(self) -> '_975.CylindricalGearFlankDesign':
        '''CylindricalGearFlankDesign: 'LeftFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_975.CylindricalGearFlankDesign)(self.wrapped.LeftFlank) if self.wrapped.LeftFlank is not None else None

    @property
    def right_flank(self) -> '_975.CylindricalGearFlankDesign':
        '''CylindricalGearFlankDesign: 'RightFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_975.CylindricalGearFlankDesign)(self.wrapped.RightFlank) if self.wrapped.RightFlank is not None else None

    @property
    def cylindrical_gear_micro_geometry(self) -> '_1052.CylindricalGearMicroGeometry':
        '''CylindricalGearMicroGeometry: 'CylindricalGearMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1052.CylindricalGearMicroGeometry)(self.wrapped.CylindricalGearMicroGeometry) if self.wrapped.CylindricalGearMicroGeometry is not None else None

    @property
    def cylindrical_gear_manufacturing_configuration(self) -> '_572.CylindricalGearManufacturingConfig':
        '''CylindricalGearManufacturingConfig: 'CylindricalGearManufacturingConfiguration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_572.CylindricalGearManufacturingConfig)(self.wrapped.CylindricalGearManufacturingConfiguration) if self.wrapped.CylindricalGearManufacturingConfiguration is not None else None

    @property
    def material(self) -> '_554.GearMaterial':
        '''GearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _554.GearMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to GearMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def material_of_type_agma_cylindrical_gear_material(self) -> '_543.AGMACylindricalGearMaterial':
        '''AGMACylindricalGearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _543.AGMACylindricalGearMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to AGMACylindricalGearMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def material_of_type_bevel_gear_iso_material(self) -> '_545.BevelGearISOMaterial':
        '''BevelGearISOMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _545.BevelGearISOMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to BevelGearISOMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def material_of_type_bevel_gear_material(self) -> '_547.BevelGearMaterial':
        '''BevelGearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _547.BevelGearMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to BevelGearMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def material_of_type_cylindrical_gear_material(self) -> '_551.CylindricalGearMaterial':
        '''CylindricalGearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _551.CylindricalGearMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to CylindricalGearMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def material_of_type_iso_cylindrical_gear_material(self) -> '_557.ISOCylindricalGearMaterial':
        '''ISOCylindricalGearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _557.ISOCylindricalGearMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to ISOCylindricalGearMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def material_of_type_klingelnberg_cyclo_palloid_conical_gear_material(self) -> '_561.KlingelnbergCycloPalloidConicalGearMaterial':
        '''KlingelnbergCycloPalloidConicalGearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _561.KlingelnbergCycloPalloidConicalGearMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to KlingelnbergCycloPalloidConicalGearMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def material_of_type_plastic_cylindrical_gear_material(self) -> '_563.PlasticCylindricalGearMaterial':
        '''PlasticCylindricalGearMaterial: 'Material' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _563.PlasticCylindricalGearMaterial.TYPE not in self.wrapped.Material.__class__.__mro__:
            raise CastException('Failed to cast material to PlasticCylindricalGearMaterial. Expected: {}.'.format(self.wrapped.Material.__class__.__qualname__))

        return constructor.new_override(self.wrapped.Material.__class__)(self.wrapped.Material) if self.wrapped.Material is not None else None

    @property
    def system_of_gear_fits(self) -> '_1088.DIN3967SystemOfGearFits':
        '''DIN3967SystemOfGearFits: 'SystemOfGearFits' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1088.DIN3967SystemOfGearFits)(self.wrapped.SystemOfGearFits) if self.wrapped.SystemOfGearFits is not None else None

    @property
    def iso_accuracy_grade(self) -> '_1092.ISO1328AccuracyGrades':
        '''ISO1328AccuracyGrades: 'ISOAccuracyGrade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1092.ISO1328AccuracyGrades)(self.wrapped.ISOAccuracyGrade) if self.wrapped.ISOAccuracyGrade is not None else None

    @property
    def agma_accuracy_grade(self) -> '_1083.AGMA20151AccuracyGrades':
        '''AGMA20151AccuracyGrades: 'AGMAAccuracyGrade' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1083.AGMA20151AccuracyGrades)(self.wrapped.AGMAAccuracyGrade) if self.wrapped.AGMAAccuracyGrade is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances(self) -> '_1085.CylindricalAccuracyGrader':
        '''CylindricalAccuracyGrader: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1085.CylindricalAccuracyGrader.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to CylindricalAccuracyGrader. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances_of_type_agma2000_accuracy_grader(self) -> '_1081.AGMA2000AccuracyGrader':
        '''AGMA2000AccuracyGrader: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1081.AGMA2000AccuracyGrader.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to AGMA2000AccuracyGrader. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances_of_type_agma20151_accuracy_grader(self) -> '_1082.AGMA20151AccuracyGrader':
        '''AGMA20151AccuracyGrader: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1082.AGMA20151AccuracyGrader.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to AGMA20151AccuracyGrader. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances_of_type_agmaiso13282013_accuracy_grader(self) -> '_1084.AGMAISO13282013AccuracyGrader':
        '''AGMAISO13282013AccuracyGrader: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1084.AGMAISO13282013AccuracyGrader.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to AGMAISO13282013AccuracyGrader. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances_of_type_cylindrical_accuracy_grader_with_profile_form_and_slope(self) -> '_1086.CylindricalAccuracyGraderWithProfileFormAndSlope':
        '''CylindricalAccuracyGraderWithProfileFormAndSlope: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1086.CylindricalAccuracyGraderWithProfileFormAndSlope.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to CylindricalAccuracyGraderWithProfileFormAndSlope. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances_of_type_iso13282013_accuracy_grader(self) -> '_1089.ISO13282013AccuracyGrader':
        '''ISO13282013AccuracyGrader: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1089.ISO13282013AccuracyGrader.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to ISO13282013AccuracyGrader. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances_of_type_iso1328_accuracy_grader(self) -> '_1090.ISO1328AccuracyGrader':
        '''ISO1328AccuracyGrader: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1090.ISO1328AccuracyGrader.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to ISO1328AccuracyGrader. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grade_allowances_and_tolerances_of_type_iso1328_accuracy_grader_common(self) -> '_1091.ISO1328AccuracyGraderCommon':
        '''ISO1328AccuracyGraderCommon: 'AccuracyGradeAllowancesAndTolerances' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1091.ISO1328AccuracyGraderCommon.TYPE not in self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grade_allowances_and_tolerances to ISO1328AccuracyGraderCommon. Expected: {}.'.format(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradeAllowancesAndTolerances.__class__)(self.wrapped.AccuracyGradeAllowancesAndTolerances) if self.wrapped.AccuracyGradeAllowancesAndTolerances is not None else None

    @property
    def accuracy_grades_specified_accuracy(self) -> '_280.AccuracyGrades':
        '''AccuracyGrades: 'AccuracyGradesSpecifiedAccuracy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _280.AccuracyGrades.TYPE not in self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades_specified_accuracy to AccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__)(self.wrapped.AccuracyGradesSpecifiedAccuracy) if self.wrapped.AccuracyGradesSpecifiedAccuracy is not None else None

    @property
    def accuracy_grades_specified_accuracy_of_type_agma20151_accuracy_grades(self) -> '_1083.AGMA20151AccuracyGrades':
        '''AGMA20151AccuracyGrades: 'AccuracyGradesSpecifiedAccuracy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1083.AGMA20151AccuracyGrades.TYPE not in self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades_specified_accuracy to AGMA20151AccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__)(self.wrapped.AccuracyGradesSpecifiedAccuracy) if self.wrapped.AccuracyGradesSpecifiedAccuracy is not None else None

    @property
    def accuracy_grades_specified_accuracy_of_type_cylindrical_accuracy_grades(self) -> '_1087.CylindricalAccuracyGrades':
        '''CylindricalAccuracyGrades: 'AccuracyGradesSpecifiedAccuracy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1087.CylindricalAccuracyGrades.TYPE not in self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades_specified_accuracy to CylindricalAccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__)(self.wrapped.AccuracyGradesSpecifiedAccuracy) if self.wrapped.AccuracyGradesSpecifiedAccuracy is not None else None

    @property
    def accuracy_grades_specified_accuracy_of_type_iso1328_accuracy_grades(self) -> '_1092.ISO1328AccuracyGrades':
        '''ISO1328AccuracyGrades: 'AccuracyGradesSpecifiedAccuracy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1092.ISO1328AccuracyGrades.TYPE not in self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades_specified_accuracy to ISO1328AccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__)(self.wrapped.AccuracyGradesSpecifiedAccuracy) if self.wrapped.AccuracyGradesSpecifiedAccuracy is not None else None

    @property
    def accuracy_grades_specified_accuracy_of_type_agma_gleason_conical_accuracy_grades(self) -> '_1139.AGMAGleasonConicalAccuracyGrades':
        '''AGMAGleasonConicalAccuracyGrades: 'AccuracyGradesSpecifiedAccuracy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1139.AGMAGleasonConicalAccuracyGrades.TYPE not in self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__mro__:
            raise CastException('Failed to cast accuracy_grades_specified_accuracy to AGMAGleasonConicalAccuracyGrades. Expected: {}.'.format(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__.__qualname__))

        return constructor.new_override(self.wrapped.AccuracyGradesSpecifiedAccuracy.__class__)(self.wrapped.AccuracyGradesSpecifiedAccuracy) if self.wrapped.AccuracyGradesSpecifiedAccuracy is not None else None

    @property
    def case_hardening_properties(self) -> '_958.CaseHardeningProperties':
        '''CaseHardeningProperties: 'CaseHardeningProperties' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_958.CaseHardeningProperties)(self.wrapped.CaseHardeningProperties) if self.wrapped.CaseHardeningProperties is not None else None

    @property
    def tiff_analysis_settings(self) -> '_1034.TiffAnalysisSettings':
        '''TiffAnalysisSettings: 'TIFFAnalysisSettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1034.TiffAnalysisSettings)(self.wrapped.TIFFAnalysisSettings) if self.wrapped.TIFFAnalysisSettings is not None else None

    @property
    def micro_geometry_settings(self) -> '_978.CylindricalGearMicroGeometrySettings':
        '''CylindricalGearMicroGeometrySettings: 'MicroGeometrySettings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_978.CylindricalGearMicroGeometrySettings)(self.wrapped.MicroGeometrySettings) if self.wrapped.MicroGeometrySettings is not None else None

    @property
    def finished_tooth_thickness_specification(self) -> '_1001.FinishToothThicknessDesignSpecification':
        '''FinishToothThicknessDesignSpecification: 'FinishedToothThicknessSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1001.FinishToothThicknessDesignSpecification)(self.wrapped.FinishedToothThicknessSpecification) if self.wrapped.FinishedToothThicknessSpecification is not None else None

    @property
    def rough_tooth_thickness_specification(self) -> '_1039.ToothThicknessSpecification':
        '''ToothThicknessSpecification: 'RoughToothThicknessSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1039.ToothThicknessSpecification.TYPE not in self.wrapped.RoughToothThicknessSpecification.__class__.__mro__:
            raise CastException('Failed to cast rough_tooth_thickness_specification to ToothThicknessSpecification. Expected: {}.'.format(self.wrapped.RoughToothThicknessSpecification.__class__.__qualname__))

        return constructor.new_override(self.wrapped.RoughToothThicknessSpecification.__class__)(self.wrapped.RoughToothThicknessSpecification) if self.wrapped.RoughToothThicknessSpecification is not None else None

    @property
    def finish_stock_specification(self) -> '_1000.FinishStockSpecification':
        '''FinishStockSpecification: 'FinishStockSpecification' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1000.FinishStockSpecification)(self.wrapped.FinishStockSpecification) if self.wrapped.FinishStockSpecification is not None else None

    @property
    def cylindrical_gear_cutting_options(self) -> '_967.CylindricalGearCuttingOptions':
        '''CylindricalGearCuttingOptions: 'CylindricalGearCuttingOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_967.CylindricalGearCuttingOptions)(self.wrapped.CylindricalGearCuttingOptions) if self.wrapped.CylindricalGearCuttingOptions is not None else None

    @property
    def cylindrical_meshes(self) -> 'List[_976.CylindricalGearMeshDesign]':
        '''List[CylindricalGearMeshDesign]: 'CylindricalMeshes' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshes, constructor.new(_976.CylindricalGearMeshDesign))
        return value

    @property
    def flanks(self) -> 'List[_975.CylindricalGearFlankDesign]':
        '''List[CylindricalGearFlankDesign]: 'Flanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Flanks, constructor.new(_975.CylindricalGearFlankDesign))
        return value

    @property
    def both_flanks(self) -> '_975.CylindricalGearFlankDesign':
        '''CylindricalGearFlankDesign: 'BothFlanks' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_975.CylindricalGearFlankDesign)(self.wrapped.BothFlanks) if self.wrapped.BothFlanks is not None else None

    @property
    def micro_geometries(self) -> 'List[_1052.CylindricalGearMicroGeometry]':
        '''List[CylindricalGearMicroGeometry]: 'MicroGeometries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MicroGeometries, constructor.new(_1052.CylindricalGearMicroGeometry))
        return value

    @property
    def manufacturing_configurations(self) -> 'List[_572.CylindricalGearManufacturingConfig]':
        '''List[CylindricalGearManufacturingConfig]: 'ManufacturingConfigurations' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ManufacturingConfigurations, constructor.new(_572.CylindricalGearManufacturingConfig))
        return value
