'''_5990.py

FlexiblePinAnalysisOptions
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.analyses_and_results.static_loads import _6519, _6526
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor
from mastapy.system_model.analyses_and_results.parametric_study_tools import _4118
from mastapy._internal.cast_exception import CastException
from mastapy.system_model.analyses_and_results.load_case_groups import _5389
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_FLEXIBLE_PIN_ANALYSIS_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.FlexiblePinAnalyses', 'FlexiblePinAnalysisOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('FlexiblePinAnalysisOptions',)


class FlexiblePinAnalysisOptions(_0.APIBase):
    '''FlexiblePinAnalysisOptions

    This is a mastapy class.
    '''

    TYPE = _FLEXIBLE_PIN_ANALYSIS_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'FlexiblePinAnalysisOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def extreme_load_case(self) -> 'list_with_selected_item.ListWithSelectedItem_StaticLoadCase':
        '''list_with_selected_item.ListWithSelectedItem_StaticLoadCase: 'ExtremeLoadCase' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_StaticLoadCase)(self.wrapped.ExtremeLoadCase) if self.wrapped.ExtremeLoadCase is not None else None

    @extreme_load_case.setter
    def extreme_load_case(self, value: 'list_with_selected_item.ListWithSelectedItem_StaticLoadCase.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_StaticLoadCase.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_StaticLoadCase.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.ExtremeLoadCase = value

    @property
    def extreme_load_case_for_stop_start(self) -> '_6519.StaticLoadCase':
        '''StaticLoadCase: 'ExtremeLoadCaseForStopStart' is the original name of this property.'''

        if _6519.StaticLoadCase.TYPE not in self.wrapped.ExtremeLoadCaseForStopStart.__class__.__mro__:
            raise CastException('Failed to cast extreme_load_case_for_stop_start to StaticLoadCase. Expected: {}.'.format(self.wrapped.ExtremeLoadCaseForStopStart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.ExtremeLoadCaseForStopStart.__class__)(self.wrapped.ExtremeLoadCaseForStopStart) if self.wrapped.ExtremeLoadCaseForStopStart is not None else None

    @extreme_load_case_for_stop_start.setter
    def extreme_load_case_for_stop_start(self, value: '_6519.StaticLoadCase'):
        value = value.wrapped if value else None
        self.wrapped.ExtremeLoadCaseForStopStart = value

    @property
    def ldd(self) -> 'list_with_selected_item.ListWithSelectedItem_DutyCycle':
        '''list_with_selected_item.ListWithSelectedItem_DutyCycle: 'LDD' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_DutyCycle)(self.wrapped.LDD) if self.wrapped.LDD is not None else None

    @ldd.setter
    def ldd(self, value: 'list_with_selected_item.ListWithSelectedItem_DutyCycle.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_DutyCycle.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_DutyCycle.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.LDD = value

    @property
    def nominal_load_case(self) -> 'list_with_selected_item.ListWithSelectedItem_StaticLoadCase':
        '''list_with_selected_item.ListWithSelectedItem_StaticLoadCase: 'NominalLoadCase' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_StaticLoadCase)(self.wrapped.NominalLoadCase) if self.wrapped.NominalLoadCase is not None else None

    @nominal_load_case.setter
    def nominal_load_case(self, value: 'list_with_selected_item.ListWithSelectedItem_StaticLoadCase.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_StaticLoadCase.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_StaticLoadCase.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.NominalLoadCase = value

    @property
    def nominal_load_case_for_stop_start(self) -> '_6519.StaticLoadCase':
        '''StaticLoadCase: 'NominalLoadCaseForStopStart' is the original name of this property.'''

        if _6519.StaticLoadCase.TYPE not in self.wrapped.NominalLoadCaseForStopStart.__class__.__mro__:
            raise CastException('Failed to cast nominal_load_case_for_stop_start to StaticLoadCase. Expected: {}.'.format(self.wrapped.NominalLoadCaseForStopStart.__class__.__qualname__))

        return constructor.new_override(self.wrapped.NominalLoadCaseForStopStart.__class__)(self.wrapped.NominalLoadCaseForStopStart) if self.wrapped.NominalLoadCaseForStopStart is not None else None

    @nominal_load_case_for_stop_start.setter
    def nominal_load_case_for_stop_start(self, value: '_6519.StaticLoadCase'):
        value = value.wrapped if value else None
        self.wrapped.NominalLoadCaseForStopStart = value

    @property
    def include_flexible_bearing_races(self) -> 'bool':
        '''bool: 'IncludeFlexibleBearingRaces' is the original name of this property.'''

        return self.wrapped.IncludeFlexibleBearingRaces

    @include_flexible_bearing_races.setter
    def include_flexible_bearing_races(self, value: 'bool'):
        self.wrapped.IncludeFlexibleBearingRaces = bool(value) if value else False
