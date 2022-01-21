'''_6730.py

AdvancedTimeSteppingAnalysisForModulationOptions
'''


from mastapy._internal.implicit import list_with_selected_item
from mastapy.system_model.analyses_and_results.static_loads import (
    _6519, _6527, _6610, _6530,
    _6539, _6544, _6557, _6562,
    _6579, _6601, _6624, _6631,
    _6634, _6637, _6651, _6674,
    _6680, _6683, _6703, _6706
)
from mastapy._internal.overridable_constructor import _unpack_overridable
from mastapy._internal import constructor, enum_with_selected_value_runtime, conversion
from mastapy.system_model.analyses_and_results import _2424
from mastapy._internal.cast_exception import CastException
from mastapy import _0
from mastapy._internal.python_net import python_net_import

_ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_OPTIONS = python_net_import('SMT.MastaAPI.SystemModel.AnalysesAndResults.AdvancedTimeSteppingAnalysesForModulation', 'AdvancedTimeSteppingAnalysisForModulationOptions')


__docformat__ = 'restructuredtext en'
__all__ = ('AdvancedTimeSteppingAnalysisForModulationOptions',)


class AdvancedTimeSteppingAnalysisForModulationOptions(_0.APIBase):
    '''AdvancedTimeSteppingAnalysisForModulationOptions

    This is a mastapy class.
    '''

    TYPE = _ADVANCED_TIME_STEPPING_ANALYSIS_FOR_MODULATION_OPTIONS

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AdvancedTimeSteppingAnalysisForModulationOptions.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()

    @property
    def load_case_for_advanced_time_stepping_analysis_for_modulation_time_options(self) -> 'list_with_selected_item.ListWithSelectedItem_StaticLoadCase':
        '''list_with_selected_item.ListWithSelectedItem_StaticLoadCase: 'LoadCaseForAdvancedTimeSteppingAnalysisForModulationTimeOptions' is the original name of this property.'''

        return constructor.new(list_with_selected_item.ListWithSelectedItem_StaticLoadCase)(self.wrapped.LoadCaseForAdvancedTimeSteppingAnalysisForModulationTimeOptions) if self.wrapped.LoadCaseForAdvancedTimeSteppingAnalysisForModulationTimeOptions is not None else None

    @load_case_for_advanced_time_stepping_analysis_for_modulation_time_options.setter
    def load_case_for_advanced_time_stepping_analysis_for_modulation_time_options(self, value: 'list_with_selected_item.ListWithSelectedItem_StaticLoadCase.implicit_type()'):
        wrapper_type = list_with_selected_item.ListWithSelectedItem_StaticLoadCase.wrapper_type()
        enclosed_type = list_with_selected_item.ListWithSelectedItem_StaticLoadCase.implicit_type()
        value = wrapper_type[enclosed_type](value.wrapped if value is not None else None)
        self.wrapped.LoadCaseForAdvancedTimeSteppingAnalysisForModulationTimeOptions = value

    @property
    def include_time_offset_for_steady_state(self) -> 'bool':
        '''bool: 'IncludeTimeOffsetForSteadyState' is the original name of this property.'''

        return self.wrapped.IncludeTimeOffsetForSteadyState

    @include_time_offset_for_steady_state.setter
    def include_time_offset_for_steady_state(self, value: 'bool'):
        self.wrapped.IncludeTimeOffsetForSteadyState = bool(value) if value else False

    @property
    def advanced_time_stepping_analysis_method(self) -> '_6527.AdvancedTimeSteppingAnalysisForModulationType':
        '''AdvancedTimeSteppingAnalysisForModulationType: 'AdvancedTimeSteppingAnalysisMethod' is the original name of this property.'''

        value = conversion.pn_to_mp_enum(self.wrapped.AdvancedTimeSteppingAnalysisMethod)
        return constructor.new(_6527.AdvancedTimeSteppingAnalysisForModulationType)(value) if value is not None else None

    @advanced_time_stepping_analysis_method.setter
    def advanced_time_stepping_analysis_method(self, value: '_6527.AdvancedTimeSteppingAnalysisForModulationType'):
        value = value if value else None
        value = conversion.mp_to_pn_enum(value)
        self.wrapped.AdvancedTimeSteppingAnalysisMethod = value

    @property
    def number_of_steps_for_advanced_time_stepping_analysis(self) -> 'int':
        '''int: 'NumberOfStepsForAdvancedTimeSteppingAnalysis' is the original name of this property.'''

        return self.wrapped.NumberOfStepsForAdvancedTimeSteppingAnalysis

    @number_of_steps_for_advanced_time_stepping_analysis.setter
    def number_of_steps_for_advanced_time_stepping_analysis(self, value: 'int'):
        self.wrapped.NumberOfStepsForAdvancedTimeSteppingAnalysis = int(value) if value else 0

    @property
    def number_of_times_per_quasi_step(self) -> 'int':
        '''int: 'NumberOfTimesPerQuasiStep' is the original name of this property.'''

        return self.wrapped.NumberOfTimesPerQuasiStep

    @number_of_times_per_quasi_step.setter
    def number_of_times_per_quasi_step(self, value: 'int'):
        self.wrapped.NumberOfTimesPerQuasiStep = int(value) if value else 0

    @property
    def number_of_periods_for_advanced_time_stepping_analysis(self) -> 'float':
        '''float: 'NumberOfPeriodsForAdvancedTimeSteppingAnalysis' is the original name of this property.'''

        return self.wrapped.NumberOfPeriodsForAdvancedTimeSteppingAnalysis

    @number_of_periods_for_advanced_time_stepping_analysis.setter
    def number_of_periods_for_advanced_time_stepping_analysis(self, value: 'float'):
        self.wrapped.NumberOfPeriodsForAdvancedTimeSteppingAnalysis = float(value) if value else 0.0

    @property
    def time_options(self) -> '_2424.TimeOptions':
        '''TimeOptions: 'TimeOptions' is the original name of this property.

        Note:
            This property is readonly.
        '''

        return constructor.new(_2424.TimeOptions)(self.wrapped.TimeOptions) if self.wrapped.TimeOptions is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation(self) -> '_6610.GearSetLoadCase':
        '''GearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6610.GearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to GearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_agma_gleason_conical_gear_set_load_case(self) -> '_6530.AGMAGleasonConicalGearSetLoadCase':
        '''AGMAGleasonConicalGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6530.AGMAGleasonConicalGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to AGMAGleasonConicalGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_bevel_differential_gear_set_load_case(self) -> '_6539.BevelDifferentialGearSetLoadCase':
        '''BevelDifferentialGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6539.BevelDifferentialGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to BevelDifferentialGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_bevel_gear_set_load_case(self) -> '_6544.BevelGearSetLoadCase':
        '''BevelGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6544.BevelGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to BevelGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_concept_gear_set_load_case(self) -> '_6557.ConceptGearSetLoadCase':
        '''ConceptGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6557.ConceptGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to ConceptGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_conical_gear_set_load_case(self) -> '_6562.ConicalGearSetLoadCase':
        '''ConicalGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6562.ConicalGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to ConicalGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_cylindrical_gear_set_load_case(self) -> '_6579.CylindricalGearSetLoadCase':
        '''CylindricalGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6579.CylindricalGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to CylindricalGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_face_gear_set_load_case(self) -> '_6601.FaceGearSetLoadCase':
        '''FaceGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6601.FaceGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to FaceGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_hypoid_gear_set_load_case(self) -> '_6624.HypoidGearSetLoadCase':
        '''HypoidGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6624.HypoidGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to HypoidGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_klingelnberg_cyclo_palloid_conical_gear_set_load_case(self) -> '_6631.KlingelnbergCycloPalloidConicalGearSetLoadCase':
        '''KlingelnbergCycloPalloidConicalGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6631.KlingelnbergCycloPalloidConicalGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to KlingelnbergCycloPalloidConicalGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_klingelnberg_cyclo_palloid_hypoid_gear_set_load_case(self) -> '_6634.KlingelnbergCycloPalloidHypoidGearSetLoadCase':
        '''KlingelnbergCycloPalloidHypoidGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6634.KlingelnbergCycloPalloidHypoidGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to KlingelnbergCycloPalloidHypoidGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_klingelnberg_cyclo_palloid_spiral_bevel_gear_set_load_case(self) -> '_6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase':
        '''KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6637.KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to KlingelnbergCycloPalloidSpiralBevelGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_planetary_gear_set_load_case(self) -> '_6651.PlanetaryGearSetLoadCase':
        '''PlanetaryGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6651.PlanetaryGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to PlanetaryGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_spiral_bevel_gear_set_load_case(self) -> '_6674.SpiralBevelGearSetLoadCase':
        '''SpiralBevelGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6674.SpiralBevelGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to SpiralBevelGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_straight_bevel_diff_gear_set_load_case(self) -> '_6680.StraightBevelDiffGearSetLoadCase':
        '''StraightBevelDiffGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6680.StraightBevelDiffGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to StraightBevelDiffGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_straight_bevel_gear_set_load_case(self) -> '_6683.StraightBevelGearSetLoadCase':
        '''StraightBevelGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6683.StraightBevelGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to StraightBevelGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_worm_gear_set_load_case(self) -> '_6703.WormGearSetLoadCase':
        '''WormGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6703.WormGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to WormGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None

    @property
    def gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation_of_type_zerol_bevel_gear_set_load_case(self) -> '_6706.ZerolBevelGearSetLoadCase':
        '''ZerolBevelGearSetLoadCase: 'GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation' is the original name of this property.

        Note:
            This property is readonly.
        '''

        if _6706.ZerolBevelGearSetLoadCase.TYPE not in self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__mro__:
            raise CastException('Failed to cast gear_set_load_case_within_load_case_for_advanced_time_stepping_analysis_for_modulation to ZerolBevelGearSetLoadCase. Expected: {}.'.format(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__.__qualname__))

        return constructor.new_override(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation.__class__)(self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation) if self.wrapped.GearSetLoadCaseWithinLoadCaseForAdvancedTimeSteppingAnalysisForModulation is not None else None
