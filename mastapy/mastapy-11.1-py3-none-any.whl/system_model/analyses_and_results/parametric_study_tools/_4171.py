'''_4171.py

ZerolBevelGearMeshParametricStudyTool
'''


from typing import List

from mastapy.system_model.connections_and_sockets.gears import _2073
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6705
from mastapy.system_model.analyses_and_results.system_deflections import _2574
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4043
from mastapy._internal.python_net import python_net_import

_ZEROL_BEVEL_GEAR_MESH_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ZerolBevelGearMeshParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ZerolBevelGearMeshParametricStudyTool',)


class ZerolBevelGearMeshParametricStudyTool(_4043.BevelGearMeshParametricStudyTool):
    '''ZerolBevelGearMeshParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _ZEROL_BEVEL_GEAR_MESH_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ZerolBevelGearMeshParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2073.ZerolBevelGearMesh':
        '''ZerolBevelGearMesh: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2073.ZerolBevelGearMesh)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6705.ZerolBevelGearMeshLoadCase':
        '''ZerolBevelGearMeshLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6705.ZerolBevelGearMeshLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def connection_system_deflection_results(self) -> 'List[_2574.ZerolBevelGearMeshSystemDeflection]':
        '''List[ZerolBevelGearMeshSystemDeflection]: 'ConnectionSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionSystemDeflectionResults, constructor.new(_2574.ZerolBevelGearMeshSystemDeflection))
        return value
