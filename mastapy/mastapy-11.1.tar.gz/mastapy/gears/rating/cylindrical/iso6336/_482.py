'''_482.py

ISO6336MeanStressInfluenceFactor
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears import _289
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ISO6336_MEAN_STRESS_INFLUENCE_FACTOR = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336', 'ISO6336MeanStressInfluenceFactor')


__docformat__ = 'restructuredtext en'
__all__ = ('ISO6336MeanStressInfluenceFactor',)


class ISO6336MeanStressInfluenceFactor(_0.APIBase):
    '''ISO6336MeanStressInfluenceFactor

    This is a mastapy class.
    '''

    TYPE = _ISO6336_MEAN_STRESS_INFLUENCE_FACTOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ISO6336MeanStressInfluenceFactor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_per_unit_face_width_of_the_lower_loaded_flank(self) -> 'float':
        '''float: 'LoadPerUnitFaceWidthOfTheLowerLoadedFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadPerUnitFaceWidthOfTheLowerLoadedFlank

    @property
    def load_per_unit_face_width_of_the_higher_loaded_flank(self) -> 'float':
        '''float: 'LoadPerUnitFaceWidthOfTheHigherLoadedFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadPerUnitFaceWidthOfTheHigherLoadedFlank

    @property
    def higher_loaded_flank(self) -> '_289.CylindricalFlanks':
        '''CylindricalFlanks: 'HigherLoadedFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.HigherLoadedFlank)
        return constructor.new(_289.CylindricalFlanks)(value) if value is not None else None

    @property
    def stress_ratio(self) -> 'float':
        '''float: 'StressRatio' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressRatio

    @property
    def mean_stress_ratio_for_static_stress(self) -> 'float':
        '''float: 'MeanStressRatioForStaticStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanStressRatioForStaticStress

    @property
    def mean_stress_ratio_for_reference_stress(self) -> 'float':
        '''float: 'MeanStressRatioForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanStressRatioForReferenceStress

    @property
    def stress_influence_factor_for_reference_stress(self) -> 'float':
        '''float: 'StressInfluenceFactorForReferenceStress' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressInfluenceFactorForReferenceStress

    @property
    def stress_influence_factor(self) -> 'float':
        '''float: 'StressInfluenceFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.StressInfluenceFactor
