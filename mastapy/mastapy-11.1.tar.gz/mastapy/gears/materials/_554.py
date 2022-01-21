'''_554.py

GearMaterial
'''


from mastapy._internal import constructor
from mastapy.materials import _249, _239
from mastapy._internal.python_net import python_net_import

_GEAR_MATERIAL = python_net_import('SMT.MastaAPI.Gears.Materials', 'GearMaterial')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMaterial',)


class GearMaterial(_239.Material):
    '''GearMaterial

    This is a mastapy class.
    '''

    TYPE = _GEAR_MATERIAL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMaterial.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def apply_derating_factors_to_contact_custom_sn_curve(self) -> 'bool':
        '''bool: 'ApplyDeratingFactorsToContactCustomSNCurve' is the original name of this property.'''

        return self.wrapped.ApplyDeratingFactorsToContactCustomSNCurve

    @apply_derating_factors_to_contact_custom_sn_curve.setter
    def apply_derating_factors_to_contact_custom_sn_curve(self, value: 'bool'):
        self.wrapped.ApplyDeratingFactorsToContactCustomSNCurve = bool(value) if value else False

    @property
    def apply_derating_factors_to_bending_custom_sn_curve(self) -> 'bool':
        '''bool: 'ApplyDeratingFactorsToBendingCustomSNCurve' is the original name of this property.'''

        return self.wrapped.ApplyDeratingFactorsToBendingCustomSNCurve

    @apply_derating_factors_to_bending_custom_sn_curve.setter
    def apply_derating_factors_to_bending_custom_sn_curve(self, value: 'bool'):
        self.wrapped.ApplyDeratingFactorsToBendingCustomSNCurve = bool(value) if value else False

    @property
    def n0_contact(self) -> 'float':
        '''float: 'N0Contact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.N0Contact

    @property
    def n0_bending(self) -> 'float':
        '''float: 'N0Bending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.N0Bending

    @property
    def nc_contact(self) -> 'float':
        '''float: 'NCContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NCContact

    @property
    def nc_bending(self) -> 'float':
        '''float: 'NCBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NCBending

    @property
    def number_of_known_points_for_user_sn_curve_bending_stress(self) -> 'int':
        '''int: 'NumberOfKnownPointsForUserSNCurveBendingStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfKnownPointsForUserSNCurveBendingStress

    @property
    def number_of_known_points_for_user_sn_curve_for_contact_stress(self) -> 'int':
        '''int: 'NumberOfKnownPointsForUserSNCurveForContactStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.NumberOfKnownPointsForUserSNCurveForContactStress

    @property
    def core_hardness(self) -> 'float':
        '''float: 'CoreHardness' is the original name of this property.'''

        return self.wrapped.CoreHardness

    @core_hardness.setter
    def core_hardness(self, value: 'float'):
        self.wrapped.CoreHardness = float(value) if value else 0.0

    @property
    def sn_curve_contact(self) -> '_249.SNCurve':
        '''SNCurve: 'SNCurveContact' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_249.SNCurve)(self.wrapped.SNCurveContact) if self.wrapped.SNCurveContact is not None else None

    @property
    def sn_curve_bending(self) -> '_249.SNCurve':
        '''SNCurve: 'SNCurveBending' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_249.SNCurve)(self.wrapped.SNCurveBending) if self.wrapped.SNCurveBending is not None else None
