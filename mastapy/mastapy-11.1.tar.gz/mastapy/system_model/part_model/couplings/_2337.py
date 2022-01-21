'''_2337.py

RollingRingAssembly
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.couplings import _2336
from mastapy.system_model.part_model import _2217
from mastapy._internal.python_net import python_net_import

_ROLLING_RING_ASSEMBLY = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Couplings', 'RollingRingAssembly')


__docformat__ = 'restructuredtext en'
__all__ = ('RollingRingAssembly',)


class RollingRingAssembly(_2217.SpecialisedAssembly):
    '''RollingRingAssembly

    This is a mastapy class.
    '''

    TYPE = _ROLLING_RING_ASSEMBLY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'RollingRingAssembly.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def angle(self) -> 'float':
        '''float: 'Angle' is the original name of this property.'''

        return self.wrapped.Angle

    @angle.setter
    def angle(self, value: 'float'):
        self.wrapped.Angle = float(value) if value else 0.0

    @property
    def rolling_rings(self) -> 'List[_2336.RollingRing]':
        '''List[RollingRing]: 'RollingRings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.RollingRings, constructor.new(_2336.RollingRing))
        return value
