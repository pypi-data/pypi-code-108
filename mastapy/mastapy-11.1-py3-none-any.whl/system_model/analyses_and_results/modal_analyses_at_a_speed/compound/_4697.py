'''_4697.py

AGMAGleasonConicalGearSetCompoundModalAnalysisAtASpeed
'''


from typing import List

from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed import _4568
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_speed.compound import _4725
from mastapy._internal.python_net import python_net_import

_AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtASpeed.Compound', 'AGMAGleasonConicalGearSetCompoundModalAnalysisAtASpeed')


__docformat__ = 'restructuredtext en'
__all__ = ('AGMAGleasonConicalGearSetCompoundModalAnalysisAtASpeed',)


class AGMAGleasonConicalGearSetCompoundModalAnalysisAtASpeed(_4725.ConicalGearSetCompoundModalAnalysisAtASpeed):
    '''AGMAGleasonConicalGearSetCompoundModalAnalysisAtASpeed

    This is a mastapy class.
    '''

    TYPE = _AGMA_GLEASON_CONICAL_GEAR_SET_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AGMAGleasonConicalGearSetCompoundModalAnalysisAtASpeed.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def assembly_analysis_cases(self) -> 'List[_4568.AGMAGleasonConicalGearSetModalAnalysisAtASpeed]':
        '''List[AGMAGleasonConicalGearSetModalAnalysisAtASpeed]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4568.AGMAGleasonConicalGearSetModalAnalysisAtASpeed))
        return value

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4568.AGMAGleasonConicalGearSetModalAnalysisAtASpeed]':
        '''List[AGMAGleasonConicalGearSetModalAnalysisAtASpeed]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4568.AGMAGleasonConicalGearSetModalAnalysisAtASpeed))
        return value
