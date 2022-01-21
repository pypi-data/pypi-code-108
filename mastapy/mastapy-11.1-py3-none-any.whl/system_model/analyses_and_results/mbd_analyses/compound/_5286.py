'''_5286.py

ConicalGearCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5138
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5312
from mastapy._internal.python_net import python_net_import

_CONICAL_GEAR_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'ConicalGearCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ConicalGearCompoundMultibodyDynamicsAnalysis',)


class ConicalGearCompoundMultibodyDynamicsAnalysis(_5312.GearCompoundMultibodyDynamicsAnalysis):
    '''ConicalGearCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _CONICAL_GEAR_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ConicalGearCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def planetaries(self) -> 'List[ConicalGearCompoundMultibodyDynamicsAnalysis]':
        '''List[ConicalGearCompoundMultibodyDynamicsAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ConicalGearCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5138.ConicalGearMultibodyDynamicsAnalysis]':
        '''List[ConicalGearMultibodyDynamicsAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5138.ConicalGearMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5138.ConicalGearMultibodyDynamicsAnalysis]':
        '''List[ConicalGearMultibodyDynamicsAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5138.ConicalGearMultibodyDynamicsAnalysis))
        return value
