'''_4260.py

PointLoadCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.part_model import _2212
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4131
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4296
from mastapy._internal.python_net import python_net_import

_POINT_LOAD_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'PointLoadCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('PointLoadCompoundParametricStudyTool',)


class PointLoadCompoundParametricStudyTool(_4296.VirtualComponentCompoundParametricStudyTool):
    '''PointLoadCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _POINT_LOAD_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'PointLoadCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def component_design(self) -> '_2212.PointLoad':
        '''PointLoad: 'ComponentDesign' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2212.PointLoad)(self.wrapped.ComponentDesign) if self.wrapped.ComponentDesign is not None else None

    @property
    def component_analysis_cases_ready(self) -> 'List[_4131.PointLoadParametricStudyTool]':
        '''List[PointLoadParametricStudyTool]: 'ComponentAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCasesReady, constructor.new(_4131.PointLoadParametricStudyTool))
        return value

    @property
    def component_analysis_cases(self) -> 'List[_4131.PointLoadParametricStudyTool]':
        '''List[PointLoadParametricStudyTool]: 'ComponentAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ComponentAnalysisCases, constructor.new(_4131.PointLoadParametricStudyTool))
        return value
