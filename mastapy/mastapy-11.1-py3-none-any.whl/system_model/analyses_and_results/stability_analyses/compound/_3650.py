'''_3650.py

BoltedJointCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2185
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3517
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3728
from mastapy._internal.python_net import python_net_import

_BOLTED_JOINT_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'BoltedJointCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltedJointCompoundStabilityAnalysis',)


class BoltedJointCompoundStabilityAnalysis(_3728.SpecialisedAssemblyCompoundStabilityAnalysis):
    '''BoltedJointCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _BOLTED_JOINT_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltedJointCompoundStabilityAnalysis.TYPE'):
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
    def assembly_analysis_cases_ready(self) -> 'List[_3517.BoltedJointStabilityAnalysis]':
        '''List[BoltedJointStabilityAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_3517.BoltedJointStabilityAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_3517.BoltedJointStabilityAnalysis]':
        '''List[BoltedJointStabilityAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_3517.BoltedJointStabilityAnalysis))
        return value
