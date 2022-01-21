'''_5256.py

AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.analyses_and_results.mbd_analyses import _5104
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5279
from mastapy._internal.python_net import python_net_import

_ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis',)


class AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis(_5279.ComponentCompoundMultibodyDynamicsAnalysis):
    '''AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _ABSTRACT_SHAFT_OR_HOUSING_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AbstractShaftOrHousingCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_analysis_cases(self) -> 'List[_5104.AbstractShaftOrHousingMultibodyDynamicsAnalysis]':
        '''List[AbstractShaftOrHousingMultibodyDynamicsAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5104.AbstractShaftOrHousingMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases_ready(self) -> 'List[_5104.AbstractShaftOrHousingMultibodyDynamicsAnalysis]':
        '''List[AbstractShaftOrHousingMultibodyDynamicsAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5104.AbstractShaftOrHousingMultibodyDynamicsAnalysis))
        return value
