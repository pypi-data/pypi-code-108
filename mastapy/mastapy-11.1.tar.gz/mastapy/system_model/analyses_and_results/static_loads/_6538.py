'''_6538.py

BevelDifferentialGearMeshLoadCase
'''


from mastapy.system_model.connections_and_sockets.gears import _2043
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6543
from mastapy._internal.python_net import python_net_import

_BEVEL_DIFFERENTIAL_GEAR_MESH_LOAD_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads', 'BevelDifferentialGearMeshLoadCase')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelDifferentialGearMeshLoadCase',)


class BevelDifferentialGearMeshLoadCase(_6543.BevelGearMeshLoadCase):
    '''BevelDifferentialGearMeshLoadCase

    This is a mastapy class.
    '''

    TYPE = _BEVEL_DIFFERENTIAL_GEAR_MESH_LOAD_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelDifferentialGearMeshLoadCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2043.BevelDifferentialGearMesh':
        '''BevelDifferentialGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2043.BevelDifferentialGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None
