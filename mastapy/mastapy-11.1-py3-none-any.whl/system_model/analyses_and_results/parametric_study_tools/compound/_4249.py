'''_4249.py

MassDiscCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2203
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4109
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4296
from mastapy._internal.python_net import python_net_import

_MASS_DISC_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'MassDiscCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('MassDiscCompoundParametricStudyTool',)


class MassDiscCompoundParametricStudyTool(_4296.VirtualComponentCompoundParametricStudyTool):
    '''MassDiscCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _MASS_DISC_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'MassDiscCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2203.MassDisc':
        '''MassDisc: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2203.MassDisc)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4109.MassDiscParametricStudyTool]':
        '''List[MassDiscParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4109.MassDiscParametricStudyTool))
        return value

    @property
    def planetaries(self) -> 'List[MassDiscCompoundParametricStudyTool]':
        '''List[MassDiscCompoundParametricStudyTool]: 'Planetaries' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.Planetaries, constructor.new(MassDiscCompoundParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4109.MassDiscParametricStudyTool]':
        '''List[MassDiscParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4109.MassDiscParametricStudyTool))
        return value
