'''_4989.py

BevelGearCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4837
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4977
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'BevelGearCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearCompoundModalAnalysis',)


class BevelGearCompoundModalAnalysis(_4977.AGMAGleasonConicalGearCompoundModalAnalysis):
    '''BevelGearCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4837.BevelGearModalAnalysis]':
        '''List[BevelGearModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4837.BevelGearModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4837.BevelGearModalAnalysis]':
        '''List[BevelGearModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4837.BevelGearModalAnalysis))
        return value
