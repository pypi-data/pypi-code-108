'''_501.py

ConicalGearSetDutyCycleRating
'''


from typing import List

from mastapy.gears.rating.conical import _504
from mastapy._internal import constructor, conversion
from mastapy.gears.rating import _328
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_SET_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Conical', 'ConicalGearSetDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearSetDutyCycleRating',)


class ConicalGearSetDutyCycleRating(_328.GearSetDutyCycleRating):
    '''ConicalGearSetDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_SET_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearSetDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def gear_mesh_duty_cycle_ratings(self) -> 'List[_504.ConicalMeshDutyCycleRating]':
        '''List[ConicalMeshDutyCycleRating]: 'GearMeshDutyCycleRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearMeshDutyCycleRatings, constructor.new(_504.ConicalMeshDutyCycleRating))
        return value

    @property
    def conical_mesh_duty_cycle_ratings(self) -> 'List[_504.ConicalMeshDutyCycleRating]':
        '''List[ConicalMeshDutyCycleRating]: 'ConicalMeshDutyCycleRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConicalMeshDutyCycleRatings, constructor.new(_504.ConicalMeshDutyCycleRating))
        return value
