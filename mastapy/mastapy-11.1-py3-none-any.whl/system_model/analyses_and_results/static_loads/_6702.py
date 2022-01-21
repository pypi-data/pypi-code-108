'''_6702.py

WormGearMeshLoadCase
'''


from mastapy.system_model.connections_and_sockets.gears import _2071
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6607
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'WormGearMeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearMeshLoadCase',)


class WormGearMeshLoadCase(_6607.GearMeshLoadCase):
    '''WormGearMeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearMeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2071.WormGearMesh':
        '''WormGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2071.WormGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
