'''_3750.py

TorqueConverterTurbineCompoundStabilityAnalysis
'''


from typing import List

from mastapy.system_model.part_model.couplings import _2350
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.stability_analyses import _3621
from mastapy.system_model.analyses_and_results.stability_analyses.compound import _3669
from mastapy._internal.python_net import python_net_import

_TORQUE_CONVERTER_TURBINE_COMPOUND_STABILITY_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses.Compound', 'TorqueConverterTurbineCompoundStabilityAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('TorqueConverterTurbineCompoundStabilityAnalysis',)


class TorqueConverterTurbineCompoundStabilityAnalysis(_3669.CouplingHalfCompoundStabilityAnalysis):
    '''TorqueConverterTurbineCompoundStabilityAnalysis

    This is a mastapy class.
    '''

    TYPE = _TORQUE_CONVERTER_TURBINE_COMPOUND_STABILITY_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorqueConverterTurbineCompoundStabilityAnalysis.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_3621.TorqueConverterTurbineStabilityAnalysis]':
        '''List[TorqueConverterTurbineStabilityAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_3621.TorqueConverterTurbineStabilityAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_3621.TorqueConverterTurbineStabilityAnalysis]':
        '''List[TorqueConverterTurbineStabilityAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_3621.TorqueConverterTurbineStabilityAnalysis))
        return value
