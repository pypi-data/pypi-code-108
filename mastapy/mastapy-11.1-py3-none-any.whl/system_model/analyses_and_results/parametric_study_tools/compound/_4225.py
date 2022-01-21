'''_4225.py

DatumCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2190
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4078
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4199
from mastapy._internal.python_net import python_net_import

_DATUM_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'DatumCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('DatumCompoundParametricStudyTool',)


class DatumCompoundParametricStudyTool(_4199.ComponentCompoundParametricStudyTool):
    '''DatumCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _DATUM_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DatumCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2190.Datum':
        '''Datum: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2190.Datum)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4078.DatumParametricStudyTool]':
        '''List[DatumParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4078.DatumParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4078.DatumParametricStudyTool]':
        '''List[DatumParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4078.DatumParametricStudyTool))
        return value
