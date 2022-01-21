'''_383.py

KlingelnbergCycloPalloidHypoidGearSingleFlankRating
'''


from mastapy._internal import constructor
from mastapy.gears.rating.klingelnberg_conical.kn3030 import _382
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SINGLE_FLANK_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.KlingelnbergConical.KN3030', 'KlingelnbergCycloPalloidHypoidGearSingleFlankRating')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidHypoidGearSingleFlankRating',)


class KlingelnbergCycloPalloidHypoidGearSingleFlankRating(_382.KlingelnbergCycloPalloidConicalGearSingleFlankRating):
    '''KlingelnbergCycloPalloidHypoidGearSingleFlankRating

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SINGLE_FLANK_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidHypoidGearSingleFlankRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def tangential_speed(self) -> 'float':
        '''float: 'TangentialSpeed' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TangentialSpeed
