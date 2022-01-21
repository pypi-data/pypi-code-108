'''_6143.py

BoltedJointCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2185
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6013
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6221
from mastapy._internal.python_net import python_net_import

_BOLTED_JOINT_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'BoltedJointCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('BoltedJointCompoundDynamicAnalysis',)


class BoltedJointCompoundDynamicAnalysis(_6221.SpecialisedAssemblyCompoundDynamicAnalysis):
    '''BoltedJointCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _BOLTED_JOINT_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'BoltedJointCompoundDynamicAnalysis.TYPE'):
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
    def assembly_analysis_cases_ready(self) -> 'List[_6013.BoltedJointDynamicAnalysis]':
        '''List[BoltedJointDynamicAnalysis]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_6013.BoltedJointDynamicAnalysis))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_6013.BoltedJointDynamicAnalysis]':
        '''List[BoltedJointDynamicAnalysis]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_6013.BoltedJointDynamicAnalysis))
        return value
