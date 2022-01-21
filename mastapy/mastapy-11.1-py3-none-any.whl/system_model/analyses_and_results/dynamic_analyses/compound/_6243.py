'''_6243.py

TorqueConverterTurbineCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2350
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6114
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6162
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_TURBINE_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'TorqueConverterTurbineCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterTurbineCompoundDynamicAnalysis',)


class TorqueConverterTurbineCompoundDynamicAnalysis(_6162.CouplingHalfCompoundDynamicAnalysis):
    '''TorqueConverterTurbineCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_TURBINE_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterTurbineCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2350.TorqueConverterTurbine':
        '''TorqueConverterTurbine: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2350.TorqueConverterTurbine)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6114.TorqueConverterTurbineDynamicAnalysis]':
        '''List[TorqueConverterTurbineDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6114.TorqueConverterTurbineDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6114.TorqueConverterTurbineDynamicAnalysis]':
        '''List[TorqueConverterTurbineDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6114.TorqueConverterTurbineDynamicAnalysis))
        return value
