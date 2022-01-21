'''_4168.py

WormGearMeshParametricStudyTool
'''


from typing import List

from mastapy.system_model.connections_and_sockets.gears import _2071
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6702
from mastapy.system_model.analyses_and_results.system_deflections import _2571
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4092
from mastapy._internal.python_net import python_net_import

_WORM_GEAR_MESH_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'WormGearMeshParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('WormGearMeshParametricStudyTool',)


class WormGearMeshParametricStudyTool(_4092.GearMeshParametricStudyTool):
    '''WormGearMeshParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _WORM_GEAR_MESH_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'WormGearMeshParametricStudyTool.TYPE'):
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
    def connection_system_deflection_results(self) -> 'List[_2571.WormGearMeshSystemDeflection]':
        '''List[WormGearMeshSystemDeflection]: 'ConnectionSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionSystemDeflectionResults, constructor.new(_2571.WormGearMeshSystemDeflection))
        return value
