'''_2228.py

ConcentricPartGroup
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy._math.vector_2d import Vector2D
from mastapy.system_model.part_model.part_groups import _2229, _2227
from mastapy._internal.python_net import python_net_import

_CONCENTRIC_PART_GROUP = python_net_import('SMT.MastaAPI.SystemModel.PartModel.PartGroups', 'ConcentricPartGroup')


__docformat__ = 'restructuredtext en'
__all__ = ('ConcentricPartGroup',)


class ConcentricPartGroup(_2227.ConcentricOrParallelPartGroup):
    '''ConcentricPartGroup

    This is a mastapy class.
    '''

    TYPE = _CONCENTRIC_PART_GROUP

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConcentricPartGroup.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def total_of_cylindrical_gear_face_widths(self) -> 'float':
        '''float: 'TotalOfCylindricalGearFaceWidths' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.TotalOfCylindricalGearFaceWidths

    @property
    def radial_position(self) -> 'Vector2D':
        '''Vector2D: 'RadialPosition' is the original name of this property.'''

        value = conversion.pn_to_mp_vector2d(self.wrapped.RadialPosition)
        return value

    @radial_position.setter
    def radial_position(self, value: 'Vector2D'):
        value = value if value else None
        value = conversion.mp_to_pn_vector2d(value)
        self.wrapped.RadialPosition = value

    @property
    def parallel_groups(self) -> 'List[_2229.ConcentricPartGroupParallelToThis]':
        '''List[ConcentricPartGroupParallelToThis]: 'ParallelGroups' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ParallelGroups, constructor.new(_2229.ConcentricPartGroupParallelToThis))
        return value
