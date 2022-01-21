'''_4121.py

ParametricStudyToolResultsForReporting
'''


from mastapy import _0
from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_TOOL_RESULTS_FOR_REPORTING = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ParametricStudyToolResultsForReporting')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyToolResultsForReporting',)


class ParametricStudyToolResultsForReporting(_0.APIBase):
    '''ParametricStudyToolResultsForReporting

    This is a mastapy class.
    '''

    TYPE = _PARAMETRIC_STUDY_TOOL_RESULTS_FOR_REPORTING

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParametricStudyToolResultsForReporting.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
