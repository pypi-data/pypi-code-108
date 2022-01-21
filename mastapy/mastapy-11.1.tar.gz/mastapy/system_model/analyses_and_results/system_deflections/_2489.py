'''_2489.py

FaceGearMeshSystemDeflection
'''


from mastapy._internal import constructor
from mastapy.gears.gear_designs.conical import _1107
from mastapy.system_model.connections_and_sockets.gears import _2053
from mastapy.system_model.analyses_and_results.static_loads import _6600
from mastapy.system_model.analyses_and_results.power_flows import _3819
from mastapy.gears.rating.face import _413
from mastapy.system_model.analyses_and_results.system_deflections import _2494
from mastapy._internal.python_net import python_net_import

_FACE_GEAR_MESH_SYSTEM_DEFLECTION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections', 'FaceGearMeshSystemDeflection')


__docformat__ = 'restructuredtext en'
__all__ = ('FaceGearMeshSystemDeflection',)


class FaceGearMeshSystemDeflection(_2494.GearMeshSystemDeflection):
    '''FaceGearMeshSystemDeflection

    This is a mastapy class.
    '''

    TYPE = _FACE_GEAR_MESH_SYSTEM_DEFLECTION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FaceGearMeshSystemDeflection.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def linear_misalignment_in_surface_of_action(self) -> 'float':
        '''float: 'LinearMisalignmentInSurfaceOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LinearMisalignmentInSurfaceOfAction

    @property
    def angular_misalignment_in_surface_of_action(self) -> 'float':
        '''float: 'AngularMisalignmentInSurfaceOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AngularMisalignmentInSurfaceOfAction

    @property
    def pinion_angular_misalignment_in_surface_of_action(self) -> 'float':
        '''float: 'PinionAngularMisalignmentInSurfaceOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.PinionAngularMisalignmentInSurfaceOfAction

    @property
    def wheel_angular_misalignment_in_surface_of_action(self) -> 'float':
        '''float: 'WheelAngularMisalignmentInSurfaceOfAction' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.WheelAngularMisalignmentInSurfaceOfAction

    @property
    def misalignments_pinion(self) -> '_1107.ConicalMeshMisalignments':
        '''ConicalMeshMisalignments: 'MisalignmentsPinion' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1107.ConicalMeshMisalignments)(self.wrapped.MisalignmentsPinion) if self.wrapped.MisalignmentsPinion is not None else None

    @property
    def misalignments_wheel(self) -> '_1107.ConicalMeshMisalignments':
        '''ConicalMeshMisalignments: 'MisalignmentsWheel' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1107.ConicalMeshMisalignments)(self.wrapped.MisalignmentsWheel) if self.wrapped.MisalignmentsWheel is not None else None

    @property
    def misalignments_total(self) -> '_1107.ConicalMeshMisalignments':
        '''ConicalMeshMisalignments: 'MisalignmentsTotal' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_1107.ConicalMeshMisalignments)(self.wrapped.MisalignmentsTotal) if self.wrapped.MisalignmentsTotal is not None else None

    @property
    def connection_design(self) -> '_2053.FaceGearMesh':
        '''FaceGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2053.FaceGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6600.FaceGearMeshLoadCase':
        '''FaceGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6600.FaceGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def power_flow_results(self) -> '_3819.FaceGearMeshPowerFlow':
        '''FaceGearMeshPowerFlow: 'PowerFlowResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_3819.FaceGearMeshPowerFlow)(self.wrapped.PowerFlowResults) if self.wrapped.PowerFlowResults is not None else None

    @property
    def rating(self) -> '_413.FaceGearMeshRating':
        '''FaceGearMeshRating: 'Rating' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_413.FaceGearMeshRating)(self.wrapped.Rating) if self.wrapped.Rating is not None else None

    @property
    def component_detailed_analysis(self) -> '_413.FaceGearMeshRating':
        '''FaceGearMeshRating: 'ComponentDetailedAnalysis' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_413.FaceGearMeshRating)(self.wrapped.ComponentDetailedAnalysis) if self.wrapped.ComponentDetailedAnalysis is not None else None
