'''_2128.py

FESubstructureNodeModeShapes
'''


from typing import List

from mastapy.system_model.fe import _2126, _2127
from mastapy._internal import constructor, conversion
from mastapy.math_utility import _1297
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_SUBSTRUCTURE_NODE_MODE_SHAPES = python_net_import('SMT.MastaAPI.SystemModel.FE', 'FESubstructureNodeModeShapes')


__docformat__ = 'restructuredtext en'
__all__ = ('FESubstructureNodeModeShapes',)


class FESubstructureNodeModeShapes(_0.APIBase):
    '''FESubstructureNodeModeShapes

    This is a mastapy class.
    '''

    TYPE = _FE_SUBSTRUCTURE_NODE_MODE_SHAPES

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FESubstructureNodeModeShapes.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def condensation_node(self) -> '_2126.FESubstructureNode':
        '''FESubstructureNode: 'CondensationNode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2126.FESubstructureNode)(self.wrapped.CondensationNode) if self.wrapped.CondensationNode is not None else None

    @property
    def connected_component_local_coordinate_system(self) -> '_1297.CoordinateSystem3D':
        '''CoordinateSystem3D: 'ConnectedComponentLocalCoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1297.CoordinateSystem3D)(self.wrapped.ConnectedComponentLocalCoordinateSystem) if self.wrapped.ConnectedComponentLocalCoordinateSystem is not None else None

    @property
    def mode_shapes_at_condensation_node(self) -> 'List[_2127.FESubstructureNodeModeShape]':
        '''List[FESubstructureNodeModeShape]: 'ModeShapesAtCondensationNode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ModeShapesAtCondensationNode, constructor.new(_2127.FESubstructureNodeModeShape))
        return value
