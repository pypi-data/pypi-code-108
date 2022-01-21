'''_499.py

ConicalGearMeshRating
'''


from typing import List

from mastapy.gears.load_case.conical import _847
from mastapy._internal import constructor, conversion
from mastapy.gears.load_case.bevel import _852
from mastapy._internal.cast_exception import CastException
from mastapy.gears.rating.conical import _505
from mastapy.gears.rating import _326
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_MESH_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Conical', 'ConicalGearMeshRating')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearMeshRating',)


class ConicalGearMeshRating(_326.GearMeshRating):
    '''ConicalGearMeshRating

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_MESH_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearMeshRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mesh_load_case(self) -> '_847.ConicalMeshLoadCase':
        '''ConicalMeshLoadCase: 'MeshLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _847.ConicalMeshLoadCase.TYPE not in self.wrapped.MeshLoadCase.__class__.__mro__:
            raise CastException('Failed to cast mesh_load_case to ConicalMeshLoadCase. Expected: {}.'.format(self.wrapped.MeshLoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MeshLoadCase.__class__)(self.wrapped.MeshLoadCase) if self.wrapped.MeshLoadCase is not None else None

    @property
    def conical_mesh_load_case(self) -> '_847.ConicalMeshLoadCase':
        '''ConicalMeshLoadCase: 'ConicalMeshLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _847.ConicalMeshLoadCase.TYPE not in self.wrapped.ConicalMeshLoadCase.__class__.__mro__:
            raise CastException('Failed to cast conical_mesh_load_case to ConicalMeshLoadCase. Expected: {}.'.format(self.wrapped.ConicalMeshLoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ConicalMeshLoadCase.__class__)(self.wrapped.ConicalMeshLoadCase) if self.wrapped.ConicalMeshLoadCase is not None else None

    @property
    def meshed_gears(self) -> 'List[_505.ConicalMeshedGearRating]':
        '''List[ConicalMeshedGearRating]: 'MeshedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshedGears, constructor.new(_505.ConicalMeshedGearRating))
        return value
