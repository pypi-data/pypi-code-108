'''_1057.py

CylindricalGearSetMicroGeometry
'''


from typing import List

from mastapy.gears.gear_designs.cylindrical import _984, _995
from mastapy._internal import constructor, conversion
from mastapy._internal.cast_exception import CastException
from mastapy.gears.gear_designs.cylindrical.micro_geometry import _1052, _1050
from mastapy.gears.analysis import _1175
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_SET_MICRO_GEOMETRY = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearSetMicroGeometry')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearSetMicroGeometry',)


class CylindricalGearSetMicroGeometry(_1175.GearSetImplementationDetail):
    '''CylindricalGearSetMicroGeometry

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_SET_MICRO_GEOMETRY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearSetMicroGeometry.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cylindrical_gear_set_design(self) -> '_984.CylindricalGearSetDesign':
        '''CylindricalGearSetDesign: 'CylindricalGearSetDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _984.CylindricalGearSetDesign.TYPE not in self.wrapped.CylindricalGearSetDesign.__class__.__mro__:
            raise CastException('Failed to cast cylindrical_gear_set_design to CylindricalGearSetDesign. Expected: {}.'.format(self.wrapped.CylindricalGearSetDesign.__class__.__qualname__))

        return constructor.new_override(self.wrapped.CylindricalGearSetDesign.__class__)(self.wrapped.CylindricalGearSetDesign) if self.wrapped.CylindricalGearSetDesign is not None else None

    @property
    def cylindrical_gear_micro_geometries(self) -> 'List[_1052.CylindricalGearMicroGeometry]':
        '''List[CylindricalGearMicroGeometry]: 'CylindricalGearMicroGeometries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalGearMicroGeometries, constructor.new(_1052.CylindricalGearMicroGeometry))
        return value

    @property
    def cylindrical_mesh_micro_geometries(self) -> 'List[_1050.CylindricalGearMeshMicroGeometry]':
        '''List[CylindricalGearMeshMicroGeometry]: 'CylindricalMeshMicroGeometries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.CylindricalMeshMicroGeometries, constructor.new(_1050.CylindricalGearMeshMicroGeometry))
        return value
