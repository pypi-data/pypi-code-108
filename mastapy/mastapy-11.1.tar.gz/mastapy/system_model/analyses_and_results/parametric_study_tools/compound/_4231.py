'''_4231.py

FlexiblePinAssemblyCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2195
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4091
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4272
from mastapy._internal.python_net import python_net_import

_FLEXIBLE_PIN_ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'FlexiblePinAssemblyCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexiblePinAssemblyCompoundParametricStudyTool',)


class FlexiblePinAssemblyCompoundParametricStudyTool(_4272.SpecialisedAssemblyCompoundParametricStudyTool):
    '''FlexiblePinAssemblyCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_PIN_ASSEMBLY_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexiblePinAssemblyCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2195.FlexiblePinAssembly':
        '''FlexiblePinAssembly: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2195.FlexiblePinAssembly)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def assembly_design(self) -> '_2195.FlexiblePinAssembly':
        '''FlexiblePinAssembly: 'AssemblyDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2195.FlexiblePinAssembly)(self.wrapped.AssemblyDesign) if self.wrapped.AssemblyDesign is not None else None

    @property
    def assembly_analysis_cases_ready(self) -> 'List[_4091.FlexiblePinAssemblyParametricStudyTool]':
        '''List[FlexiblePinAssemblyParametricStudyTool]: 'AssemblyAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCasesReady, constructor.new(_4091.FlexiblePinAssemblyParametricStudyTool))
        return value

    @property
    def assembly_analysis_cases(self) -> 'List[_4091.FlexiblePinAssemblyParametricStudyTool]':
        '''List[FlexiblePinAssemblyParametricStudyTool]: 'AssemblyAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.AssemblyAnalysisCases, constructor.new(_4091.FlexiblePinAssemblyParametricStudyTool))
        return value
