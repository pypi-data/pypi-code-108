'''_331.py

MeshDutyCycleRating
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.gears.rating import _324, _319
from mastapy._internal.python_net import python_net_import

_MESH_DUTY_CYCLE_RATING = python_net_import('SMT.MastaAPI.Gears.Rating', 'MeshDutyCycleRating')


__docformat__ = 'restructuredtext en'
__all__ = ('MeshDutyCycleRating',)


class MeshDutyCycleRating(_319.AbstractGearMeshRating):
    '''MeshDutyCycleRating

    This is a mastapy class.
    '''

    TYPE = _MESH_DUTY_CYCLE_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeshDutyCycleRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def total_energy(self) -> 'float':
        '''float: 'TotalEnergy' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalEnergy

    @property
    def energy_loss(self) -> 'float':
        '''float: 'EnergyLoss' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.EnergyLoss

    @property
    def mesh_efficiency(self) -> 'float':
        '''float: 'MeshEfficiency' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.MeshEfficiency

    @property
    def gear_duty_cycle_ratings(self) -> 'List[_324.GearDutyCycleRating]':
        '''List[GearDutyCycleRating]: 'GearDutyCycleRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.GearDutyCycleRatings, constructor.new(_324.GearDutyCycleRating))
        return value
