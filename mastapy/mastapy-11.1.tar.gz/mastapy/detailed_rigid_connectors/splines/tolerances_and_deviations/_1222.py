'''_1222.py

SAESplineTolerances
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SAE_SPLINE_TOLERANCES = python_net_import('SMT.MastaAPI.DetailedRigidConnectors.Splines.TolerancesAndDeviations', 'SAESplineTolerances')


__docformat__ = 'restructuredtext en'
__all__ = ('SAESplineTolerances',)


class SAESplineTolerances(_0.APIBase):
    '''SAESplineTolerances

    This is a mastapy class.
    '''

    TYPE = _SAE_SPLINE_TOLERANCES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SAESplineTolerances.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def variation_tolerance(self) -> 'float':
        '''float: 'VariationTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.VariationTolerance

    @property
    def lead_variation(self) -> 'float':
        '''float: 'LeadVariation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeadVariation

    @property
    def profile_variation_f_fp(self) -> 'float':
        '''float: 'ProfileVariationF_fp' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileVariationF_fp

    @property
    def profile_variation_f_fm(self) -> 'float':
        '''float: 'ProfileVariationF_fm' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ProfileVariationF_fm

    @property
    def total_index_variation(self) -> 'float':
        '''float: 'TotalIndexVariation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalIndexVariation

    @property
    def machining_variation(self) -> 'float':
        '''float: 'MachiningVariation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MachiningVariation

    @property
    def major_diameter_tolerance(self) -> 'float':
        '''float: 'MajorDiameterTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MajorDiameterTolerance

    @property
    def minor_diameter_tolerance(self) -> 'float':
        '''float: 'MinorDiameterTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MinorDiameterTolerance

    @property
    def internal_major_diameter_tolerance(self) -> 'float':
        '''float: 'InternalMajorDiameterTolerance' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.InternalMajorDiameterTolerance

    @property
    def multiplier_f(self) -> 'float':
        '''float: 'MultiplierF' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MultiplierF
