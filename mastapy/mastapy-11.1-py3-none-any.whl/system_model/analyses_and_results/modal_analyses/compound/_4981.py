'''_4981.py

BearingCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2182
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses import _4828
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _5009
from mastapy._internal.python_net import python_net_import

_BEARING_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'BearingCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BearingCompoundModalAnalysis',)


class BearingCompoundModalAnalysis(_5009.ConnectorCompoundModalAnalysis):
    '''BearingCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEARING_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BearingCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2182.Bearing':
        '''Bearing: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2182.Bearing)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4828.BearingModalAnalysis]':
        '''List[BearingModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4828.BearingModalAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[BearingCompoundModalAnalysis]':
        '''List[BearingCompoundModalAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(BearingCompoundModalAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4828.BearingModalAnalysis]':
        '''List[BearingModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4828.BearingModalAnalysis))
        return value
