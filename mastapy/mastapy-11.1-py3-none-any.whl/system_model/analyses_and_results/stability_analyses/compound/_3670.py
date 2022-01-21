'''_3670.py

CVTBeltConnectionCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3539
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3639
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'CVTBeltConnectionCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionCompoundStabilityAnalysis',)


class CVTBeltConnectionCompoundStabilityAnalysis(_3639.BeltConnectionCompoundStabilityAnalysis):
    '''CVTBeltConnectionCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_3539.CVTBeltConnectionStabilityAnalysis]':
        '''List[CVTBeltConnectionStabilityAnalysis]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_3539.CVTBeltConnectionStabilityAnalysis))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_3539.CVTBeltConnectionStabilityAnalysis]':
        '''List[CVTBeltConnectionStabilityAnalysis]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_3539.CVTBeltConnectionStabilityAnalysis))
        return value
