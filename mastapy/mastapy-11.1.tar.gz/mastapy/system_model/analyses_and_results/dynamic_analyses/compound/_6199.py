'''_6199.py

MeasurementComponentCompoundDynamicAnalysis
'''


from typing import List

from mastapy.system_model.part_model import _2204
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6070
from mastapy.system_model.analyses_and_results.dynamic_analyses.compound import _6245
from mastapy._internal.python_net import python_net_import

_MEASUREMENT_COMPONENT_COMPOUND_DYNAMIC_ANALYSIS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses.Compound', 'MeasurementComponentCompoundDynamicAnalysis')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementComponentCompoundDynamicAnalysis',)


class MeasurementComponentCompoundDynamicAnalysis(_6245.VirtualComponentCompoundDynamicAnalysis):
    '''MeasurementComponentCompoundDynamicAnalysis

    This is a mastapy class.
    '''

    TYPE = _MEASUREMENT_COMPONENT_COMPOUND_DYNAMIC_ANALYSIS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeasurementComponentCompoundDynamicAnalysis.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2204.MeasurementComponent':
        '''MeasurementComponent: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2204.MeasurementComponent)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_6070.MeasurementComponentDynamicAnalysis]':
        '''List[MeasurementComponentDynamicAnalysis]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_6070.MeasurementComponentDynamicAnalysis))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_6070.MeasurementComponentDynamicAnalysis]':
        '''List[MeasurementComponentDynamicAnalysis]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_6070.MeasurementComponentDynamicAnalysis))
        return value
