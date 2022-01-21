'''_4453.py

BoltedJointCompoundModalAnalysisAtAStiffness
'''


from typing import List

from mastapy.system_model.part_model import _2185
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness import _4322
from mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import _4531
from mastapy._internal.python_net import python_net_import

_BOLTED_JOINT_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound', 'BoltedJointCompoundModalAnalysisAtAStiffness')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltedJointCompoundModalAnalysisAtAStiffness',)


class BoltedJointCompoundModalAnalysisAtAStiffness(_4531.SpecialisedAssemblyCompoundModalAnalysisAtAStiffness):
    '''BoltedJointCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    '''

    TYPE = _BOLTED_JOINT_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltedJointCompoundModalAnalysisAtAStiffness.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2185.BoltedJoint':
        '''BoltedJoint: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2185.BoltedJoint)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2185.BoltedJoint':
        '''BoltedJoint: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2185.BoltedJoint)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4322.BoltedJointModalAnalysisAtAStiffness]':
        '''List[BoltedJointModalAnalysisAtAStiffness]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4322.BoltedJointModalAnalysisAtAStiffness))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4322.BoltedJointModalAnalysisAtAStiffness]':
        '''List[BoltedJointModalAnalysisAtAStiffness]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4322.BoltedJointModalAnalysisAtAStiffness))
        return value
