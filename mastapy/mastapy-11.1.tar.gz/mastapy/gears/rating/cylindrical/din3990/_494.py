'''_494.py

DIN3990MeshSingleFlankRating
'''


from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.gears.rating.cylindrical import _442, _443
from mastapy.gears.rating.cylindrical.iso6336 import _473
from mastapy._internal.python_net import python_net_import

_DIN3990_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Cylindrical.DIN3990', 'DIN3990MeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('DIN3990MeshSingleFlankRating',)


class DIN3990MeshSingleFlankRating(_473.ISO63361996MeshSingleFlankRating):
    '''DIN3990MeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _DIN3990_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DIN3990MeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def rating_standard_name(self) -> 'str':
        '''str: 'RatingStandardName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RatingStandardName

    @property
    def scuffing_rating_method_flash_temperature_method(self) -> '_442.ScuffingFlashTemperatureRatingMethod':
        '''ScuffingFlashTemperatureRatingMethod: 'ScuffingRatingMethodFlashTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ScuffingRatingMethodFlashTemperatureMethod)
        return constructor.new(_442.ScuffingFlashTemperatureRatingMethod)(value) if value is not None else None

    @property
    def scuffing_rating_method_integral_temperature_method(self) -> '_443.ScuffingIntegralTemperatureRatingMethod':
        '''ScuffingIntegralTemperatureRatingMethod: 'ScuffingRatingMethodIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ScuffingRatingMethodIntegralTemperatureMethod)
        return constructor.new(_443.ScuffingIntegralTemperatureRatingMethod)(value) if value is not None else None

    @property
    def resonance_ratio_in_the_main_resonance_range(self) -> 'float':
        '''float: 'ResonanceRatioInTheMainResonanceRange' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ResonanceRatioInTheMainResonanceRange

    @property
    def basic_mean_flash_temperature(self) -> 'float':
        '''float: 'BasicMeanFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.BasicMeanFlashTemperature

    @property
    def transverse_unit_load(self) -> 'float':
        '''float: 'TransverseUnitLoad' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TransverseUnitLoad

    @property
    def mean_coefficient_of_friction_integral_temperature_method(self) -> 'float':
        '''float: 'MeanCoefficientOfFrictionIntegralTemperatureMethod' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanCoefficientOfFrictionIntegralTemperatureMethod

    @property
    def flash_factor_integral(self) -> 'float':
        '''float: 'FlashFactorIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FlashFactorIntegral

    @property
    def tip_relief_factor_integral(self) -> 'float':
        '''float: 'TipReliefFactorIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TipReliefFactorIntegral

    @property
    def estimated_bulk_temperature_integral(self) -> 'float':
        '''float: 'EstimatedBulkTemperatureIntegral' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EstimatedBulkTemperatureIntegral

    @property
    def estimated_bulk_temperature_flash(self) -> 'float':
        '''float: 'EstimatedBulkTemperatureFlash' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EstimatedBulkTemperatureFlash

    @property
    def parameter_on_line_of_action_at_maximum_flash_temperature(self) -> 'float':
        '''float: 'ParameterOnLineOfActionAtMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ParameterOnLineOfActionAtMaximumFlashTemperature

    @property
    def thermo_elastic_factor_at_maximum_flash_temperature(self) -> 'float':
        '''float: 'ThermoElasticFactorAtMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ThermoElasticFactorAtMaximumFlashTemperature

    @property
    def geometry_factor_at_maximum_flash_temperature(self) -> 'float':
        '''float: 'GeometryFactorAtMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactorAtMaximumFlashTemperature

    @property
    def load_distribution_factor_at_maximum_flash_temperature(self) -> 'float':
        '''float: 'LoadDistributionFactorAtMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactorAtMaximumFlashTemperature

    @property
    def mean_local_coefficient_of_friction_at_maximum_flash_temperature(self) -> 'float':
        '''float: 'MeanLocalCoefficientOfFrictionAtMaximumFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeanLocalCoefficientOfFrictionAtMaximumFlashTemperature

    @property
    def integral_scuffing_temperature(self) -> 'float':
        '''float: 'IntegralScuffingTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntegralScuffingTemperature
