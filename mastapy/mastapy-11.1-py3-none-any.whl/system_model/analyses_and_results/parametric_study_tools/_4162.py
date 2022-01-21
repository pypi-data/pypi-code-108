'''_4162.py

TorqueConverterConnectionParametricStudyTool
'''


from typing import List

from mastapy.system_model.connections_and_sockets.couplings import _2094
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.static_loads import _6691
from mastapy.system_model.analyses_and_results.system_deflections import _2563
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4064
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_CONNECTION_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'TorqueConverterConnectionParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterConnectionParametricStudyTool',)


class TorqueConverterConnectionParametricStudyTool(_4064.CouplingConnectionParametricStudyTool):
    '''TorqueConverterConnectionParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_CONNECTION_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterConnectionParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_design(self) -> '_2094.TorqueConverterConnection':
        '''TorqueConverterConnection: 'ConnectionDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2094.TorqueConverterConnection)(self.wrapped.ConnectionDesign) if self.wrapped.ConnectionDesign is not None else None

    @property
    def connection_load_case(self) -> '_6691.TorqueConverterConnectionLoadCase':
        '''TorqueConverterConnectionLoadCase: 'ConnectionLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6691.TorqueConverterConnectionLoadCase)(self.wrapped.ConnectionLoadCase) if self.wrapped.ConnectionLoadCase is not None else None

    @property
    def connection_system_deflection_results(self) -> 'List[_2563.TorqueConverterConnectionSystemDeflection]':
        '''List[TorqueConverterConnectionSystemDeflection]: 'ConnectionSystemDeflectionResults' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionSystemDeflectionResults, constructor.new(_2563.TorqueConverterConnectionSystemDeflection))
        return value
