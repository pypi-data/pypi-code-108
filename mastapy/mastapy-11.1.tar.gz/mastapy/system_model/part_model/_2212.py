'''_2212.py

PointLoad
'''


from mastapy._math.vector_2d import Vector2D
from mastapy._internal import constructor, conversion
from mastapy.system_model.part_model import _2220
from mastapy._internal.python_net import python_net_import

_POINT_LOAD = python_net_import('SMT.MastaAPI.SystemModel.PartModel', 'PointLoad')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoad',)


class PointLoad(_2220.VirtualComponent):
    '''PointLoad

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoad.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def offset(self) -> 'Vector2D':
        '''Vector2D: 'Offset' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_vector2d(self.wrapped.Offset)
        return value

    def set_offset(self, radius: 'float', angle: 'float'):
        ''' 'SetOffset' is the original name of this method.

        Args:
            radius (float)
            angle (float)
        '''

        radius = float(radius)
        angle = float(angle)
        self.wrapped.SetOffset(radius if radius else 0.0, angle if angle else 0.0)
