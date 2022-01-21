'''_1230.py

SAESplineJointRating
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.splines.ratings import _1232
from mastapy._internal.python_net import python_net_import

_SAE_SPLINE_JOINT_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.Ratings', 'SAESplineJointRating')


__docformat__ = 'restructuredtext en'
__all__ = ('SAESplineJointRating',)


class SAESplineJointRating(_1232.SplineJointRating):
    '''SAESplineJointRating

    This is a mastapy class.
    '''

    TYPE = _SAE_SPLINE_JOINT_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SAESplineJointRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def fatigue_life_factor(self) -> 'float':
        '''float: 'FatigueLifeFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueLifeFactor

    @property
    def wear_life_factor(self) -> 'float':
        '''float: 'WearLifeFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WearLifeFactor

    @property
    def misalignment_factor(self) -> 'float':
        '''float: 'MisalignmentFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MisalignmentFactor

    @property
    def over_load_factor(self) -> 'float':
        '''float: 'OverLoadFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.OverLoadFactor

    @property
    def allowable_compressive_stress(self) -> 'float':
        '''float: 'AllowableCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableCompressiveStress

    @property
    def active_contact_height(self) -> 'float':
        '''float: 'ActiveContactHeight' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ActiveContactHeight

    @property
    def calculated_compressive_stress(self) -> 'float':
        '''float: 'CalculatedCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedCompressiveStress

    @property
    def allowable_shear_stress(self) -> 'float':
        '''float: 'AllowableShearStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableShearStress

    @property
    def calculated_maximum_tooth_shearing_stress(self) -> 'float':
        '''float: 'CalculatedMaximumToothShearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CalculatedMaximumToothShearingStress

    @property
    def maximum_allowable_tensile_stress(self) -> 'float':
        '''float: 'MaximumAllowableTensileStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MaximumAllowableTensileStress

    @property
    def internal_hoop_stress(self) -> 'float':
        '''float: 'InternalHoopStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InternalHoopStress

    @property
    def safety_factor_for_equivalent_root_stress(self) -> 'float':
        '''float: 'SafetyFactorForEquivalentRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForEquivalentRootStress

    @property
    def fatigue_damage_for_equivalent_root_stress(self) -> 'float':
        '''float: 'FatigueDamageForEquivalentRootStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueDamageForEquivalentRootStress

    @property
    def safety_factor_for_compressive_stress(self) -> 'float':
        '''float: 'SafetyFactorForCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForCompressiveStress

    @property
    def fatigue_damage_for_compressive_stress(self) -> 'float':
        '''float: 'FatigueDamageForCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueDamageForCompressiveStress

    @property
    def safety_factor_for_tooth_shearing_stress(self) -> 'float':
        '''float: 'SafetyFactorForToothShearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForToothShearingStress

    @property
    def fatigue_damage_for_tooth_shearing_stress(self) -> 'float':
        '''float: 'FatigueDamageForToothShearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FatigueDamageForToothShearingStress
