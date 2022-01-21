'''_1333.py

Vector2DListAccessor
'''


from typing import List

from mastapy._math.vector_2d import Vector2D
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_VECTOR_2D_LIST_ACCESSOR = python_net_import('SMT.MastaAPI.MathUtility', 'Vector2DListAccessor')


__docformat__ = 'restructuredtext en'
__all__ = ('Vector2DListAccessor',)


class Vector2DListAccessor(_0.APIBase):
    '''Vector2DListAccessor

    This is a mastapy class.
    '''

    TYPE = _VECTOR_2D_LIST_ACCESSOR

    __hash__ = None

    def __init__(self, instance_to_wrap: 'Vector2DListAccessor.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    def get_vector_list(self) -> 'List[Vector2D]':
        ''' 'GetVectorList' is the original name of this method.

        Returns:
            List[Vector2D]
        '''

        return conversion.pn_to_mp_objects_in_list(self.wrapped.GetVectorList(), Vector2D)

    def create_new_from_vector_list(self, list: 'List[Vector2D]') -> 'Vector2DListAccessor':
        ''' 'CreateNewFromVectorList' is the original name of this method.

        Args:
            list (List[Vector2D])

        Returns:
            mastapy.math_utility.Vector2DListAccessor
        '''

        list = conversion.mp_to_pn_objects_in_list(list)
        method_result = self.wrapped.CreateNewFromVectorList(list)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None
