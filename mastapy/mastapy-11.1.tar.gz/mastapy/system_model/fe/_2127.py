'''_2127.py

FESubstructureNodeModeShape
'''


from mastapy._internal import constructor
from mastapy.math_utility.measured_vectors import _1363
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FE_SUBSTRUCTURE_NODE_MODE_SHAPE = python_net_import('SMT.MastaAPI.SystemModel.FE', 'FESubstructureNodeModeShape')


__docformat__ = 'restructuredtext en'
__all__ = ('FESubstructureNodeModeShape',)


class FESubstructureNodeModeShape(_0.APIBase):
    '''FESubstructureNodeModeShape

    This is a mastapy class.
    '''

    TYPE = _FE_SUBSTRUCTURE_NODE_MODE_SHAPE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FESubstructureNodeModeShape.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def mode(self) -> 'int':
        '''int: 'Mode' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.Mode

    @property
    def mode_shape_global_cordinate_system(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'ModeShapeGlobalCordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.ModeShapeGlobalCordinateSystem) if self.wrapped.ModeShapeGlobalCordinateSystem is not None else None

    @property
    def mode_shape_component_coordinate_system(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'ModeShapeComponentCoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.ModeShapeComponentCoordinateSystem) if self.wrapped.ModeShapeComponentCoordinateSystem is not None else None

    @property
    def mode_shape_fe_coordinate_system(self) -> '_1363.VectorWithLinearAndAngularComponents':
        '''VectorWithLinearAndAngularComponents: 'ModeShapeFECoordinateSystem' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1363.VectorWithLinearAndAngularComponents)(self.wrapped.ModeShapeFECoordinateSystem) if self.wrapped.ModeShapeFECoordinateSystem is not None else None
