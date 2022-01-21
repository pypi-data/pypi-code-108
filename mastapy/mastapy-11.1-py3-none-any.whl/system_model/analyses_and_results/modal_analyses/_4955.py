'''_4955.py

WormGearMeshModalAnalysis
'''


from mastapy.system_model.connections_and_sockets.gears import _2071
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6702
from mastapy.system_model.analyses_and_results.system_deflections import _2571
from mastapy.system_model.analyses_and_results.modal_analyses import _4880
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_MESH_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses', 'WormGearMeshModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearMeshModalAnalysis',)


class WormGearMeshModalAnalysis(_4880.GearMeshModalAnalysis):
    '''WormGearMeshModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_MESH_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearMeshModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2071.WormGearMesh':
        '''WormGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2071.WormGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6702.WormGearMeshLoadCase':
        '''WormGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6702.WormGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def system_deflection_results(self) -> '_2571.WormGearMeshSystemDeflection':
        '''WormGearMeshSystemDeflection: 'SystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2571.WormGearMeshSystemDeflection)(self.wrapped.SystemDeflectionResults) if self.wrapped.SystemDeflectionResults is not None else None
