'''_2516.py

MeshSeparationsAtFaceWidth
'''


from mastapy._internal import constructor
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_MESH_SEPARATIONS_AT_FACE_WIDTH = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'MeshSeparationsAtFaceWidth')


__docformat__ = 'restructuredtext en'
__all__ = ('MeshSeparationsAtFaceWidth',)


class MeshSeparationsAtFaceWidth(_0.APIBase):
    '''MeshSeparationsAtFaceWidth

    This is a mastapy class.
    '''

    TYPE = _MESH_SEPARATIONS_AT_FACE_WIDTH

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeshSeparationsAtFaceWidth.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def face_width_location(self) -> 'float':
        '''float: 'FaceWidthLocation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.FaceWidthLocation

    @property
    def left_flank_separation(self) -> 'float':
        '''float: 'LeftFlankSeparation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LeftFlankSeparation

    @property
    def right_flank_separation(self) -> 'float':
        '''float: 'RightFlankSeparation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.RightFlankSeparation

    @property
    def name(self) -> 'str':
        '''str: 'Name' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Name
