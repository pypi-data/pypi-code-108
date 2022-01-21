'''_5041.py

KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4890
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5007
from mastapy._internal.python_net import python_net_import

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis',)


class KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis(_5007.ConicalGearSetCompoundModalAnalysis):
    '''KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'KlingelnbergCycloPalloidConicalGearSetCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4890.KlingelnbergCycloPalloidConicalGearSetModalAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearSetModalAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4890.KlingelnbergCycloPalloidConicalGearSetModalAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4890.KlingelnbergCycloPalloidConicalGearSetModalAnalysis]':
        '''List[KlingelnbergCycloPalloidConicalGearSetModalAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4890.KlingelnbergCycloPalloidConicalGearSetModalAnalysis))
        return value
