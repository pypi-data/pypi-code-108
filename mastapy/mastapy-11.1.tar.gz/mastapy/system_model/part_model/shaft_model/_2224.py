'''_2224.py

ShaftBow
'''


from typing import List

from mastapy._math.vector_3d import Vector3D
from mastapy._internal import constructor, conversion
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_SHAFT_BOW = python_net_import('SMT.MastaAPI.SystemModel.PartModel.ShaftModel', 'ShaftBow')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftBow',)


class ShaftBow(_0.APIBase):
    '''ShaftBow

    This is a mastapy class.
    '''

    TYPE = _SHAFT_BOW

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftBow.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def linear_displacement(self) -> 'List[Vector3D]':
        '''List[Vector3D]: 'LinearDisplacement' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.LinearDisplacement, Vector3D)
        return value
