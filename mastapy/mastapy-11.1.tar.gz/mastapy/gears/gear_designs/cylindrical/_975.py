'''_975.py

CylindricalGearFlankDesign
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.cylindrical import _981
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_FLANK_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical', 'CylindricalGearFlankDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearFlankDesign',)


class CylindricalGearFlankDesign(_0.APIBase):
    '''CylindricalGearFlankDesign

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_FLANK_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearFlankDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def transverse_chamfer_angle(self) -> 'float':
        '''float: 'TransverseChamferAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseChamferAngle

    @property
    def chamfer_angle_in_normal_plane(self) -> 'float':
        '''float: 'ChamferAngleInNormalPlane' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ChamferAngleInNormalPlane

    @property
    def base_thickness_half_angle(self) -> 'float':
        '''float: 'BaseThicknessHalfAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseThicknessHalfAngle

    @property
    def tooth_thickness_half_angle_at_reference_circle(self) -> 'float':
        '''float: 'ToothThicknessHalfAngleAtReferenceCircle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ToothThicknessHalfAngleAtReferenceCircle

    @property
    def transverse_pressure_angle(self) -> 'float':
        '''float: 'TransversePressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransversePressureAngle

    @property
    def normal_pressure_angle(self) -> 'float':
        '''float: 'NormalPressureAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalPressureAngle

    @property
    def normal_base_pitch(self) -> 'float':
        '''float: 'NormalBasePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NormalBasePitch

    @property
    def transverse_base_pitch(self) -> 'float':
        '''float: 'TransverseBasePitch' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseBasePitch

    @property
    def base_diameter(self) -> 'float':
        '''float: 'BaseDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseDiameter

    @property
    def absolute_base_diameter(self) -> 'float':
        '''float: 'AbsoluteBaseDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AbsoluteBaseDiameter

    @property
    def tip_form_diameter(self) -> 'float':
        '''float: 'TipFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipFormDiameter

    @property
    def absolute_tip_form_diameter(self) -> 'float':
        '''float: 'AbsoluteTipFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AbsoluteTipFormDiameter

    @property
    def root_form_diameter(self) -> 'float':
        '''float: 'RootFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFormDiameter

    @property
    def absolute_form_diameter(self) -> 'float':
        '''float: 'AbsoluteFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AbsoluteFormDiameter

    @property
    def form_radius(self) -> 'float':
        '''float: 'FormRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormRadius

    @property
    def root_form_roll_distance(self) -> 'float':
        '''float: 'RootFormRollDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFormRollDistance

    @property
    def root_form_roll_angle(self) -> 'float':
        '''float: 'RootFormRollAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RootFormRollAngle

    @property
    def base_to_form_diameter_clearance_as_normal_module_ratio(self) -> 'float':
        '''float: 'BaseToFormDiameterClearanceAsNormalModuleRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseToFormDiameterClearanceAsNormalModuleRatio

    @property
    def base_to_form_diameter_clearance(self) -> 'float':
        '''float: 'BaseToFormDiameterClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BaseToFormDiameterClearance

    @property
    def mean_normal_thickness_at_tip_form_diameter(self) -> 'float':
        '''float: 'MeanNormalThicknessAtTipFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanNormalThicknessAtTipFormDiameter

    @property
    def mean_normal_thickness_at_root_form_diameter(self) -> 'float':
        '''float: 'MeanNormalThicknessAtRootFormDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanNormalThicknessAtRootFormDiameter

    @property
    def has_chamfer(self) -> 'bool':
        '''bool: 'HasChamfer' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.HasChamfer

    @property
    def flank_name(self) -> 'str':
        '''str: 'FlankName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlankName

    @property
    def effective_tip_radius(self) -> 'float':
        '''float: 'EffectiveTipRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EffectiveTipRadius

    @property
    def tip_form_roll_distance(self) -> 'float':
        '''float: 'TipFormRollDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipFormRollDistance

    @property
    def tip_form_roll_angle(self) -> 'float':
        '''float: 'TipFormRollAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipFormRollAngle

    @property
    def signed_root_diameter(self) -> 'float':
        '''float: 'SignedRootDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SignedRootDiameter

    @property
    def lowest_sap_diameter(self) -> 'float':
        '''float: 'LowestSAPDiameter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LowestSAPDiameter

    @property
    def form_to_sap_diameter_absolute_clearance_as_normal_module_ratio(self) -> 'float':
        '''float: 'FormToSAPDiameterAbsoluteClearanceAsNormalModuleRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FormToSAPDiameterAbsoluteClearanceAsNormalModuleRatio

    @property
    def absolute_form_to_sap_diameter_clearance(self) -> 'float':
        '''float: 'AbsoluteFormToSAPDiameterClearance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AbsoluteFormToSAPDiameterClearance

    @property
    def tip_form(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'TipForm' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.TipForm) if self.wrapped.TipForm is not None else None

    @property
    def root_form(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'RootForm' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.RootForm) if self.wrapped.RootForm is not None else None

    @property
    def tip_diameter_reporting(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'TipDiameterReporting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.TipDiameterReporting) if self.wrapped.TipDiameterReporting is not None else None

    @property
    def root_diameter_reporting(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'RootDiameterReporting' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.RootDiameterReporting) if self.wrapped.RootDiameterReporting is not None else None

    @property
    def lowest_point_of_fewest_tooth_contacts(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'LowestPointOfFewestToothContacts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.LowestPointOfFewestToothContacts) if self.wrapped.LowestPointOfFewestToothContacts is not None else None

    @property
    def highest_point_of_fewest_tooth_contacts(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'HighestPointOfFewestToothContacts' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.HighestPointOfFewestToothContacts) if self.wrapped.HighestPointOfFewestToothContacts is not None else None

    @property
    def lowest_start_of_active_profile(self) -> '_981.CylindricalGearProfileMeasurement':
        '''CylindricalGearProfileMeasurement: 'LowestStartOfActiveProfile' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_981.CylindricalGearProfileMeasurement)(self.wrapped.LowestStartOfActiveProfile) if self.wrapped.LowestStartOfActiveProfile is not None else None
