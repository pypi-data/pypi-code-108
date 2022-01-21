'''_949.py

FaceGearMeshMicroGeometry
'''


from typing import List

from mastapy.gears.gear_designs.face import _948, _953, _950
from mastapy._internal import constructor, conversion
from mastapy.gears.analysis import _1169
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_MESH_MICRO_GEOMETRY = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Face', 'FaceGearMeshMicroGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearMeshMicroGeometry',)


class FaceGearMeshMicroGeometry(_1169.GearMeshImplementationDetail):
    '''FaceGearMeshMicroGeometry

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_MESH_MICRO_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearMeshMicroGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_mesh(self) -> '_948.FaceGearMeshDesign':
        '''FaceGearMeshDesign: 'FaceMesh' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_948.FaceGearMeshDesign)(self.wrapped.FaceMesh) if self.wrapped.FaceMesh is not None else None

    @property
    def face_gear_set_micro_geometry(self) -> '_953.FaceGearSetMicroGeometry':
        '''FaceGearSetMicroGeometry: 'FaceGearSetMicroGeometry' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_953.FaceGearSetMicroGeometry)(self.wrapped.FaceGearSetMicroGeometry) if self.wrapped.FaceGearSetMicroGeometry is not None else None

    @property
    def face_gear_micro_geometries(self) -> 'List[_950.FaceGearMicroGeometry]':
        '''List[FaceGearMicroGeometry]: 'FaceGearMicroGeometries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.FaceGearMicroGeometries, constructor.new(_950.FaceGearMicroGeometry))
        return value
