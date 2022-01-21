'''_4214.py

CVTBeltConnectionCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4067
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4183
from mastapy._internal.python_net import python_net_import

_CVT_BELT_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'CVTBeltConnectionCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('CVTBeltConnectionCompoundParametricStudyTool',)


class CVTBeltConnectionCompoundParametricStudyTool(_4183.BeltConnectionCompoundParametricStudyTool):
    '''CVTBeltConnectionCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _CVT_BELT_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CVTBeltConnectionCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4067.CVTBeltConnectionParametricStudyTool]':
        '''List[CVTBeltConnectionParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4067.CVTBeltConnectionParametricStudyTool))
        return value

    @property
    def connection_analysis_cases(self) -> 'List[_4067.CVTBeltConnectionParametricStudyTool]':
        '''List[CVTBeltConnectionParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4067.CVTBeltConnectionParametricStudyTool))
        return value
