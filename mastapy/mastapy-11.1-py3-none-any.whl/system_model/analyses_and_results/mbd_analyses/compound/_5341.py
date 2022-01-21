'''_5341.py

PowerLoadCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2213
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5200
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5376
from mastapy._internal.python_net import python_net_import

_POWER_LOAD_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'PowerLoadCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('PowerLoadCompoundMultibodyDynamicsAnalysis',)


class PowerLoadCompoundMultibodyDynamicsAnalysis(_5376.VirtualComponentCompoundMultibodyDynamicsAnalysis):
    '''PowerLoadCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _POWER_LOAD_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PowerLoadCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2213.PowerLoad':
        '''PowerLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2213.PowerLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5200.PowerLoadMultibodyDynamicsAnalysis]':
        '''List[PowerLoadMultibodyDynamicsAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5200.PowerLoadMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5200.PowerLoadMultibodyDynamicsAnalysis]':
        '''List[PowerLoadMultibodyDynamicsAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5200.PowerLoadMultibodyDynamicsAnalysis))
        return value
