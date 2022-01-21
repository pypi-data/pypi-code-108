'''_5349.py

ShaftCompoundMultibodyDynamicsAnalysis
'''


from typing import List

from mastapy.system_model.part_model.shaft_model import _2223
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.mbd_analyses import _5211
from mastapy.system_model.analyses_and_results.mbd_analyses.compound import _5255
from mastapy._internal.python_net import python_net_import

_SHAFT_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses.Compound', 'ShaftCompoundMultibodyDynamicsAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('ShaftCompoundMultibodyDynamicsAnalysis',)


class ShaftCompoundMultibodyDynamicsAnalysis(_5255.AbstractShaftCompoundMultibodyDynamicsAnalysis):
    '''ShaftCompoundMultibodyDynamicsAnalysis

    This is a mastapy class.
    '''

    TYPE = _SHAFT_COMPOUND_MULTIBODY_DYNAMICS_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ShaftCompoundMultibodyDynamicsAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2223.Shaft':
        '''Shaft: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2223.Shaft)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_5211.ShaftMultibodyDynamicsAnalysis]':
        '''List[ShaftMultibodyDynamicsAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_5211.ShaftMultibodyDynamicsAnalysis))
        return value

    @property
    def planetaries(self) -> 'List[ShaftCompoundMultibodyDynamicsAnalysis]':
        '''List[ShaftCompoundMultibodyDynamicsAnalysis]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(ShaftCompoundMultibodyDynamicsAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_5211.ShaftMultibodyDynamicsAnalysis]':
        '''List[ShaftMultibodyDynamicsAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_5211.ShaftMultibodyDynamicsAnalysis))
        return value
