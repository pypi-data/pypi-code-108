'''_4212.py

CouplingConnectionCompoundParametricStudyTool
'''


from typing import List

from mastapy.system_model.analyses_and_results.parametric_study_tools import _4064
from mastapy._internal import constructor, conversion
from mastapy.system_model.analyses_and_results.parametric_study_tools.compound import _4239
from mastapy._internal.python_net import python_net_import

_COUPLING_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools.Compound', 'CouplingConnectionCompoundParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('CouplingConnectionCompoundParametricStudyTool',)


class CouplingConnectionCompoundParametricStudyTool(_4239.InterMountableComponentConnectionCompoundParametricStudyTool):
    '''CouplingConnectionCompoundParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _COUPLING_CONNECTION_COMPOUND_PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'CouplingConnectionCompoundParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def connection_analysis_cases(self) -> 'List[_4064.CouplingConnectionParametricStudyTool]':
        '''List[CouplingConnectionParametricStudyTool]: 'ConnectionAnalysisCases' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCases, constructor.new(_4064.CouplingConnectionParametricStudyTool))
        return value

    @property
    def connection_analysis_cases_ready(self) -> 'List[_4064.CouplingConnectionParametricStudyTool]':
        '''List[CouplingConnectionParametricStudyTool]: 'ConnectionAnalysisCasesReady' is the original name of this property.

        Note:
            This property is readonly.
        '''

        value = conversion.pn_to_mp_objects_in_list(self.wrapped.ConnectionAnalysisCasesReady, constructor.new(_4064.CouplingConnectionParametricStudyTool))
        return value
