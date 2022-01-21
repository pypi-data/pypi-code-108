'''_2226.py

SpecifiedParallelPartGroupDrawingOrder
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model.projections import _2225
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SPECIFIED_PARALLEL_PART_GROUP_DRAWING_ORDER = python_net_import('SMT.MastaAPI.SystemModel.PartModel.Projections', 'SpecifiedParallelPartGroupDrawingOrder')


__docformat__ = 'restructuredtext en'
__all__ = ('SpecifiedParallelPartGroupDrawingOrder',)


class SpecifiedParallelPartGroupDrawingOrder(_0.APIBase):
    '''SpecifiedParallelPartGroupDrawingOrder

    This is a mastapy class.
    '''

    TYPE = _SPECIFIED_PARALLEL_PART_GROUP_DRAWING_ORDER

    __hash__ = None

    def __init__(self, instance_to_wrap: 'SpecifiedParallelPartGroupDrawingOrder.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name

    @property
    def specified_groups(self) -> 'List[_2225.SpecifiedConcentricPartGroupDrawingOrder]':
        '''List[SpecifiedConcentricPartGroupDrawingOrder]: 'SpecifiedGroups' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.SpecifiedGroups, constructor.new(_2225.SpecifiedConcentricPartGroupDrawingOrder))
        return value
