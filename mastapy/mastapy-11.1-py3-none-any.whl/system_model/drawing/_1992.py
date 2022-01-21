'''_1992.py

ModalAnalysisViewable
'''


from mastapy.system_model.analyses_and_results.dynamic_analyses import _6045
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.modal_analyses import _4900
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5743
from mastapy.system_model.drawing import _1989
from mastapy._internal.python_net import python_net_import

_MODAL_ANALYSIS_VIEWABLE = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'ModalAnalysisViewable')


__docformat__ = 'restructuredtext en'
__all__ = ('ModalAnalysisViewable',)


class ModalAnalysisViewable(_1989.DynamicAnalysisViewable):
    '''ModalAnalysisViewable

    This is a mastapy class.
    '''

    TYPE = _MODAL_ANALYSIS_VIEWABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'ModalAnalysisViewable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def dynamic_analysis_draw_style(self) -> '_6045.DynamicAnalysisDrawStyle':
        '''DynamicAnalysisDrawStyle: 'DynamicAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6045.DynamicAnalysisDrawStyle.TYPE not in self.wrapped.DynamicAnalysisDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast dynamic_analysis_draw_style to DynamicAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.DynamicAnalysisDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.DynamicAnalysisDrawStyle.__class__)(self.wrapped.DynamicAnalysisDrawStyle) if self.wrapped.DynamicAnalysisDrawStyle is not None else None

    @property
    def dynamic_analysis_draw_style_of_type_modal_analysis_draw_style(self) -> '_4900.ModalAnalysisDrawStyle':
        '''ModalAnalysisDrawStyle: 'DynamicAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4900.ModalAnalysisDrawStyle.TYPE not in self.wrapped.DynamicAnalysisDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast dynamic_analysis_draw_style to ModalAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.DynamicAnalysisDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.DynamicAnalysisDrawStyle.__class__)(self.wrapped.DynamicAnalysisDrawStyle) if self.wrapped.DynamicAnalysisDrawStyle is not None else None

    @property
    def dynamic_analysis_draw_style_of_type_harmonic_analysis_draw_style(self) -> '_5743.HarmonicAnalysisDrawStyle':
        '''HarmonicAnalysisDrawStyle: 'DynamicAnalysisDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5743.HarmonicAnalysisDrawStyle.TYPE not in self.wrapped.DynamicAnalysisDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast dynamic_analysis_draw_style to HarmonicAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.DynamicAnalysisDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.DynamicAnalysisDrawStyle.__class__)(self.wrapped.DynamicAnalysisDrawStyle) if self.wrapped.DynamicAnalysisDrawStyle is not None else None
