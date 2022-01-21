'''_742.py

ConicalMeshFlankMicroGeometryConfig
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.conical.micro_geometry import _1120
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_CONICAL_MESH_FLANK_MICRO_GEOMETRY_CONFIG = python_net_import('SMT.MastaAPI.Gears.Manufacturing.Bevel', 'ConicalMeshFlankMicroGeometryConfig')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalMeshFlankMicroGeometryConfig',)


class ConicalMeshFlankMicroGeometryConfig(_0.APIBase):
    '''ConicalMeshFlankMicroGeometryConfig

    This is a mastapy class.
    '''

    TYPE = _CONICAL_MESH_FLANK_MICRO_GEOMETRY_CONFIG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalMeshFlankMicroGeometryConfig.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def perform_vh_check(self) -> 'bool':
        '''bool: 'PerformVHCheck' is the original name of this property.'''

        return self.wrapped.PerformVHCheck

    @perform_vh_check.setter
    def perform_vh_check(self, value: 'bool'):
        self.wrapped.PerformVHCheck = bool(value) if value else False

    @property
    def delta_v_as_percent_of_wheel_tip_to_fillet_flank_boundary(self) -> 'float':
        '''float: 'DeltaVAsPercentOfWheelTipToFilletFlankBoundary' is the original name of this property.'''

        return self.wrapped.DeltaVAsPercentOfWheelTipToFilletFlankBoundary

    @delta_v_as_percent_of_wheel_tip_to_fillet_flank_boundary.setter
    def delta_v_as_percent_of_wheel_tip_to_fillet_flank_boundary(self, value: 'float'):
        self.wrapped.DeltaVAsPercentOfWheelTipToFilletFlankBoundary = float(value) if value else 0.0

    @property
    def delta_h_as_percent_of_face_width(self) -> 'float':
        '''float: 'DeltaHAsPercentOfFaceWidth' is the original name of this property.'''

        return self.wrapped.DeltaHAsPercentOfFaceWidth

    @delta_h_as_percent_of_face_width.setter
    def delta_h_as_percent_of_face_width(self, value: 'float'):
        self.wrapped.DeltaHAsPercentOfFaceWidth = float(value) if value else 0.0

    @property
    def specified_ease_off_surface(self) -> '_1120.ConicalGearFlankMicroGeometry':
        '''ConicalGearFlankMicroGeometry: 'SpecifiedEaseOffSurface' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1120.ConicalGearFlankMicroGeometry)(self.wrapped.SpecifiedEaseOffSurface) if self.wrapped.SpecifiedEaseOffSurface is not None else None
