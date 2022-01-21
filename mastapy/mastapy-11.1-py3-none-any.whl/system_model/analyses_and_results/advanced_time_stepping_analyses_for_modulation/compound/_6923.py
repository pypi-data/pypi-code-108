'''_6923.py

InterMountableComponentConnectionCompoundAdvancedTimeSteppingAnalysisForModulation
'''


from typing import List

from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation import _6794
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.advanced_time_stepping_analyses_for_modulation.compound import _6893
from mastapy._internal.python_net import python_net_import

_INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation.Compound', 'InterMountableComponentConnectionCompoundAdvancedTimeSteppingAnalysisForModulation')


__docformat__ = 'restructuredtext en'
__all__ = ('InterMountableComponentConnectionCompoundAdvancedTimeSteppingAnalysisForModulation',)


class InterMountableComponentConnectionCompoundAdvancedTimeSteppingAnalysisForModulation(_6893.ConnectionCompoundAdvancedTimeSteppingAnalysisForModulation):
    '''InterMountableComponentConnectionCompoundAdvancedTimeSteppingAnalysisForModulation

    This is a mastapy class.
    '''

    TYPE = _INTER_MOUNTABLE_COMPONENT_CONNECTION_COMPOUND_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION

    __hash__ = None

    def __init__(self, instance_to_wrap: 'InterMountableComponentConnectionCompoundAdvancedTimeSteppingAnalysisForModulation.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_6794.InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation]':
        '''List[InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_6794.InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_6794.InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation]':
        '''List[InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_6794.InterMountableComponentConnectionAdvancedTimeSteppingAnalysisForModulation))
        return value
