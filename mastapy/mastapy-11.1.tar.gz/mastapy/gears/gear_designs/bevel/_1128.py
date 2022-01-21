'''_1128.py

BevelGearMeshDesign
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.agma_gleason_conical import _1141
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_MESH_DESIGN = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Bevel', 'BevelGearMeshDesign')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearMeshDesign',)


class BevelGearMeshDesign(_1141.AGMAGleasonConicalGearMeshDesign):
    '''BevelGearMeshDesign

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_MESH_DESIGN

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearMeshDesign.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def wheel_pitch_angle(self) -> 'float':
        '''float: 'WheelPitchAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelPitchAngle

    @property
    def wheel_face_angle(self) -> 'float':
        '''float: 'WheelFaceAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelFaceAngle

    @property
    def wheel_root_angle(self) -> 'float':
        '''float: 'WheelRootAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelRootAngle

    @property
    def pinion_pitch_angle(self) -> 'float':
        '''float: 'PinionPitchAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionPitchAngle

    @property
    def pinion_face_angle(self) -> 'float':
        '''float: 'PinionFaceAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionFaceAngle

    @property
    def pinion_root_angle(self) -> 'float':
        '''float: 'PinionRootAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionRootAngle

    @property
    def contact_wheel_mean_cone_distance(self) -> 'float':
        '''float: 'ContactWheelMeanConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactWheelMeanConeDistance

    @property
    def contact_wheel_outer_cone_distance(self) -> 'float':
        '''float: 'ContactWheelOuterConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactWheelOuterConeDistance

    @property
    def contact_wheel_inner_cone_distance(self) -> 'float':
        '''float: 'ContactWheelInnerConeDistance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactWheelInnerConeDistance

    @property
    def contact_effective_face_width(self) -> 'float':
        '''float: 'ContactEffectiveFaceWidth' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactEffectiveFaceWidth

    @property
    def ideal_wheel_pitch_angle(self) -> 'float':
        '''float: 'IdealWheelPitchAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IdealWheelPitchAngle

    @property
    def ideal_pinion_pitch_angle(self) -> 'float':
        '''float: 'IdealPinionPitchAngle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IdealPinionPitchAngle

    @property
    def pinion_pitch_angle_modification(self) -> 'float':
        '''float: 'PinionPitchAngleModification' is the original name of this property.'''

        return self.wrapped.PinionPitchAngleModification

    @pinion_pitch_angle_modification.setter
    def pinion_pitch_angle_modification(self, value: 'float'):
        self.wrapped.PinionPitchAngleModification = float(value) if value else 0.0

    @property
    def wheel_pitch_angle_modification(self) -> 'float':
        '''float: 'WheelPitchAngleModification' is the original name of this property.'''

        return self.wrapped.WheelPitchAngleModification

    @wheel_pitch_angle_modification.setter
    def wheel_pitch_angle_modification(self, value: 'float'):
        self.wrapped.WheelPitchAngleModification = float(value) if value else 0.0

    @property
    def wheel_spiral_angle_at_contact_outer(self) -> 'float':
        '''float: 'WheelSpiralAngleAtContactOuter' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelSpiralAngleAtContactOuter

    @property
    def pinion_inner_dedendum(self) -> 'float':
        '''float: 'PinionInnerDedendum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionInnerDedendum

    @property
    def is_topland_balanced(self) -> 'bool':
        '''bool: 'IsToplandBalanced' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IsToplandBalanced

    @property
    def pinion_thickness_modification_coefficient_backlash_included(self) -> 'float':
        '''float: 'PinionThicknessModificationCoefficientBacklashIncluded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionThicknessModificationCoefficientBacklashIncluded

    @property
    def wheel_thickness_modification_coefficient_backlash_included(self) -> 'float':
        '''float: 'WheelThicknessModificationCoefficientBacklashIncluded' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelThicknessModificationCoefficientBacklashIncluded

    @property
    def strength_balance_agma_drive(self) -> 'float':
        '''float: 'StrengthBalanceAGMADrive' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthBalanceAGMADrive

    @property
    def strength_balance_agma_coast(self) -> 'float':
        '''float: 'StrengthBalanceAGMACoast' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthBalanceAGMACoast

    @property
    def strength_balance_gleason_drive(self) -> 'float':
        '''float: 'StrengthBalanceGleasonDrive' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthBalanceGleasonDrive

    @property
    def strength_balance_gleason_coast(self) -> 'float':
        '''float: 'StrengthBalanceGleasonCoast' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthBalanceGleasonCoast

    @property
    def geometry_factor_g(self) -> 'float':
        '''float: 'GeometryFactorG' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorG

    @property
    def load_sharing_ratio_scoring(self) -> 'float':
        '''float: 'LoadSharingRatioScoring' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatioScoring

    @property
    def transverse_contact_ratio(self) -> 'float':
        '''float: 'TransverseContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseContactRatio

    @property
    def face_contact_ratio(self) -> 'float':
        '''float: 'FaceContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceContactRatio

    @property
    def modified_contact_ratio(self) -> 'float':
        '''float: 'ModifiedContactRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ModifiedContactRatio

    @property
    def inertia_factor_bending(self) -> 'float':
        '''float: 'InertiaFactorBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaFactorBending

    @property
    def strength_balance_obtained_drive(self) -> 'float':
        '''float: 'StrengthBalanceObtainedDrive' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthBalanceObtainedDrive

    @property
    def strength_balance_obtained_coast(self) -> 'float':
        '''float: 'StrengthBalanceObtainedCoast' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StrengthBalanceObtainedCoast

    @property
    def geometry_factor_i(self) -> 'float':
        '''float: 'GeometryFactorI' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorI

    @property
    def pitting_resistance_geometry_factor(self) -> 'float':
        '''float: 'PittingResistanceGeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PittingResistanceGeometryFactor

    @property
    def inertia_factor_contact(self) -> 'float':
        '''float: 'InertiaFactorContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InertiaFactorContact

    @property
    def length_of_line_of_contact(self) -> 'float':
        '''float: 'LengthOfLineOfContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LengthOfLineOfContact

    @property
    def load_sharing_ratio_contact(self) -> 'float':
        '''float: 'LoadSharingRatioContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadSharingRatioContact

    @property
    def pinion_passed_undercut_check(self) -> 'bool':
        '''bool: 'PinionPassedUndercutCheck' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionPassedUndercutCheck

    @property
    def pinion_inner_dedendum_limit(self) -> 'float':
        '''float: 'PinionInnerDedendumLimit' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionInnerDedendumLimit
