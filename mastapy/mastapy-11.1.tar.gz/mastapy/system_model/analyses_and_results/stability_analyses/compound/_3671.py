'''_3671.py

CVTCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.stability_analyses import _3541
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3640
from mastapy._internal.python_net import python_net_import

_CVT_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'CVTCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTCompoundStabilityAnalysis',)


class CVTCompoundStabilityAnalysis(_3640.BeltDriveCompoundStabilityAnalysis):
    '''CVTCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _CVT_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTCompoundStabilityAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_3541.CVTStabilityAnalysis]':
        '''List[CVTStabilityAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3541.CVTStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3541.CVTStabilityAnalysis]':
        '''List[CVTStabilityAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3541.CVTStabilityAnalysis))
        return value
