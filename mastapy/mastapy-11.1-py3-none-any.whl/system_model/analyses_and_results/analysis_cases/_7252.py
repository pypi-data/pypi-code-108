'''_7252.py

AnalysisCase
'''


from mastapy._internal import constructor
from mastapy.system_model import _1951
from mastapy.system_model.analyses_and_results import _2391, _2390
from mastapy._internal.python_net import python_net_import

_ANALYSIS_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'AnalysisCase')


__docformat__ = 'restructuredtext en'
__all__ = ('AnalysisCase',)


class AnalysisCase(_2390.Context):
    '''AnalysisCase

    This is a mastapy class.
    '''

    TYPE = _ANALYSIS_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AnalysisCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def analysis_time(self) -> 'float':
        '''float: 'AnalysisTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AnalysisTime

    @property
    def load_case_name(self) -> 'str':
        '''str: 'LoadCaseName' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.LoadCaseName

    @property
    def analysis_setup_time(self) -> 'float':
        '''float: 'AnalysisSetupTime' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return self.wrapped.AnalysisSetupTime

    @property
    def results_ready(self) -> 'bool':
        '''bool: 'ResultsReady' is the original name of this property.'''

        return self.wrapped.ResultsReady

    @results_ready.setter
    def results_ready(self, value: 'bool'):
        self.wrapped.ResultsReady = bool(value) if value else False

    def results_for(self, design_entity: '_1951.DesignEntity') -> '_2391.DesignEntityAnalysis':
        ''' 'ResultsFor' is the original name of this method.

        Args:
            design_entity (mastapy.system_model.DesignEntity)

        Returns:
            mastapy.system_model.analyses_and_results.DesignEntityAnalysis
        '''

        method_result = self.wrapped.ResultsFor(design_entity.wrapped if design_entity else None)
        return constructor.new_override(method_result.__class__)(method_result) if method_result is not None else None

    def perform_analysis(self):
        ''' 'PerformAnalysis' is the original name of this method.'''

        self.wrapped.PerformAnalysis()
