'''_1227.py

GBT17855SplineHalfRating
'''


from mastapy._internal import constructor
from mastapy.detailed_rigid_connectors.splines.ratings import _1231
from mastapy._internal.python_net import python_net_import

_GBT17855_SPLINE_HALF_RATING = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.Ratings', 'GBT17855SplineHalfRating')


__docformat__ = 'restructuredtext en'
__all__ = ('GBT17855SplineHalfRating',)


class GBT17855SplineHalfRating(_1231.SplineHalfRating):
    '''GBT17855SplineHalfRating

    This is a mastapy class.
    '''

    TYPE = _GBT17855_SPLINE_HALF_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GBT17855SplineHalfRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def allowable_stress(self) -> 'float':
        '''float: 'AllowableStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableStress

    @property
    def permissible_stress(self) -> 'float':
        '''float: 'PermissibleStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleStress

    @property
    def allowable_compressive_stress(self) -> 'float':
        '''float: 'AllowableCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableCompressiveStress

    @property
    def permissible_compressive_stress(self) -> 'float':
        '''float: 'PermissibleCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleCompressiveStress

    @property
    def allowable_tooth_shearing_stress(self) -> 'float':
        '''float: 'AllowableToothShearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableToothShearingStress

    @property
    def permissible_tooth_shearing_stress(self) -> 'float':
        '''float: 'PermissibleToothShearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleToothShearingStress

    @property
    def allowable_root_bending_stress(self) -> 'float':
        '''float: 'AllowableRootBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableRootBendingStress

    @property
    def permissible_root_bending_stress(self) -> 'float':
        '''float: 'PermissibleRootBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleRootBendingStress

    @property
    def allowable_wearing_stress(self) -> 'float':
        '''float: 'AllowableWearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AllowableWearingStress

    @property
    def permissible_wearing_stress(self) -> 'float':
        '''float: 'PermissibleWearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PermissibleWearingStress

    @property
    def safety_factor_for_equivalent_stress(self) -> 'float':
        '''float: 'SafetyFactorForEquivalentStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForEquivalentStress

    @property
    def safety_factor_for_compressive_stress(self) -> 'float':
        '''float: 'SafetyFactorForCompressiveStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForCompressiveStress

    @property
    def safety_factor_for_tooth_shearing_stress(self) -> 'float':
        '''float: 'SafetyFactorForToothShearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForToothShearingStress

    @property
    def safety_factor_for_root_bending_stress(self) -> 'float':
        '''float: 'SafetyFactorForRootBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForRootBendingStress

    @property
    def safety_factor_for_wearing_stress(self) -> 'float':
        '''float: 'SafetyFactorForWearingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SafetyFactorForWearingStress
