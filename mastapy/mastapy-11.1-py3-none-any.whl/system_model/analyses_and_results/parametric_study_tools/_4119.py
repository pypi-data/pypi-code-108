'''_4119.py

ParametricStudyTool
'''


from mastapy.system_model.analyses_and_results.parametric_study_tools import _4120, _4118
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.static_loads import _6520, _6519, _6526
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.analysis_cases import _7252
from mastapy._internal.python_net import python_net_import

_PARAMETRIC_STUDY_TOOL = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools', 'ParametricStudyTool')


__docformat__ = 'restructuredtext en'
__all__ = ('ParametricStudyTool',)


class ParametricStudyTool(_7252.AnalysisCase):
    '''ParametricStudyTool

    This is a mastapy class.
    '''

    TYPE = _PARAMETRIC_STUDY_TOOL

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ParametricStudyTool.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def parametric_analysis_options(self) -> '_4120.ParametricStudyToolOptions':
        '''ParametricStudyToolOptions: 'ParametricAnalysisOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_4120.ParametricStudyToolOptions)(self.wrapped.ParametricAnalysisOptions) if self.wrapped.ParametricAnalysisOptions is not None else None

    @property
    def time_series_load_case(self) -> '_6520.TimeSeriesLoadCase':
        '''TimeSeriesLoadCase: 'TimeSeriesLoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_6520.TimeSeriesLoadCase)(self.wrapped.TimeSeriesLoadCase) if self.wrapped.TimeSeriesLoadCase is not None else None

    @property
    def load_case(self) -> '_6519.StaticLoadCase':
        '''StaticLoadCase: 'LoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6519.StaticLoadCase.TYPE not in self.wrapped.LoadCase.__class__.__mro__:
            raise CastException('Failed to cast load_case to StaticLoadCase. Expected: {}.'.format(self.wrapped.LoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LoadCase.__class__)(self.wrapped.LoadCase) if self.wrapped.LoadCase is not None else None
