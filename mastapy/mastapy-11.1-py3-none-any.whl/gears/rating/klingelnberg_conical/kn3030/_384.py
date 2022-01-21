'''_384.py

KlingelnbergCycloPalloidHypoidMeshSingleFlankRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.rating.klingelnberg_conical.kn3030 import _383, _380
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_MESH_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.KlingelnbergConical.KN3030', 'KlingelnbergCycloPalloidHypoidMeshSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidMeshSingleFlankRating',)


class KlingelnbergCycloPalloidHypoidMeshSingleFlankRating(_380.KlingelnbergConicalMeshSingleFlankRating):
    '''KlingelnbergCycloPalloidHypoidMeshSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_MESH_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidMeshSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def dynamic_factor(self) -> 'float':
        '''float: 'DynamicFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.DynamicFactor

    @property
    def load_distribution_factor_transverse(self) -> 'float':
        '''float: 'LoadDistributionFactorTransverse' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadDistributionFactorTransverse

    @property
    def relating_factor_for_the_thermal_flash_temperature(self) -> 'float':
        '''float: 'RelatingFactorForTheThermalFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RelatingFactorForTheThermalFlashTemperature

    @property
    def tangential_speed_sum(self) -> 'float':
        '''float: 'TangentialSpeedSum' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialSpeedSum

    @property
    def friction_coefficient(self) -> 'float':
        '''float: 'FrictionCoefficient' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FrictionCoefficient

    @property
    def curvature_radius(self) -> 'float':
        '''float: 'CurvatureRadius' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.CurvatureRadius

    @property
    def geometry_factor(self) -> 'float':
        '''float: 'GeometryFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.GeometryFactor

    @property
    def sliding_factor(self) -> 'float':
        '''float: 'SlidingFactor' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.SlidingFactor

    @property
    def total_speed_in_depthwise_direction(self) -> 'float':
        '''float: 'TotalSpeedInDepthwiseDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalSpeedInDepthwiseDirection

    @property
    def total_speed_in_lengthwise_direction(self) -> 'float':
        '''float: 'TotalSpeedInLengthwiseDirection' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalSpeedInLengthwiseDirection

    @property
    def contact_ratio_factor_scuffing(self) -> 'float':
        '''float: 'ContactRatioFactorScuffing' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.ContactRatioFactorScuffing

    @property
    def integral_flash_temperature(self) -> 'float':
        '''float: 'IntegralFlashTemperature' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.IntegralFlashTemperature

    @property
    def gear_single_flank_ratings(self) -> 'List[_383.KlingelnbergCycloPalloidHypoidGearSingleFlankRating]':
        '''List[KlingelnbergCycloPalloidHypoidGearSingleFlankRating]: 'GearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearSingleFlankRatings, constructor.new(_383.KlingelnbergCycloPalloidHypoidGearSingleFlankRating))
        return value

    @property
    def kn3030_klingelnberg_gear_single_flank_ratings(self) -> 'List[_383.KlingelnbergCycloPalloidHypoidGearSingleFlankRating]':
        '''List[KlingelnbergCycloPalloidHypoidGearSingleFlankRating]: 'KN3030KlingelnbergGearSingleFlankRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.KN3030KlingelnbergGearSingleFlankRatings, constructor.new(_383.KlingelnbergCycloPalloidHypoidGearSingleFlankRating))
        return value
