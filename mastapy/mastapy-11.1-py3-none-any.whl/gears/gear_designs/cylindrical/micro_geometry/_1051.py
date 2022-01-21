'''_1051.py

CylindricalGearMeshMicroGeometryDutyCycle
'''


from typing import List

from mastapy.gears.rating.cylindrical import _427
from mastapy._internal import constructor, conversion
from mastapy.gears.ltca.cylindrical import _817
from mastapy.gears.analysis import _1166
from mastapy._internal.python_net import python_net_import

_CYLINDRICAL_GEAR_MESH_MICRO_GEOMETRY_DUTY_CYCLE = python_net_import('SMT.MastaAPI.Gears.GearDesigns.Cylindrical.MicroGeometry', 'CylindricalGearMeshMicroGeometryDutyCycle')


__docformat__ = 'restructuredtext en'
__all__ = ('CylindricalGearMeshMicroGeometryDutyCycle',)


class CylindricalGearMeshMicroGeometryDutyCycle(_1166.GearMeshDesignAnalysis):
    '''CylindricalGearMeshMicroGeometryDutyCycle

    This is a mastapy class.
    '''

    TYPE = _CYLINDRICAL_GEAR_MESH_MICRO_GEOMETRY_DUTY_CYCLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CylindricalGearMeshMicroGeometryDutyCycle.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def cylindrical_gear_set_duty_cycle_rating(self) -> '_427.CylindricalGearSetDutyCycleRating':
        '''CylindricalGearSetDutyCycleRating: 'CylindricalGearSetDutyCycleRating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_427.CylindricalGearSetDutyCycleRating)(self.wrapped.CylindricalGearSetDutyCycleRating) if self.wrapped.CylindricalGearSetDutyCycleRating is not None else None

    @property
    def meshes_analysis(self) -> 'List[_817.CylindricalGearMeshLoadDistributionAnalysis]':
        '''List[CylindricalGearMeshLoadDistributionAnalysis]: 'MeshesAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.MeshesAnalysis, constructor.new(_817.CylindricalGearMeshLoadDistributionAnalysis))
        return value
