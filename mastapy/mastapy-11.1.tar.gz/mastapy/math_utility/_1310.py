'''_1310.py

FacetedBody
'''


from typing import List

from mastapy.math_utility import _1311
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FACETED_BODY = python_net_import('SMT.MastaAPI.MathUtility', 'FacetedBody')


__docformat__ = 'restructuredtext en'
__all__ = ('FacetedBody',)


class FacetedBody(_0.APIBase):
    '''FacetedBody

    This is a mastapy class.
    '''

    TYPE = _FACETED_BODY

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FacetedBody.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def surfaces(self) -> 'List[_1311.FacetedSurface]':
        '''List[FacetedSurface]: 'Surfaces' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Surfaces, constructor.new(_1311.FacetedSurface))
        return value

    def add_surface(self, vertices: 'List[List[float]]', normals: 'List[List[float]]', facets: 'List[List[int]]'):
        ''' 'AddSurface' is the original name of this method.

        Args:
            vertices (List[List[float]])
            normals (List[List[float]])
            facets (List[List[int]])
        '''

        vertices = conversion.mp_to_pn_objects_in_list(vertices)
        normals = conversion.mp_to_pn_objects_in_list(normals)
        facets = conversion.mp_to_pn_objects_in_list(facets)
        self.wrapped.AddSurface(vertices, normals, facets)
