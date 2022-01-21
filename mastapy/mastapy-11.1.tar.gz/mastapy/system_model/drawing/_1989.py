'''_1989.py

DynamicAnalysisViewable
'''


from mastapy.system_model.drawing import _1987, _1994
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.system_deflections import _2561
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.steady_state_synchronous_responses import _3343
from mastapy.system_model.analyses_and_results.stability_analyses import _3604
from mastapy.system_model.analyses_and_results.rotor_dynamics import _3759
from mastapy.system_model.analyses_and_results.modal_analyses import _4900
from mastapy.system_model.analyses_and_results.mbd_analyses import _5186
from mastapy.system_model.analyses_and_results.harmonic_analyses import _5743
from mastapy.system_model.analyses_and_results.dynamic_analyses import _6045
from mastapy.system_model.analyses_and_results.critical_speed_analyses import _6298
from mastapy._internal.python_net import python_net_import

_DYNAMIC_ANALYSIS_VIEWABLE = python_net_import('SMT.MastaAPI.SystemModel.Drawing', 'DynamicAnalysisViewable')


__docformat__ = 'restructuredtext en'
__all__ = ('DynamicAnalysisViewable',)


class DynamicAnalysisViewable(_1994.PartAnalysisCaseWithContourViewable):
    '''DynamicAnalysisViewable

    This is a mastapy class.
    '''

    TYPE = _DYNAMIC_ANALYSIS_VIEWABLE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'DynamicAnalysisViewable.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def contour_draw_style(self) -> '_1987.ContourDrawStyle':
        '''ContourDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _1987.ContourDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to ContourDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_system_deflection_draw_style(self) -> '_2561.SystemDeflectionDrawStyle':
        '''SystemDeflectionDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _2561.SystemDeflectionDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to SystemDeflectionDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_steady_state_synchronous_response_draw_style(self) -> '_3343.SteadyStateSynchronousResponseDrawStyle':
        '''SteadyStateSynchronousResponseDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3343.SteadyStateSynchronousResponseDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to SteadyStateSynchronousResponseDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_stability_analysis_draw_style(self) -> '_3604.StabilityAnalysisDrawStyle':
        '''StabilityAnalysisDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3604.StabilityAnalysisDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to StabilityAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_rotor_dynamics_draw_style(self) -> '_3759.RotorDynamicsDrawStyle':
        '''RotorDynamicsDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _3759.RotorDynamicsDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to RotorDynamicsDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_modal_analysis_draw_style(self) -> '_4900.ModalAnalysisDrawStyle':
        '''ModalAnalysisDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _4900.ModalAnalysisDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to ModalAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_mbd_analysis_draw_style(self) -> '_5186.MBDAnalysisDrawStyle':
        '''MBDAnalysisDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5186.MBDAnalysisDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to MBDAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_harmonic_analysis_draw_style(self) -> '_5743.HarmonicAnalysisDrawStyle':
        '''HarmonicAnalysisDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _5743.HarmonicAnalysisDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to HarmonicAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_dynamic_analysis_draw_style(self) -> '_6045.DynamicAnalysisDrawStyle':
        '''DynamicAnalysisDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6045.DynamicAnalysisDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to DynamicAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

    @property
    def contour_draw_style_of_type_critical_speed_analysis_draw_style(self) -> '_6298.CriticalSpeedAnalysisDrawStyle':
        '''CriticalSpeedAnalysisDrawStyle: 'ContourDrawStyle' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6298.CriticalSpeedAnalysisDrawStyle.TYPE not in self.wrapped.ContourDrawStyle.__class__.__mro__:
            raise CastException('Failed to cast contour_draw_style to CriticalSpeedAnalysisDrawStyle. Expected: {}.'.format(self.wrapped.ContourDrawStyle.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ContourDrawStyle.__class__)(self.wrapped.ContourDrawStyle) if self.wrapped.ContourDrawStyle is not None else None

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

    def fe_results(self):
        ''' 'FEResults' is the original name of this method.'''

        self.wrapped.FEResults()
