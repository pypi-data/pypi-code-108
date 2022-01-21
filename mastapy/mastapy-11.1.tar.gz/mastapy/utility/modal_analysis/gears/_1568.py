'''_1568.py

GearMeshForTE
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.utility.modal_analysis.gears import _1569, _1573
from mastapy._internal.python_net import python_net_import

_GEAR_MESH_FOR_TE = python_net_import('SMT.MastaAPI.Utility.ModalAnalysis.Gears', 'GearMeshForTE')


__docformat__ = 'restructuredtext en'
__all__ = ('GearMeshForTE',)


class GearMeshForTE(_1573.OrderForTE):
    '''GearMeshForTE

    This is a mastapy class.
    '''

    TYPE = _GEAR_MESH_FOR_TE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearMeshForTE.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def number_of_teeth(self) -> 'str':
        '''str: 'NumberOfTeeth' is the original name of this property.'''

        return self.wrapped.NumberOfTeeth

    @number_of_teeth.setter
    def number_of_teeth(self, value: 'str'):
        self.wrapped.NumberOfTeeth = str(value) if value else ''

    @property
    def attached_gears(self) -> 'List[_1569.GearOrderForTE]':
        '''List[GearOrderForTE]: 'AttachedGears' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AttachedGears, constructor.new(_1569.GearOrderForTE))
        return value
