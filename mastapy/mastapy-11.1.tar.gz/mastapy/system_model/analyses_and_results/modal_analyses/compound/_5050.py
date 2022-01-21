'''_5050.py

MountableComponentCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4902
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4998
from mastapy._internal.python_net import python_net_import

_MOUNTABLE_COMPONENT_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'MountableComponentCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MountableComponentCompoundModalAnalysis',)


class MountableComponentCompoundModalAnalysis(_4998.ComponentCompoundModalAnalysis):
    '''MountableComponentCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _MOUNTABLE_COMPONENT_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MountableComponentCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_4902.MountableComponentModalAnalysis]':
        '''List[MountableComponentModalAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4902.MountableComponentModalAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_4902.MountableComponentModalAnalysis]':
        '''List[MountableComponentModalAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4902.MountableComponentModalAnalysis))
        return value
