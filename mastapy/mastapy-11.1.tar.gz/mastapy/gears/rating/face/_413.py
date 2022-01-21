'''_413.py

FaceGearMeshRating
'''


from typing import List

from mastapy.gears import _292
from mastapy._internal import enum_with_selected_value_runtime, constructor, conversion
from mastapy.gears.load_case.face import _841
from mastapy.gears.rating.face import _416, _414
from mastapy.gears.rating.cylindrical.iso6336 import _475, _477
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.face import _948
from mastapy.gears.rating import _326
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_MESH_RATING = python_net_import('SMT.MastaAPI.Gears.Rating.Face', 'FaceGearMeshRating')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearMeshRating',)


class FaceGearMeshRating(_326.GearMeshRating):
    '''FaceGearMeshRating

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_MESH_RATING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearMeshRating.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def active_flank(self) -> '_292.GearFlanks':
        '''GearFlanks: 'ActiveFlank' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_enum(self.wrapped.ActiveFlank)
        return constructor.new(_292.GearFlanks)(value) if value is not None else None

    @property
    def mesh_load_case(self) -> '_841.FaceMeshLoadCase':
        '''FaceMeshLoadCase: 'MeshLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_841.FaceMeshLoadCase)(self.wrapped.MeshLoadCase) if self.wrapped.MeshLoadCase is not None else None

    @property
    def gear_set_rating(self) -> '_416.FaceGearSetRating':
        '''FaceGearSetRating: 'GearSetRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_416.FaceGearSetRating)(self.wrapped.GearSetRating) if self.wrapped.GearSetRating is not None else None

    @property
    def mesh_single_flank_rating(self) -> '_475.ISO63362006MeshSingleFlankRating':
        '''ISO63362006MeshSingleFlankRating: 'MeshSingleFlankRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _475.ISO63362006MeshSingleFlankRating.TYPE not in self.wrapped.MeshSingleFlankRating.__class__.__mro__:
            raise CastException('Failed to cast mesh_single_flank_rating to ISO63362006MeshSingleFlankRating. Expected: {}.'.format(self.wrapped.MeshSingleFlankRating.__class__.__qualname__))

        return constructor.new_override(self.wrapped.MeshSingleFlankRating.__class__)(self.wrapped.MeshSingleFlankRating) if self.wrapped.MeshSingleFlankRating is not None else None

    @property
    def face_gear_mesh(self) -> '_948.FaceGearMeshDesign':
        '''FaceGearMeshDesign: 'FaceGearMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_948.FaceGearMeshDesign)(self.wrapped.FaceGearMesh) if self.wrapped.FaceGearMesh is not None else None

    @property
    def face_gear_ratings(self) -> 'List[_414.FaceGearRating]':
        '''List[FaceGearRating]: 'FaceGearRatings' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearRatings, constructor.new(_414.FaceGearRating))
        return value
