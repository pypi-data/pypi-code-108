'''_6198.py

MassDiscCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6069
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6245
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'MassDiscCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundDynamicAnalysis',)


class MassDiscCompoundDynamicAnalysis(_6245.VirtualComponentCompoundDynamicAnalysis):
    '''MassDiscCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6069.MassDiscDynamicAnalysis]':
        '''List[MassDiscDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6069.MassDiscDynamicAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundDynamicAnalysis]':
        '''List[MassDiscCompoundDynamicAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6069.MassDiscDynamicAnalysis]':
        '''List[MassDiscDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6069.MassDiscDynamicAnalysis))
        return value
