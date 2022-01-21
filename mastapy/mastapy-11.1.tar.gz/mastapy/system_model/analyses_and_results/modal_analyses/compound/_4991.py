'''_4991.py

BevelGearSetCompoundModalAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses import _4838
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses.compound import _4979
from mastapy._internal.python_net import python_net_import

_BEVEL_GEAR_SET_COMPOUND_MODAL_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalyses.Compound', 'BevelGearSetCompoundModalAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BevelGearSetCompoundModalAnalysis',)


class BevelGearSetCompoundModalAnalysis(_4979.AGMAGleasonConicalGearSetCompoundModalAnalysis):
    '''BevelGearSetCompoundModalAnalysis

    This is a mastapy class.
    '''

    TYPE = _BEVEL_GEAR_SET_COMPOUND_MODAL_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BevelGearSetCompoundModalAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4838.BevelGearSetModalAnalysis]':
        '''List[BevelGearSetModalAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4838.BevelGearSetModalAnalysis))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4838.BevelGearSetModalAnalysis]':
        '''List[BevelGearSetModalAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4838.BevelGearSetModalAnalysis))
        return value
