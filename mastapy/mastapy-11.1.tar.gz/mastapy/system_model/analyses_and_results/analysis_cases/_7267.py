'''_7267.py

StaticLoadAnalysisCase
'''


from mastapy.system_model.analyses_and_results.static_loads import _6519, _6526
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4118
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.analysis_cases import _7252
from mastapy._internal.python_net import python_net_import

_STATIC_LOAD_ANALYSIS_CASE = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AnalysisCases', 'StaticLoadAnalysisCase')


__docformat__ = 'restructuredtext en'
__all__ = ('StaticLoadAnalysisCase',)


class StaticLoadAnalysisCase(_7252.AnalysisCase):
    '''StaticLoadAnalysisCase

    This is a mastapy class.
    '''

    TYPE = _STATIC_LOAD_ANALYSIS_CASE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'StaticLoadAnalysisCase.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_case(self) -> '_6519.StaticLoadCase':
        '''StaticLoadCase: 'LoadCase' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6519.StaticLoadCase.TYPE not in self.wrapped.LoadCase.__class__.__mro__:
            raise CastException('Failed to cast load_case to StaticLoadCase. Expected: {}.'.format(self.wrapped.LoadCase.__class__.__qualname__))

        return constructor.new_override(self.wrapped.LoadCase.__class__)(self.wrapped.LoadCase) if self.wrapped.LoadCase is not None else None
