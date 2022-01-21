'''_5312.py

GearCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.mbd_analyses import _5165
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5331
from mastapy._internal.python_net import python_net_import

_GEAR_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'GearCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('GearCompoundMultibodyDynamicsAnalysis',)


class GearCompoundMultibodyDynamicsAnalysis(_5331.MountableComponentCompoundMultibodyDynamicsAnalysis):
    '''GearCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _GEAR_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'GearCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5165.GearMultibodyDynamicsAnalysis]':
        '''List[GearMultibodyDynamicsAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5165.GearMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5165.GearMultibodyDynamicsAnalysis]':
        '''List[GearMultibodyDynamicsAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5165.GearMultibodyDynamicsAnalysis))
        return value
