'''_749.py

ConicalPinionMicroGeometryConfig
'''


from mastapy.gears.manufacturing.bevel import _743, _737
from mastapy._internal import constructor
from mastapy._internal.python_net import python_net_import

_CONICAL_PINION_MICRO_GEOMETRY_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalPinionMicroGeometryConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalPinionMicroGeometryConfig',)


class ConicalPinionMicroGeometryConfig(_737.ConicalGearMicroGeometryConfig):
    '''ConicalPinionMicroGeometryConfig

    This is a mastapy class.
    '''

    TYPE = _CONICAL_PINION_MICRO_GEOMETRY_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalPinionMicroGeometryConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def pinion_concave_ob_configuration(self) -> '_743.ConicalMeshFlankNurbsMicroGeometryConfig':
        '''ConicalMeshFlankNurbsMicroGeometryConfig: 'PinionConcaveOBConfiguration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_743.ConicalMeshFlankNurbsMicroGeometryConfig)(self.wrapped.PinionConcaveOBConfiguration) if self.wrapped.PinionConcaveOBConfiguration is not None else None

    @property
    def pinion_convex_ib_configuration(self) -> '_743.ConicalMeshFlankNurbsMicroGeometryConfig':
        '''ConicalMeshFlankNurbsMicroGeometryConfig: 'PinionConvexIBConfiguration' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_743.ConicalMeshFlankNurbsMicroGeometryConfig)(self.wrapped.PinionConvexIBConfiguration) if self.wrapped.PinionConvexIBConfiguration is not None else None
