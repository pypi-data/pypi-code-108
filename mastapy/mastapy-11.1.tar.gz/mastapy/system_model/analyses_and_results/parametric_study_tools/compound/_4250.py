'''_4250.py

MeasurementComponentCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2204
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4110
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4296
from mastapy._internal.python_net import python_net_import

_MEASUREMENT_COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'MeasurementComponentCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('MeasurementComponentCompoundParametricStudyTool',)


class MeasurementComponentCompoundParametricStudyTool(_4296.VirtualComponentCompoundParametricStudyTool):
    '''MeasurementComponentCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _MEASUREMENT_COMPONENT_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MeasurementComponentCompoundParametricStudyTool.TYPE'):
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
    def component_analysis_cases_ready(self) -> 'List[_4110.MeasurementComponentParametricStudyTool]':
        '''List[MeasurementComponentParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4110.MeasurementComponentParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4110.MeasurementComponentParametricStudyTool]':
        '''List[MeasurementComponentParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4110.MeasurementComponentParametricStudyTool))
        return value
